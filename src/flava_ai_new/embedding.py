

from google.generativeai.embedding import (
    EmbeddingTaskType,
)
from google.generativeai.embedding import (
    embed_content as _embed_content,
)


def embed_content(
    contents: str
) -> list[float]:
    """
    Generate text embeddings using Gemini.

    Args:
        model (str): The embedding model to use (e.g., "text-embedding-004").
        contents (str): The text to be embedded.

    Returns:
        list[float]: The generated embedding vector.
    """
    response = _embed_content(
        model="models/text-embedding-004", content=contents, task_type=EmbeddingTaskType.RETRIEVAL_QUERY
    )
    try:
        embedding = response["embedding"]
    except (KeyError, IndexError) as e:
        msg = "Failed to extract embedding from response."
        raise ValueError(msg) from e
    return embedding
