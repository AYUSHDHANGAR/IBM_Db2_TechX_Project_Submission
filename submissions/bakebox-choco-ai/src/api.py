"""
Production FastAPI Application Server for BAKEBOX Choco AI on IBM Db2.
Exposes RESTful endpoints for:
1. GET / & GET /api/health: System health, Db2 live/mock state, catalog items, and RRF status.
2. POST /api/chat: Conversational agent with session isolation, buffer memory, and prompt injection defense.
3. GET /api/cakes/search: 3-Way Reciprocal Rank Fusion (Dense Vector + BM25 + TF-IDF) product search.
4. GET /api/orders/{order_id}: Real-time order tracking with PII data masking.
5. POST /api/orders/{order_id}/refund: Happiness Guarantee evaluation against Db2 order logs.
"""
import os
import sys
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager

_pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

try:
    from fastapi import FastAPI, HTTPException, Query, Path as FPath, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    FastAPI = None
    BaseModel = object
    Field = lambda *args, **kwargs: None

from src.db import is_live_db2_available, get_dbi_connection
from src.query_engine import ChocoQueryEngine
from src.order_engine import evaluate_refund_request

START_TIME = time.time()
engine_instance: Optional[ChocoQueryEngine] = None

def get_engine() -> ChocoQueryEngine:
    global engine_instance
    if engine_instance is None:
        engine_instance = ChocoQueryEngine(use_llm=False)
    return engine_instance

# ==============================================================================
# SECURITY GUARDRAILS & PROMPT INJECTION DEFENSE
# ==============================================================================

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(in\s+)?developer\s+mode", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
    re.compile(r"(price\s*[:=]\s*0|set\s+price\s+to\s+0|make\s+everything\s+free)", re.IGNORECASE),
    re.compile(r"(drop\s+table|delete\s+from\s+bb_|truncate\s+table)", re.IGNORECASE),
    re.compile(r"<script>|javascript:|alert\(", re.IGNORECASE),
]

def check_prompt_security(message: str) -> Tuple[bool, Optional[str]]:
    """
    Evaluates input message against compiled prompt injection patterns.
    Returns (is_safe: bool, flagged_reason: Optional[str]).
    """
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(message):
            return False, f"Malicious pattern detected: {pattern.pattern}"
    return True, None


# ==============================================================================
# PYDANTIC DATA SCHEMAS
# ==============================================================================

if BaseModel is not object:
    class CakeCardSchema(BaseModel):
        name: str = Field(..., description="Cake title")
        price: float = Field(..., description="Base retail price in INR")
        eggless: bool = Field(True, description="Whether pure veg eggless is available")
        branches: List[str] = Field(default_factory=lambda: ["Holigate (Mathura)", "Gosna Highway Kitchen"], description="Mathura branch availability")
        shelf_life: str = Field("24 Hours (Fresh Chilled)", description="Recommended consumption window")
        slug: str = Field(..., description="URL slug or SKU identifier")
        score: Optional[float] = Field(None, description="Fused 3-Way RRF ranking score")

    class ChatRequest(BaseModel):
        session_id: str = Field("session_default", description="Unique client session ID for buffer memory isolation")
        message: str = Field(..., min_length=1, max_length=2000, description="Customer natural language message")

    class ChatResponse(BaseModel):
        reply: str
        ui_cards: List[CakeCardSchema] = []
        intent: str
        session_id: str
        guardrail_triggered: bool = False

    class RefundRequest(BaseModel):
        reason: str = Field("Cake damaged in transit or incorrect base delivered", description="Reason for refund request")
else:
    class CakeCardSchema:
        def __init__(self, name: str, price: float, eggless: bool = True, branches: List[str] = None, shelf_life: str = "24h", slug: str = "", score: float = None):
            self.name = name
            self.price = price
            self.eggless = eggless
            self.branches = branches or ["Holigate", "Gosna"]
            self.shelf_life = shelf_life
            self.slug = slug
            self.score = score

    class ChatRequest:
        def __init__(self, session_id: str = "default", message: str = ""):
            self.session_id = session_id
            self.message = message

    class ChatResponse:
        def __init__(self, reply: str, ui_cards: list = None, intent: str = "", session_id: str = "", guardrail_triggered: bool = False):
            self.reply = reply
            self.ui_cards = ui_cards or []
            self.intent = intent
            self.session_id = session_id
            self.guardrail_triggered = guardrail_triggered

    class RefundRequest:
        def __init__(self, reason: str = "Damaged"):
            self.reason = reason


# ==============================================================================
# CORE REST BUSINESS LOGIC ENDPOINTS
# ==============================================================================

