from .qdrant import semantic_search
import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from google.generativeai.generative_models import GenerativeModel
from pydantic_ai import Agent, RunContext


# from .response import generate_response

logger = structlog.get_logger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    """
    Pydantic model for chat message validation.

    Attributes:
        message (str): The chat message content, must not be empty
    """

    message: str = Field(..., min_length=1)


class ChatRouter:
    """
    A simple chat router that processes incoming messages using the RAG pipeline.

    It wraps the existing query classification, document retrieval, and response
    generation components to handle a conversation in a single endpoint.
    """

    def __init__(
        self,
        router: APIRouter,
        qdrant_client: QdrantClient,
        gemini_model: GenerativeModel,
        agent: Agent,
        consensus_agent: Agent,
        pydantic_deps
    ) -> None:
        """
        Initialize the ChatRouter.

        Args:
            router (APIRouter): FastAPI router to attach endpoints.
            query_router: Component that classifies the query.
            retriever: Component that retrieves relevant documents.
            responder: Component that generates a response.
        """
        self._router = router
        self.qdrant_client = qdrant_client
        self.gemini_model = gemini_model
        self.agent = agent
        self.consensus_agent = consensus_agent
        self.pydantic_deps = pydantic_deps
        self.logger = logger.bind(router="chat")
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        Set up FastAPI routes for the chat endpoint.
        """

        @self._router.post("/")
        # pyright: ignore [reportUnusedFunction]
        async def chat(message: ChatMessage) -> dict[str, str] | None:
            """
            Process a chat message through the RAG pipeline.
            Returns a response containing the query classification and the answer.
            """
            try:
                self.logger.debug("Received chat message",
                                  message=message.message)

                # @self.agent.tool
                # def retrieve_blaze_swap_documentation(ctx: RunContext[str]):
                #     retrieved_docs = semantic_search(self, qdrant_client=self.qdrant_client,
                #                                      query=ctx.deps, collection_name="blaze-swap", top_k=5
                #                                      )
                #     self.logger.info("Documents retrieved for blaze-swap")
                #     return retrieved_docs

                response = self.agent.run_sync(
                    message.message, deps=message.message)

                logger.debug(response.data)

                # Generate the final answer using retrieved context.
                # answer = generate_response(gemini_model=self.gemini_model,
                #                            query=message.message, retrieved_documents=retrieved_docs
                #                            )
                # self.logger.info("Response generated", answer=answer)
                # return {"response": answer}

                self.logger.info("Response generated", answer=response.data)
                return {"response": response.data}

            except Exception as e:
                self.logger.exception("Chat processing failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e)) from e

        @self._router.post("/consensus")
        # pyright: ignore [reportUnusedFunction]
        async def chat_consensus(message: ChatMessage) -> dict[str, str] | None:
            """
            Process a chat message through the RAG pipeline.
            Returns a response containing the query classification and the answer.
            """
            try:
                self.logger.debug("Received chat message for consensus mode",
                                  message=message.message)

                # @self.agent.tool
                # def retrieve_blaze_swap_documentation(ctx: RunContext[str]):
                #     retrieved_docs = semantic_search(self, qdrant_client=self.qdrant_client,
                #                                      query=ctx.deps, collection_name="blaze-swap", top_k=5
                #                                      )
                #     self.logger.info("Documents retrieved for blaze-swap")
                #     return retrieved_docs

                response = self.consensus_agent.run_sync(
                    message.message, deps=message.message)

                logger.debug(response.data)

                # Generate the final answer using retrieved context.
                # answer = generate_response(gemini_model=self.gemini_model,
                #                            query=message.message, retrieved_documents=retrieved_docs
                #                            )
                # self.logger.info("Response generated", answer=answer)
                # return {"response": answer}

                self.logger.info("Response generated", answer=response.data)
                return {"response": response.data}

            except Exception as e:
                self.logger.exception("Chat processing failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e)) from e

    @property
    def router(self) -> APIRouter:
        """Return the underlying FastAPI router with registered endpoints."""
        return self._router
