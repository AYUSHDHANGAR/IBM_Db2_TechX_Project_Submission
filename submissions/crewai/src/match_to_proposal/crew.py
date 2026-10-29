import os
from typing import List, Optional
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import DB2VectorSearchTool, FileReadTool
from src.utils.db2_config import get_db2_config
from src.utils.embeddings import local_embedding_function, get_embedding_model_name


def get_configured_llm() -> LLM:
    """
    Configure reasoning LLM for CrewAI agents.
    Prioritizes OpenAI if OPENAI_API_KEY is set, otherwise falls back to local Ollama (granite3.3:8b).
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and not openai_key.startswith("your_"):
        model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        return LLM(model=model, api_key=openai_key)

    # Local Ollama fallback (e.g. granite3.3:8b)
    ollama_model = os.getenv("OLLAMA_MODEL", "ollama/granite3.3:8b")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"🤖 Using local Ollama LLM for agent reasoning: '{ollama_model}' at {ollama_base_url}")
    return LLM(model=ollama_model, base_url=ollama_base_url)


@CrewBase
class MatchToDb2PositionsCrew:
    """Crew for matching CVs to job opportunities stored in IBM Db2 Vector Database using Local Granite Embeddings."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def cv_reader(self) -> Agent:
        llm = get_configured_llm()
        return Agent(
            config=self.agents_config["cv_reader"],
            tools=[FileReadTool()],
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def matcher(self) -> Agent:
        cfg = get_db2_config()
        model_name = get_embedding_model_name()
        llm = get_configured_llm()

        print(f"🔗 Initializing DB2VectorSearchTool with local embedding model: '{model_name}'...")

        # Initialize the official CrewAI DB2VectorSearchTool using custom local embedding function
        db2_tool = DB2VectorSearchTool(
            connection_string=cfg["connection_string"],
            table_name=cfg["table_name"],
            vector_column="embedding",
            return_columns=["id", "content", "meta"],
            limit=5,
            distance_metric="COSINE",
            custom_embedding_fn=local_embedding_function,
        )

        return Agent(
            config=self.agents_config["matcher"],
            tools=[db2_tool],
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    @task
    def read_cv_task(self) -> Task:
        return Task(
            config=self.tasks_config["read_cv_task"],
            agent=self.cv_reader(),
        )

    @task
    def match_cv_task(self) -> Task:
        return Task(
            config=self.tasks_config["match_cv_task"],
            agent=self.matcher(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MatchToProposal crew with sequential execution."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
