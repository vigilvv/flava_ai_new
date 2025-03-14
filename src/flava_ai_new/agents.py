
"""
Sets up pydantic agents - RAG and consensus
"""
import structlog

from pydantic_ai import Agent, RunContext


from .PROMPTS import AGENT_SYSTEM_PROMPT, CONSENSUS_MAIN_AGENT_PROMPT, CONSENSUS_SUB_AGENT_PROMPT

from .agent_tools import retrieve_blaze_swap_documentation, retrieve_flare_network_documentation, get_validator_info


logger = structlog.get_logger(__name__)


def setup_pydantic_agent(qdrant_client):
    agent = Agent(
        'google-gla:gemini-2.0-pro-exp-02-05',
        system_prompt=AGENT_SYSTEM_PROMPT,
        deps_type=None,
        retries=2
    )

    def retrieve_flare_network_documentation_with_qdrant(ctx: RunContext[str]):
        return retrieve_flare_network_documentation(ctx, qdrant_client)

    def retrieve_blaze_swap_documentation_with_qdrant(ctx: RunContext[str]):
        return retrieve_blaze_swap_documentation(ctx, qdrant_client)

    agent.tool(retrieve_flare_network_documentation_with_qdrant)
    agent.tool(retrieve_blaze_swap_documentation_with_qdrant)
    agent.tool_plain(get_validator_info)

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

    def retrieve_flare_network_documentation_with_qdrant(ctx: RunContext[str]):
        return retrieve_flare_network_documentation(ctx, qdrant_client)

    def retrieve_blaze_swap_documentation_with_qdrant(ctx: RunContext[str]):
        return retrieve_blaze_swap_documentation(ctx, qdrant_client)

    agent_1.tool(retrieve_flare_network_documentation_with_qdrant)
    agent_1.tool(retrieve_blaze_swap_documentation_with_qdrant)
    agent_1.tool_plain(get_validator_info)

    agent_2.tool(retrieve_flare_network_documentation_with_qdrant)
    agent_2.tool(retrieve_blaze_swap_documentation_with_qdrant)

    agent_3.tool(retrieve_flare_network_documentation_with_qdrant)
    agent_3.tool_plain(get_validator_info)

    agent_4.tool(retrieve_flare_network_documentation_with_qdrant)
    agent_4.tool(retrieve_blaze_swap_documentation_with_qdrant)

    return main_agent
