
import pandas as pd
import structlog
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from google.generativeai.embedding import (
    EmbeddingTaskType,
)

from .embedding import embed_content

logger = structlog.get_logger(__name__)


def _create_collection(
    client: QdrantClient, collection_name: str, vector_size: int
) -> None:
    """
    Creates a Qdrant collection with the given parameters.
    :param collection_name: Name of the collection.
    :param vector_size: Dimension of the vectors.
    """
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size, distance=Distance.COSINE),
    )


def generate_collection(
    df_docs: pd.DataFrame,
    qdrant_client: QdrantClient,
    qdrant_collection_name: str
) -> None:
    """Routine for generating a Qdrant collection for a specific CSV file type."""
    _create_collection(
        # qdrant_client, retriever_config.collection_name, retriever_config.vector_size
        qdrant_client, qdrant_collection_name, 768
    )
    logger.info(
        # "Created the collection.", collection_name=retriever_config.collection_name
        "Created the collection.", collection_name=qdrant_collection_name
    )

    points = []
    for idx, (_, row) in enumerate(
        df_docs.iterrows(), start=1
    ):  # Using _ for unused variable
        content = row["chunk"]

        if not isinstance(content, str):
            logger.warning(
                "Skipping document due to missing or invalid content.",
                filename=row["page_url"],
            )
            continue

        payload = {
            "page_url": row["page_url"],
            "page_title": row["page_title"],
            "page_description": row["page_description"],
            "text": content,
        }

        point = PointStruct(
            id=idx,  # Using integer ID starting from 1
            vector=row["embedding"],
            payload=payload,
        )
        points.append(point)

    if points:
        qdrant_client.upsert(
            # collection_name=retriever_config.collection_name,  # noqa: ERA001
            collection_name=qdrant_collection_name,
            points=points,
        )
        logger.info(
            "Collection generated and documents inserted into Qdrant successfully.",
            collection_name=qdrant_collection_name,
            num_points=len(points),
        )
    else:
        logger.warning("No valid documents found to insert.")


def semantic_search(qdrant_client: QdrantClient, query: str, collection_name: str, top_k: int = 5) -> list[dict]:
    """
    Perform semantic search by converting the query into a vector
    and searching in Qdrant.

    :param query: The input query.
    :param top_k: Number of top results to return.
    :return: A list of dictionaries, each representing a retrieved document.
    """
    # Convert the query into a vector embedding using Gemini
    query_vector = embed_content(
        contents=query
    )

    logger.debug("User query embedding generated")

    # Search Qdrant for similar vectors.
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
    )

    # Process and return results.
    output = []
    for hit in results:
        if hit.payload:
            text = hit.payload.get("text", "")
            metadata = {
                field: value
                for field, value in hit.payload.items()
                if field != "text"
            }
        else:
            text = ""
            metadata = ""
        output.append(
            {"text": text, "score": hit.score, "metadata": metadata})
    return output
