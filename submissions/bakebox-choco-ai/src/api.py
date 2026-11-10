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
    HTTPException = None
    BaseModel = object
    Field = lambda *args, **kwargs: None

from src.db import is_live_db2_available, get_dbi_connection
from src.query_engine import ChocoQueryEngine, check_prompt_security
from src.order_engine import evaluate_refund_request

START_TIME = time.time()
engine_instance: Optional[ChocoQueryEngine] = None

def get_engine() -> ChocoQueryEngine:
    global engine_instance
    if engine_instance is None:
        engine_instance = ChocoQueryEngine(use_llm=True)
    return engine_instance


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
        reason: str = Field("Cake damaged in transit or incorrect base delivered", min_length=3, max_length=500, description="Reason for refund request")
        phone: str = Field(..., min_length=10, max_length=20, description="Registered 10-digit customer mobile number for two-factor verification")
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
        def __init__(self, reason: str = "Damaged", phone: str = ""):
            self.reason = reason
            self.phone = phone


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
            "Stored Procedure Stock Reservation (SP_RESERVE_CAKE_STOCK via callproc)",
            "In-Database Bill-of-Materials (BOM) CTE (WITH RECIPE_BOM)",
            "Cryptographic SHA-256 Hash-Chained Audit Trail (BB_AUDIT_LOG)"
        ],
        "catalog_items_indexed": len(engine.retriever.corpus_nodes) if hasattr(engine.retriever, "corpus_nodes") else 0,
        "session_isolation": "ENABLED",
        "active_sessions": len(engine.sessions)
    }

def chat_endpoint(req: ChatRequest) -> ChatResponse:
    """Processes customer natural language chat through CHOCO AI with shared guardrail protection."""
    engine = get_engine()
    result = engine.query(req.message, session_id=req.session_id)
    if result.get("guardrail_triggered"):
        return ChatResponse(
            reply=result["reply"],
            ui_cards=[],
            intent="SECURITY_VIOLATION",
            session_id=req.session_id,
            guardrail_triggered=True
        )

    cards = []
    for card in result.get("ui_cards", []):
        cards.append(CakeCardSchema(
            name=card.get("name", "Artisan Cake"),
            price=float(card.get("price", 499.0)),
            eggless=bool(card.get("is_eggless_available", True)),
            branches=["Holigate (Mathura)", "Gosna Highway Kitchen"],
            shelf_life="24 Hours (Chilled)",
            slug=card.get("sku_id", "cake-sku"),
            score=card.get("rrf_score", card.get("score"))
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
    is_safe, flag_reason = check_prompt_security(q)
    if not is_safe:
        if HTTPException is not None:
            raise HTTPException(status_code=400, detail=f"Invalid search query blocked by guardrail: {flag_reason}")
        return {"query": q, "total_matches": 0, "algorithm": "3-Way Reciprocal Rank Fusion (k=60)", "results": [], "guardrail_triggered": True}

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

def post_refund_request(order_id: int, req: Optional[RefundRequest] = None, phone: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluates Shri Ram Baker's Happiness Guarantee policy against Db2 order status.
    Requires two-factor verification (order_id + customer registered phone number)
    before permitting any order mutation.
    """
    auth_phone = (req.phone if req and getattr(req, "phone", None) else phone) or ""
    engine = get_engine()
    auth_check = engine.tool_track_live_order(order_id=order_id, phone_number=auth_phone or None)

    if not auth_check:
        if HTTPException is not None:
            raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
        return {"eligible": False, "order_id": order_id, "status": "ORDER_NOT_FOUND", "message": f"Order #{order_id} not found."}

    if auth_check.get("auth_error") == "VERIFICATION_REQUIRED":
        if HTTPException is not None:
            raise HTTPException(status_code=401, detail="Registered 10-digit phone number is required to authorize refund requests.")
        return {"eligible": False, "order_id": order_id, "status": "VERIFICATION_REQUIRED", "message": "Registered 10-digit phone number is required to authorize refund requests."}

    if auth_check.get("auth_error") == "PHONE_MISMATCH":
        if HTTPException is not None:
            raise HTTPException(status_code=403, detail="Phone number does not match order records.")
        return {"eligible": False, "order_id": order_id, "status": "PHONE_MISMATCH", "message": "Phone number does not match order records."}

    conn = get_dbi_connection()
    try:
        reason = req.reason if req else "Customer claim"
        return evaluate_refund_request(conn, order_id=order_id, reason=reason)
    finally:
        conn.close()


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

    allowed_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    app.get("/", tags=["Health"])(get_health_status)
    app.get("/api/health", tags=["Health"])(get_health_status)
    app.post("/api/chat", response_model=ChatResponse, tags=["AI Agent"])(chat_endpoint)
    app.get("/api/cakes/search", tags=["Catalog Search"])(search_cakes)
    app.get("/api/orders/{order_id}", tags=["Orders"])(get_order_tracking)
    app.post("/api/orders/{order_id}/refund", tags=["Orders"])(post_refund_request)
else:
    app = None