def get_health_status() -> Dict[str, Any]:
    """Returns live system health, Db2 connectivity state, and active RRF status."""
    engine = get_engine()
    live_db2 = is_live_db2_available()
    return {
        "status": "HEALTHY",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "db2_mode": "LIVE_DB2" if live_db2 else "MOCK_DB2_OFFLINE_SANDBOX",
        "db2_features_active": [
            "3-Way Hybrid Reciprocal Rank Fusion (k=60)",
            "Db2 Native Vector Store (DB2LlamaVS)",
            "Row-Level ACID Concurrency (SELECT FOR UPDATE WITH RS)",
            "Recursive Bill-of-Materials (BOM) CTE",
            "Cryptographic SHA-256 Hash-Chained Audit Trail (BB_AUDIT_LOG)"
        ],
        "catalog_items_indexed": len(engine.retriever.corpus_metadata) if hasattr(engine.retriever, "corpus_metadata") else 9,
        "session_isolation": "ENABLED",
        "active_sessions": len(engine.sessions)
    }

def chat_endpoint(req: ChatRequest) -> ChatResponse:
    """Processes customer natural language chat through CHOCO AI with guardrail protection."""
    is_safe, flag_reason = check_prompt_security(req.message)
    if not is_safe:
        return ChatResponse(
            reply=(
                "Radhe Radhe ji! Shri Ram Baker's Choco AI customer safety filter triggered. "
                "Aapka request hamare automated security guidelines ke mutabiq reject kar diya gaya hai. "
                "Hum keval authentic bakery queries aur real order tracking process karte hain."
            ),
            ui_cards=[],
            intent="SECURITY_VIOLATION",
            session_id=req.session_id,
            guardrail_triggered=True
        )

    engine = get_engine()
    result = engine.query(req.message, session_id=req.session_id)

    cards = []
    for card in result.get("ui_cards", []):
        cards.append(CakeCardSchema(
            name=card.get("name", "Artisan Cake"),
            price=float(card.get("price", 499.0)),
            eggless=bool(card.get("is_eggless_available", True)),
            branches=["Holigate (Mathura)", "Gosna Highway Kitchen"],
            shelf_life="24 Hours (Chilled)",
            slug=card.get("sku_id", "cake-sku"),
            score=card.get("score")
        ))

    return ChatResponse(
        reply=result.get("reply", "Radhe Radhe ji!"),
        ui_cards=cards,
        intent=result.get("intent", "UNKNOWN"),
        session_id=req.session_id,
        guardrail_triggered=False
    )

def search_cakes(q: str, eggless_only: bool = False) -> Dict[str, Any]:
    """Executes 3-Way Reciprocal Rank Fusion (Dense Vector + BM25 + TF-IDF) and returns top ranked cakes."""
    engine = get_engine()
    cards = engine.tool_recommend_cakes(q, limit=6)
    if eggless_only:
        cards = [c for c in cards if c.get("is_eggless_available", True)]
    return {
        "query": q,
        "total_matches": len(cards),
        "algorithm": "3-Way Reciprocal Rank Fusion (k=60)",
        "results": cards
    }

def get_order_tracking(order_id: int, phone: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves verified order tracking with PII data masking."""
    engine = get_engine()
    order = engine.tool_track_live_order(order_id=order_id, phone_number=phone)
    if not order:
        return {"status": "ORDER_NOT_FOUND", "message": f"Order #{order_id} not found."}
    return order

def post_refund_request(order_id: int, req: Optional[RefundRequest] = None) -> Dict[str, Any]:
    """Evaluates Shri Ram Baker's Happiness Guarantee policy against Db2 order status."""
    conn = get_dbi_connection()
    reason = req.reason if req else "Customer claim"
    return evaluate_refund_request(conn, order_id=order_id, reason=reason)


# ==============================================================================
# FASTAPI APP INSTANTIATION
# ==============================================================================

if FastAPI is not None:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        get_engine()
        yield

    app = FastAPI(
        title="BAKEBOX Choco AI — IBM Db2 Autonomous Bakery Management API",
        description="Official REST API for BAKEBOX Choco AI at IBM Db2 TechX Summit 2026. Powered by IBM Db2 & LlamaIndex 3-Way RRF.",
        version="2.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.get("/", tags=["Health"])(get_health_status)
    app.get("/api/health", tags=["Health"])(get_health_status)
    app.post("/api/chat", response_model=ChatResponse, tags=["AI Agent"])(chat_endpoint)
    app.get("/api/cakes/search", tags=["Catalog Search"])(search_cakes)
    app.get("/api/orders/{order_id}", tags=["Orders"])(get_order_tracking)
    app.post("/api/orders/{order_id}/refund", tags=["Orders"])(post_refund_request)
else:
    app = None
