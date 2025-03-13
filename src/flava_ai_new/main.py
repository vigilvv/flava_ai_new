from dotenv import load_dotenv
import pandas as pd
import structlog
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
import os
from dataclasses import dataclass

import requests
from datetime import datetime, timezone

import nest_asyncio

from .chat import ChatRouter

from .qdrant import generate_collection
from google.generativeai.generative_models import GenerativeModel

from .PROMPTS import SYSTEM_INSTRUCTION, AGENT_SYSTEM_PROMPT

from google.generativeai.client import configure

from .qdrant import semantic_search
from pydantic_ai import Agent, RunContext

load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))


logger = structlog.get_logger(__name__)


@dataclass
class PydanticAIDeps:
    qdrant: QdrantClient


# EMBEDDING_SAVE_FILES = [
#     {"file_name": "flare-network_simple_d2.json",
#         "qdrant_collection_name": "flare-network"},
#     {"file_name": "blaze-swap_simple_d3.json", "qdrant_collection_name": "blaze-swap"}]

EMBEDDING_SAVE_FILES = [
    {"file_name": "blaze-swap_simple_d3.json", "qdrant_collection_name": "blaze-swap"}]


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
    agent = Agent(
        'google-gla:gemini-2.0-pro-exp-02-05',
        system_prompt=AGENT_SYSTEM_PROMPT,
        deps_type=PydanticAIDeps,
        retries=1  # Todo: Change to 2 before deployoment
    )

    @agent.tool
    def retrieve_blaze_swap_documentation(ctx: RunContext[str]):
        retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                         query=ctx.deps, collection_name="blaze-swap", top_k=5
                                         )
        logger.info("Documents retrieved for blaze-swap")
        return retrieved_docs

    @agent.tool_plain
    async def get_validator_info():
        """
        Retrieve information about validators in the flare network. If any specific information about the validator is asked use this tool. Like if a user names a validator and asks questions about it.

        Returns: It returns an array of objects with the following fields:
            "name" - Name of the validator
            "node_id" - Node id of the validator. When asked check if there are multiple entries with the same "name" and provide the the node_id for each entry. The different validators under the same "name" are identified by different "validator_number" field.
            "total_stake" - is the total amount of flr staked to the validator
            "free_space" - is the free space in flr left in the validator for people to stake -- not used
            "fee" - is the percentage fee charged by the validator
            "delegators" - is the number of people currently delegated to the validator
            "start_date" - is the date when the validator was started
            "end_date" - is the date when the validator will expire
            "time_left" - is the time left from now in days when the validator will expire
            "uptime" - is the uptime of the validator. multiply it by 100 to convert it to a percentage.
            "version" - is the validator node version
            "validator_number" - is the number of validator run by "name". When asked how many validators a particular "name" is running, check for the highest number in the array for all the same "name"s. That number + 1, would be the total number of validators that the "name" is running. For example, if "validator_number" is "0" and there is no other entry for the same "name", then they are running only 1 validator.

        """

        url = "https://api.flaremetrics.io/v2/network/validators/flare/stakes"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            data = response.json()  # Convert response to JSON

            all_validators = []  # Only contains relevant data
            # Only take relevant data
            for entry in data:
                validator_dict = {}

                if ((entry["validator"]["entity"] is not None) and (entry["validator"]["entity"]["companyProfile"] is not None)):
                    validator_dict = {
                        "name": entry["validator"].get("entity", {}).get("companyProfile", {}).get("name", "Unknown"),
                        "node_id": entry["validator"]["nodeId"],
                        "total_stake": entry["stakeTotal"],
                        "cap": entry["stakeAmount"],
                        # "free_space": entry["stakeTotal"] - entry["stakeAmount"],
                        "fee": entry["delegationFeePct"],
                        "delegators": entry["delegators"],
                        "start_date": entry["startTime"],
                        "end_date": entry["endTime"],
                        "time_left": (datetime.fromisoformat(entry["endTime"].replace("Z", "")).replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days,
                        "uptime": entry["uptime"],
                        "version": entry["version"],
                        "validator_number": "0" if entry["validator"].get("label") is None else entry["validator"]["label"]
                    }

                    all_validators.append(validator_dict)

            print(all_validators)
            return all_validators
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    # Create an APIRouter for chat endpoints and initialize ChatRouter.
    chat_router = ChatRouter(
        router=APIRouter(),
        qdrant_client=qdrant_client,
        gemini_model=gemini_model,
        agent=agent,
        pydantic_deps=PydanticAIDeps
    )
    app.include_router(chat_router.router,
                       prefix="/api/routes/chat", tags=["chat"])

    return app


app = create_app()


def start() -> None:
    """
    Start the FastAPI application server.
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104


if __name__ == "__main__":
    start()
