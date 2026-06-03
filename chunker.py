import re


def chunk_text_by_words(text, max_words=500, overlap_words=75):
    """
    Splits text into overlapping word-based chunks.
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += max_words - overlap_words

    return chunks


def create_chapter_chunks(chapter, max_words=500, overlap_words=75):
    """
    Creates retrieval-ready chunks from one chapter.

    Each chunk keeps metadata needed for RAG.
    """

    raw_chunks = chunk_text_by_words(
        chapter["text"],
        max_words=max_words,
        overlap_words=overlap_words
    )

    chunks = []

    for i, chunk_text in enumerate(raw_chunks, start=1):
        chunks.append({
            "chunk_id": i,
            "chapter_number": chapter["chapter_number"],
            "chapter_title": chapter["chapter_title"],
            "part": chapter["part"],
            "start_page": chapter["start_page"],
            "end_page": chapter["end_page"],
            "text": chunk_text
        })

    return chunks


def create_all_chunks(chapters, max_words=500, overlap_words=75):
    """
    Creates chunks for all extracted chapters.
    """

    all_chunks = []

    for chapter in chapters:
        chapter_chunks = create_chapter_chunks(
            chapter,
            max_words=max_words,
            overlap_words=overlap_words
        )

        all_chunks.extend(chapter_chunks)

    return all_chunks
