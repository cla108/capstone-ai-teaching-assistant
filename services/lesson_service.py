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

    Returns
    -------
    dict
        {
            "chunks": ...,
            "retrieved_chunks": ...,
            "lesson": ...,
            "evaluation": ...
        }
    """

    # --------------------------------------------------
    # Create chunks
    # --------------------------------------------------

    chunks = create_chapter_chunks(
        selected_chapter,
        max_words=500,
        overlap_words=75,
    )

    # --------------------------------------------------
    # Build vector store
    # --------------------------------------------------

    vector_store = VectorStore(
        provider=provider
    )

    vector_store.add_chunks(chunks)

    # --------------------------------------------------
    # Retrieve context
    # --------------------------------------------------

    lesson_query = (
        f"Create instructor guide for "
        f"Chapter {selected_chapter['chapter_number']}: "
        f"{selected_chapter['chapter_title']}"
    )

    retrieved_chunks = vector_store.search(
        lesson_query,
        k=20,
    )

    # --------------------------------------------------
    # Generate lesson
    # --------------------------------------------------

    lesson = generate_instructor_guide(
        selected_chapter=selected_chapter,
        retrieved_chunks=retrieved_chunks,
        provider=provider,
        ollama_model=ollama_model,
    )

    # --------------------------------------------------
    # Evaluate
    # --------------------------------------------------

    evaluation = evaluate_lesson(
        instructor_guide=lesson,
        retrieved_chunks=retrieved_chunks,
        provider=provider,
        ollama_model=ollama_model,
    )

    # --------------------------------------------------
    # Rewrite if necessary
    # --------------------------------------------------

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
