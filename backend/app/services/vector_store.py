"""pgvector store service.

Handles storing and searching document chunks with vector embeddings
in PostgreSQL using the pgvector extension.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def store_chunks(
    dataset_id: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
) -> int:
    """Store document chunks with embeddings in pgvector.

    Args:
        dataset_id: UUID of the dataset the chunks belong to.
        chunks: List of chunk dictionaries with content, page_number, chunk_index.
        embeddings: Corresponding embedding vectors.

    Returns:
        Number of chunks stored.
    """
    logger.info("storing_chunks", dataset_id=dataset_id, count=len(chunks))

    async with async_session_factory() as session:
        for chunk, embedding in zip(chunks, embeddings):
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

            await session.execute(
                text("""
                    INSERT INTO document_chunks
                        (dataset_id, content, page_number, chunk_index, metadata_, embedding)
                    VALUES
                        (:dataset_id, :content, :page_number, :chunk_index, :metadata, :embedding::vector)
                """),
                {
                    "dataset_id": dataset_id,
                    "content": chunk["content"],
                    "page_number": chunk.get("page_number"),
                    "chunk_index": chunk["chunk_index"],
                    "metadata": str(chunk.get("metadata", {})),
                    "embedding": embedding_str,
                },
            )

        await session.commit()

    logger.info("chunks_stored", dataset_id=dataset_id, count=len(chunks))
    return len(chunks)


async def search_similar_chunks(
    query_text: str,
    dataset_id: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Search for document chunks similar to the query text.

    Uses cosine similarity via pgvector to find the most relevant chunks.

    Args:
        query_text: The search query text.
        dataset_id: UUID of the dataset to search within.
        top_k: Number of results to return.

    Returns:
        List of chunk dictionaries ordered by similarity.
    """
    logger.info("searching_chunks", dataset_id=dataset_id, query=query_text[:100])

    # Generate embedding for the query
    from app.services.pdf_processor import generate_embeddings
    query_embeddings = await generate_embeddings([query_text])
    query_embedding = query_embeddings[0]

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    async with async_session_factory() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    content,
                    page_number,
                    chunk_index,
                    metadata_,
                    1 - (embedding <=> :embedding::vector) as similarity
                FROM document_chunks
                WHERE dataset_id = :dataset_id
                ORDER BY embedding <=> :embedding::vector
                LIMIT :top_k
            """),
            {
                "embedding": embedding_str,
                "dataset_id": dataset_id,
                "top_k": top_k,
            },
        )

        rows = result.fetchall()

    chunks = []
    for row in rows:
        chunks.append({
            "id": str(row[0]),
            "content": row[1],
            "page_number": row[2],
            "chunk_index": row[3],
            "metadata": row[4],
            "similarity": float(row[5]) if row[5] else 0.0,
        })

    logger.info("chunks_found", count=len(chunks))
    return chunks


async def delete_dataset_chunks(dataset_id: str) -> int:
    """Delete all chunks for a dataset.

    Args:
        dataset_id: UUID of the dataset whose chunks to delete.

    Returns:
        Number of chunks deleted.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            text("DELETE FROM document_chunks WHERE dataset_id = :dataset_id"),
            {"dataset_id": dataset_id},
        )
        await session.commit()

        count = result.rowcount
        logger.info("chunks_deleted", dataset_id=dataset_id, count=count)
        return count
