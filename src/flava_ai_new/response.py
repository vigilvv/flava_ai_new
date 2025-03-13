"""
Generate chat response using Gemini
"""


import structlog


from google.generativeai.types import GenerationConfig

from google.generativeai.generative_models import GenerativeModel

from .PROMPTS import RESPONDER_PROMPT

logger = structlog.get_logger(__name__)


def generate_response(gemini_model: GenerativeModel, query: str, retrieved_documents: list[dict]) -> str:
    """
    Generate a final answer using the query and the retrieved context.

    :param query: The input query.
    :param retrieved_documents: A list of dictionaries containing retrieved docs.
    :return: The generated answer as a string.
    """
    context = "List of retrieved documents:\n"

    # Build context from the retrieved documents.
    for idx, doc in enumerate(retrieved_documents, start=1):
        # identifier = doc.get("metadata", {}).get("filename", f"Doc{idx}")  # noqa: ERA001
        identifier = doc.get("metadata", {}).get("page_url", f"URL{idx}")
        # context += f"Document {identifier}:\n{doc.get('text', '')}\n\n"  # noqa: ERA001
        context += f"URL {identifier}:\n{doc.get('text', '')}\n\n"

    # Compose the prompt
    prompt = context + \
        f"User query: {query}\n" + RESPONDER_PROMPT

    response = gemini_model.generate_content(
        prompt,
        generation_config=GenerationConfig(),
    )

    return response.text
