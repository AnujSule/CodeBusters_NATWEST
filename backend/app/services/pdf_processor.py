"""PDF processor service.

Downloads PDF from MinIO, extracts text using pdfplumber,
splits into chunks, generates embeddings, and stores in pgvector.
"""

import os
import tempfile
from typing import Dict, Any, List, Tuple

import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.storage import download_file_to_path
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Text splitter configured from settings
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)

# Global model cache to prevent re-loading on every request
_model = None


def get_embedding_model():
    """Get or load the SentenceTransformer model (singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("loading_embedding_model", model=settings.EMBEDDING_MODEL)
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from a PDF file page by page using pdfplumber.

    Args:
        file_path: Local path to the PDF file.

    Returns:
        List of dictionaries with page_number and text for each page.
    """
    pages = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({
                    "page_number": i + 1,
                    "text": text.strip(),
                })

    logger.info("pdf_text_extracted", pages=len(pages))
    return pages


def chunk_text(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Split extracted PDF text into chunks for embedding.

    Args:
        pages: List of page dictionaries from extract_text_from_pdf.

    Returns:
        List of chunk dictionaries with content, page_number, and chunk_index.
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        page_chunks = text_splitter.split_text(page["text"])
        for chunk_text_content in page_chunks:
            chunks.append({
                "content": chunk_text_content,
                "page_number": page["page_number"],
                "chunk_index": chunk_index,
                "metadata": {
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                },
            })
            chunk_index += 1

    logger.info("text_chunked", total_chunks=len(chunks))
    return chunks


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using sentence-transformers.

    The model is loaded once and cached in memory.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)

    logger.info("embeddings_generated", count=len(texts))
    return embeddings.tolist()


async def process_pdf(
    object_name: str,
    file_name: str,
    dataset_id: str,
) -> Dict[str, Any]:
    """Process a PDF file: download, extract text, chunk, embed, and store.

    Args:
        object_name: MinIO object key for the PDF file.
        file_name: Original file name.
        dataset_id: UUID of the dataset this PDF belongs to.

    Returns:
        Dictionary with processing results (chunk count, page count, etc.).
    """
    logger.info("processing_pdf", object_name=object_name, file_name=file_name)

    # Download PDF to temp file
    temp_dir = tempfile.mkdtemp(prefix="datadialogue_pdf_")
    temp_path = os.path.join(temp_dir, file_name)
    await download_file_to_path(object_name, temp_path)

    try:
        # Extract text from PDF
        pages = extract_text_from_pdf(temp_path)

        if not pages:
            logger.warning("pdf_empty", file_name=file_name)
            return {
                "chunk_count": 0,
                "page_count": 0,
                "status": "failed",
                "error": "No text could be extracted from the PDF.",
            }

        # Chunk the text
        chunks = chunk_text(pages)

        # Generate embeddings
        chunk_texts = [c["content"] for c in chunks]
        embeddings = await generate_embeddings(chunk_texts)

        # Store in pgvector
        from app.services.vector_store import store_chunks

        await store_chunks(
            dataset_id=dataset_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        result = {
            "chunk_count": len(chunks),
            "page_count": len(pages),
            "status": "ready",
            "file_name": file_name,
        }

        logger.info("pdf_processed", **result)
        return result

    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
            os.rmdir(temp_dir)
        except OSError:
            pass
