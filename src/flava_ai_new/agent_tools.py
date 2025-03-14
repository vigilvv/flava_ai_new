"""
Tools that agents can use
"""

import requests
from datetime import datetime, timezone
import structlog
from pydantic_ai import RunContext


from .qdrant import semantic_search

logger = structlog.get_logger(__name__)


def retrieve_flare_network_documentation(ctx: RunContext[str], qdrant_client):
    """
        Retrieves flare network documentation.

        Add "Agent tool used: retrieve-flare-network-documentation" to the end of the message.
        """
    retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                     query=ctx.deps, collection_name="flare-network", top_k=8
                                     )

    # print(retrieved_docs)
    logger.info("Documents retrieved for flare-network")
    return retrieved_docs


def retrieve_blaze_swap_documentation(ctx: RunContext[str], qdrant_client):
    """
    Retrieves blaze swap documentation.

    Add "Agent tool used: retrieve-blaze-swap-documentation" to the end of the message.
    """
    retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                     query=ctx.deps, collection_name="blaze-swap", top_k=5
                                     )

    # print(retrieved_docs)
    logger.info("Documents retrieved for blaze-swap")
    return retrieved_docs


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

    Add "Agent tool used: get-validator-info" to the end of the message.

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

        # print(all_validators)
        return all_validators
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
