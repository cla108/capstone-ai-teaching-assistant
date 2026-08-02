import os
import re
import json
import hashlib

from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings


load_dotenv()

CACHE_DIR = "outputs/cache/chunks"
CACHE_VERSION = "chapter-safe-v2"
os.makedirs(CACHE_DIR, exist_ok=True)


def count_words(text):
    return len(text.split())


def clean_text(text):
    text = re.sub(r"--- PDF PAGE \d+ ---", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_paragraphs(text):
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def force_split_words(text, max_words):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))

    return chunks


def get_cache_path(chapter, max_words, overlap_words):
    """
    Cache by the complete chapter text and verified physical page range.

    This prevents stale chunks from being reused after chapter boundaries
    have been corrected.
    """

    text_hash = hashlib.sha256(
        chapter["text"].encode("utf-8")
    ).hexdigest()

    raw_key = (
        f"{CACHE_VERSION}|"
        f"{chapter['chapter_number']}|"
        f"{chapter['chapter_title']}|"
        f"{chapter.get('pdf_start_page')}|"
        f"{chapter.get('pdf_end_page')}|"
        f"{text_hash}|"
        f"{max_words}|"
        f"{overlap_words}"
    )

    key = hashlib.md5(raw_key.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{key}.json")


def semantic_split_large_text(text):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile"
    )

    documents = splitter.create_documents([text])

    return [
        doc.page_content.strip()
        for doc in documents
        if doc.page_content.strip()
    ]


def recursive_semantic_split(
    text,
    max_words=500,
    semantic_trigger_words=900
):
    text = clean_text(text)
    paragraphs = split_into_paragraphs(text)

    chunks = []
    current_block = ""

    for paragraph in paragraphs:
        candidate = (current_block + "\n\n" + paragraph).strip()

        if count_words(candidate) <= max_words:
            current_block = candidate
            continue

        if current_block:
            chunks.append(current_block)
            current_block = ""

        if count_words(paragraph) > semantic_trigger_words:
            semantic_chunks = semantic_split_large_text(paragraph)

            for semantic_chunk in semantic_chunks:
                if count_words(semantic_chunk) <= max_words:
                    chunks.append(semantic_chunk)
                else:
                    chunks.extend(
                        force_split_words(
                            semantic_chunk,
                            max_words,
                        )
                    )

        elif count_words(paragraph) > max_words:
            chunks.extend(
                force_split_words(
                    paragraph,
                    max_words,
                )
            )

        else:
            current_block = paragraph

    if current_block:
        chunks.append(current_block)

    return chunks


def add_overlap(chunks, overlap_words=75):
    if overlap_words <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = []

    for i, chunk in enumerate(chunks):
        if i == 0:
            overlapped.append(chunk)
            continue

        previous_words = chunks[i - 1].split()
        overlap = " ".join(previous_words[-overlap_words:])

        overlapped.append(
            f"{overlap}\n\n{chunk}".strip()
        )

    return overlapped


def create_chapter_chunks(
    chapter,
    max_words=500,
    overlap_words=75,
    semantic_trigger_words=900
):
    """Create chunks for exactly one verified chapter."""

    if not chapter.get("text", "").strip():
        raise ValueError(
            "The selected chapter contains no extracted text."
        )

    cache_path = get_cache_path(
        chapter,
        max_words,
        overlap_words,
    )

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as file:
            return json.load(file)

    base_chunks = recursive_semantic_split(
        chapter["text"],
        max_words=max_words,
        semantic_trigger_words=semantic_trigger_words
    )

    base_chunks = add_overlap(
        base_chunks,
        overlap_words=overlap_words
    )

    chunks = []
    chapter_key = (
        f"{chapter['chapter_number']}|"
        f"{chapter['chapter_title']}|"
        f"{chapter.get('pdf_start_page')}|"
        f"{chapter.get('pdf_end_page')}"
    )

    for index, text in enumerate(base_chunks, start=1):
        chunks.append({
            "chunk_id": index,
            "chapter_key": chapter_key,
            "chapter_number": chapter["chapter_number"],
            "chapter_title": chapter["chapter_title"],
            "start_page": chapter.get("start_page"),
            "end_page": chapter.get("end_page"),
            "pdf_start_page": chapter.get("pdf_start_page"),
            "pdf_end_page": chapter.get("pdf_end_page"),
            "chunking_method": (
                "recursive paragraph chunking + "
                "semantic chunking for large blocks"
            ),
            "word_count": count_words(text),
            "text": text
        })

    with open(cache_path, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2)

    return chunks
