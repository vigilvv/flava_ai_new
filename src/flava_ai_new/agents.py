
"""
Sets up pydantic agents - RAG and consensus
"""
import structlog

from pydantic_ai import Agent, RunContext
import requests
from datetime import datetime, timezone


from .PROMPTS import AGENT_SYSTEM_PROMPT, CONSENSUS_MAIN_AGENT_PROMPT, CONSENSUS_SUB_AGENT_PROMPT

# from .agent_tools import retrieve_blaze_swap_documentation, retrieve_flare_network_documentation, get_validator_info
from .qdrant import semantic_search

logger = structlog.get_logger(__name__)


def setup_pydantic_agent(qdrant_client):
    agent = Agent(
        'google-gla:gemini-2.0-pro-exp-02-05',
        system_prompt=AGENT_SYSTEM_PROMPT,
        deps_type=None,
        retries=2
    )

    @agent.tool
    def retrieve_flare_network_documentation(ctx: RunContext[str]):
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

    @agent.tool
    def retrieve_blaze_swap_documentation(ctx: RunContext[str]):
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

    @agent.tool
    def retrieve_spark_dex_documentation(ctx: RunContext[str]):
        """
        Retrieves spark dex documentation.

        Add "Agent tool used: retrieve-spark-dex-documentation" to the end of the message.
        """
        retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                         query=ctx.deps, collection_name="spark-dex_semantic", top_k=5
                                         )

        # print(retrieved_docs)
        logger.info("Documents retrieved for spark-dex")
        return retrieved_docs

    @agent.tool
    def retrieve_rain_dex_documentation(ctx: RunContext[str]):
        """
        Retrieves rain dex documentation.

        Add "Agent tool used: retrieve-rain-dex-documentation" to the end of the message.
        """
        retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                         query=ctx.deps, collection_name="rain-dex_semantic", top_k=5
                                         )

        # print(retrieved_docs)
        logger.info("Documents retrieved for rain-dex")
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

    return agent


def setup_pydantic_consensus_agent(qdrant_client):
    main_agent = Agent(
        'google-gla:gemini-2.0-pro-exp-02-05',
        system_prompt=CONSENSUS_MAIN_AGENT_PROMPT,
        deps_type=None,
        retries=1
    )

    agent_1 = Agent(
        'google-gla:gemini-2.0-flash',
        system_prompt=CONSENSUS_SUB_AGENT_PROMPT,
        deps_type=None,
        retries=1
    )

    agent_2 = Agent(
        'google-gla:gemini-1.5-flash-8b',
        system_prompt=CONSENSUS_SUB_AGENT_PROMPT,
        deps_type=None,
        retries=1
    )

    agent_3 = Agent(
        'openai:gpt-4o-mini',
        system_prompt=CONSENSUS_SUB_AGENT_PROMPT,
        deps_type=None,
        retries=1
    )

    agent_4 = Agent(
        'openai:o3-mini',
        system_prompt=CONSENSUS_SUB_AGENT_PROMPT,
        deps_type=None,
        retries=1
    )

    @main_agent.tool
    async def get_multiple_responses(ctx: RunContext[str]):
        """
        You get multiple responses from multiple agents
        """
        logger.info("Getting multiple responses")
        # first argument is message passesd to this, second argument is message that it passes to its tools
        r1 = await agent_1.run(ctx.deps, deps=ctx.deps)
        r2 = await agent_2.run(ctx.deps, deps=ctx.deps)
        r3 = await agent_3.run(ctx.deps, deps=ctx.deps)
        r4 = await agent_4.run(ctx.deps, deps=ctx.deps)

        print(r1.data)
        print(r2.data)
        print(r3.data)
        print(r4.data)

        return f"""
        Agent 1 response:
        
        {r1.data}\n\n
        
        Agent 2 response:
        
        {r2.data}\n\n
        
        Agent 3 response:
        
        {r3.data}\n\n
        
        Agent 4 response:
        
        {r4.data}\n\n
        """

    ###########################################################
    ###################### AGENT 1 TOOLS ######################
    ###########################################################

    @agent_1.tool
    def retrieve_flare_network_documentation_1(ctx: RunContext[str]):
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

    @agent_1.tool
    def retrieve_blaze_swap_documentation_1(ctx: RunContext[str]):
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

    @agent_1.tool
    def retrieve_spark_dex_documentation(ctx: RunContext[str]):
        """
        Retrieves spark dex documentation.

        Add "Agent tool used: retrieve-spark-dex-documentation" to the end of the message.
        """
        retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                         query=ctx.deps, collection_name="spark-dex_semantic", top_k=5
                                         )

        # print(retrieved_docs)
        logger.info("Documents retrieved for spark-dex")
        return retrieved_docs

    @agent_1.tool
    def retrieve_rain_dex_documentation(ctx: RunContext[str]):
        """
        Retrieves rain dex documentation.

        Add "Agent tool used: retrieve-rain-dex-documentation" to the end of the message.
        """
        retrieved_docs = semantic_search(qdrant_client=qdrant_client,
                                         query=ctx.deps, collection_name="rain-dex_semantic", top_k=5
                                         )

        # print(retrieved_docs)
        logger.info("Documents retrieved for rain-dex")
        return retrieved_docs

    @agent_1.tool_plain
    async def get_validator_info_1():
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

    ###########################################################
    ###################### AGENT 2 TOOLS ######################
    ###########################################################

    @agent_2.tool
    def retrieve_flare_network_documentation_2(ctx: RunContext[str]):
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

    @agent_2.tool
    def retrieve_blaze_swap_documentation_2(ctx: RunContext[str]):
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

    ###########################################################
    ###################### AGENT 3 TOOLS ######################
    ###########################################################

    @agent_3.tool
    def retrieve_flare_network_documentation_3(ctx: RunContext[str]):
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

    @agent_3.tool_plain
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

    ###########################################################
    ###################### AGENT 4 TOOLS ######################
    ###########################################################

    @agent_4.tool
    def retrieve_flare_network_documentation_4(ctx: RunContext[str]):
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

    @agent_4.tool
    def retrieve_blaze_swap_documentation_4(ctx: RunContext[str]):
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

    return main_agent
