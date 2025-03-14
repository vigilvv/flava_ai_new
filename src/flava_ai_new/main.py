from dotenv import load_dotenv
import pandas as pd
import structlog
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
import os
# from dataclasses import dataclass


import nest_asyncio

from .chat import ChatRouter
from .agents import setup_pydantic_agent, setup_pydantic_consensus_agent

from .qdrant import generate_collection
from google.generativeai.generative_models import GenerativeModel

from .PROMPTS import SYSTEM_INSTRUCTION

from google.generativeai.client import configure


load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))


logger = structlog.get_logger(__name__)


# @dataclass
# class PydanticAIDeps:
#     qdrant: QdrantClient


EMBEDDING_SAVE_FILES = [
    {"file_name": "flare-network_simple_d2.json",
        "qdrant_collection_name": "flare-network"},
    {"file_name": "blaze-swap_simple_d3.json", "qdrant_collection_name": "blaze-swap"}]

# EMBEDDING_SAVE_FILES = [
#     {"file_name": "blaze-swap_simple_d3.json", "qdrant_collection_name": "blaze-swap"}]


# def main():
#     agent = Agent(
#         'google-gla:gemini-2.0-pro-exp-02-05',
#         system_prompt='Be concise, reply with one sentence.',
#     )

#     result = agent.run_sync('What is flare?')
#     print(result.data)


def setup_qdrant():
    # Load RAG data and convert to df
    df_docs = []

    logger.debug("Loading JSON dataset files")
    for file in EMBEDDING_SAVE_FILES:
        df_read = pd.read_json(f"src/data/{file['file_name']}")
        df_docs.append(
            {"df": df_read, "qdrant_collection_name": file["qdrant_collection_name"]})

    logger.info("Loaded JSON Data.", num_dfs=len(df_docs))

    # Setup qdrant client
    qdrant_client = QdrantClient(
        host="localhost", port=6333)

    # Generate qdrant collection
    for file in df_docs:
        generate_collection(
            file["df"],
            qdrant_client,
            file["qdrant_collection_name"]
        )

    logger.info(
        "The Qdrant collection has been generated.",
        # collection_name=retriever_config.collection_name,  # noqa: ERA001
    )

    return qdrant_client


def setup_gemini():
    model = GenerativeModel(
        model_name="gemini-2.0-pro-exp-02-05",
        system_instruction=SYSTEM_INSTRUCTION
    )

    return model


def create_app() -> FastAPI:

    nest_asyncio.apply()

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

    qdrant_client = setup_qdrant()

    gemini_model = setup_gemini()

    # Setup Pydantic AI Agent

    agent = setup_pydantic_agent(qdrant_client)
    consensus_agent = setup_pydantic_consensus_agent(qdrant_client)

    # Create an APIRouter for chat endpoints and initialize ChatRouter.
    chat_router = ChatRouter(
        router=APIRouter(),
        qdrant_client=qdrant_client,
        gemini_model=gemini_model,
        agent=agent,
        # pydantic_deps=PydanticAIDeps
        consensus_agent=consensus_agent,
        pydantic_deps=None
    )
    app.include_router(chat_router.router,
                       prefix="/api/routes/chat", tags=["chat"])
    # app.include_router(chat_router.router,
    #                    prefix="/api/routes/chat/consensus", tags=["consensus"])

    return app


app = create_app()


def start() -> None:
    """
    Start the FastAPI application server.
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104


if __name__ == "__main__":
    start()
