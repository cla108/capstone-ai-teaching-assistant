from processing.chunker import create_chapter_chunks

from ai.vector_store import VectorStore
from ai.lesson_generator import generate_instructor_guide
from ai.evaluator import (
    evaluate_lesson,
    rewrite_lesson_if_needed,
)


def generate_complete_lesson(
    selected_chapter,
    provider,
    ollama_model=None,
    teaching_style="Practical and interactive",
    difficulty="Intermediate",
    lesson_duration="90 minutes",
    output_type="Instructor Guide",
    include_activities=True,
    include_discussion=True,
    include_quiz=True,
    include_homework=False,
    include_case_study=True,
):
    """
    Complete lesson generation pipeline.

    Only chunks belonging to the selected chapter are indexed and retrieved.
    """

    if not selected_chapter:
        raise ValueError("No chapter was selected.")

    if not selected_chapter.get("text", "").strip():
        raise ValueError(
            "The selected chapter has no extracted text."
        )

    selected_number = selected_chapter["chapter_number"]

    chunks = create_chapter_chunks(
        selected_chapter,
        max_words=500,
        overlap_words=75,
    )

    invalid_chunks = [
        chunk
        for chunk in chunks
        if str(chunk.get("chapter_number")).strip().casefold()
        != str(selected_number).strip().casefold()
    ]

    if invalid_chunks:
        raise ValueError(
            "Chunk metadata contains chapters other than the "
            "selected chapter."
        )

    vector_store = VectorStore(
        provider=provider
    )

    vector_store.add_chunks(chunks)

    lesson_query = (
        f"Create {output_type} for "
        f"Chapter {selected_chapter['chapter_number']}: "
        f"{selected_chapter['chapter_title']}. "
        f"Difficulty: {difficulty}. "
        f"Lesson duration: {lesson_duration}. "
        f"Teaching style: {teaching_style}."
    )

    retrieved_chunks = vector_store.search(
        lesson_query,
        k=min(20, len(chunks)),
        chapter_number=selected_number,
    )

    if not retrieved_chunks:
        raise ValueError(
            "No chunks were retrieved for the selected chapter."
        )

    lesson = generate_instructor_guide(
        selected_chapter=selected_chapter,
        retrieved_chunks=retrieved_chunks,
        provider=provider,
        ollama_model=ollama_model,
    )

    evaluation = evaluate_lesson(
        instructor_guide=lesson,
        retrieved_chunks=retrieved_chunks,
        provider=provider,
        ollama_model=ollama_model,
    )

    lesson, rewritten = rewrite_lesson_if_needed(
        instructor_guide=lesson,
        retrieved_chunks=retrieved_chunks,
        evaluation=evaluation,
        provider=provider,
        ollama_model=ollama_model,
    )

    if rewritten:
        evaluation = evaluate_lesson(
            instructor_guide=lesson,
            retrieved_chunks=retrieved_chunks,
            provider=provider,
            ollama_model=ollama_model,
        )

    return {
        "chunks": chunks,
        "retrieved_chunks": retrieved_chunks,
        "lesson": lesson,
        "evaluation": evaluation,
    }
