from dotenv import load_dotenv
from pydantic_ai import Agent
import pandas as pd
import structlog
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient

logger = structlog.get_logger(__name__)
load_dotenv()

EMBEDDING_SAVE_FILES = [
    {"file_name": "flare-network_simple_d2.json",
        "qdrant_collection_name": "flare-network"},
    {"file_name": "blaze-swap_simple_d3.json", "qdrant_collection_name": "blaze-swap"}]


def main():
    agent = Agent(
        'google-gla:gemini-2.0-pro-exp-02-05',
        system_prompt='Be concise, reply with one sentence.',
    )

    result = agent.run_sync('What is flare?')
    print(result.data)


def create_app() -> FastAPI:
    app = FastAPI(title="Flare Knowledge API",
                  version="1.0", redirect_slashes=False)

    # Optional: configure CORS middleware using settings.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load RAG data.
    df_docs = []

    logger.debug("Loading JSON dataset files")
    for file in EMBEDDING_SAVE_FILES:
        df_read = pd.read_json(f"src/data/{file['file_name']}")
        df_docs.append(
            {"df": df_read, "qdrant_collection_name": file["qdrant_collection_name"]})

    logger.info("Loaded JSON Data.", num_dfs=len(df_docs))

    return app


app = create_app()


def start() -> None:
    """
    Start the FastAPI application server.
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104


if __name__ == "__main__":
    start()
