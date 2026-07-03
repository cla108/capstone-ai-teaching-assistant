import os
import streamlit as st

from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, parse_toc
from chapter_extractor import extract_chapters_from_pages
from chunker import create_chapter_chunks
from vector_store import VectorStore
from lesson_generator import generate_instructor_guide
from evaluator import evaluate_lesson, rewrite_lesson_if_needed
from pdf_generator import generate_lesson_pdf
from database import DatabaseManager

from config import (
    OPENAI_PROVIDER,
    OLLAMA_PROVIDER,
    OLLAMA_MODELS
)


st.set_page_config(
    page_title="Capstone AI Teaching Assistant",
    layout="wide"
)

st.title("Capstone AI Teaching Assistant")

# ==========================================================
# DATABASE
# ==========================================================

db = DatabaseManager()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("AI Configuration")

provider = st.sidebar.radio(
    "Execution Mode",
    [OPENAI_PROVIDER, OLLAMA_PROVIDER],
    index=0
)

ollama_model = None

if provider == OLLAMA_PROVIDER:

    ollama_label = st.sidebar.selectbox(
        "Local Model",
        list(OLLAMA_MODELS.keys())
    )

    ollama_model = OLLAMA_MODELS[ollama_label]

    st.sidebar.success("Running locally with Ollama")

else:

    st.sidebar.success("Running with OpenAI GPT")

# ==========================================================
# FILE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload textbook PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    with st.spinner("Processing textbook..."):

        pages = extract_text_from_pdf(uploaded_file)
        full_text = combine_pages(pages)

        toc_lines = extract_toc_lines(full_text)
        structure = parse_toc(toc_lines)

        chapters = extract_chapters_from_pages(
            pages,
            structure
        )

    if not chapters:

        st.error(
            "No chapters were detected. Please upload a textbook PDF with a readable table of contents."
        )

        st.stop()

    textbook_id = db.save_textbook(

        filename=uploaded_file.name,

        total_pages=len(pages),

        total_chapters=len(chapters)

    )

    st.success("Textbook processed successfully.")

    chapter_options = [

        f"Chapter {chapter['chapter_number']}: {chapter['chapter_title']}"

        for chapter in chapters

    ]

    selected_chapter_label = st.selectbox(

        "Select chapter",

        chapter_options

    )

    selected_index = chapter_options.index(
        selected_chapter_label
    )

    selected_chapter = chapters[selected_index]

    chapter_id = db.save_chapter(

        textbook_id=textbook_id,

        chapter=selected_chapter

    )

    st.write(

        f"Selected: Chapter {selected_chapter['chapter_number']} — "

        f"{selected_chapter['chapter_title']}"

    )

    # ==========================================================
    # GENERATE LESSON
    # ==========================================================

    if st.button("Generate lesson"):

        progress = st.progress(0)

        status = st.empty()

        # -------------------------
        # Chunking
        # -------------------------

        status.write("Creating recursive + semantic chunks...")

        selected_chapter_chunks = create_chapter_chunks(

            selected_chapter,

            max_words=500,

            overlap_words=75

        )

        progress.progress(20)

        # -------------------------
        # Vector Store
        # -------------------------

        status.write("Building vector store...")

        vector_store = VectorStore(
            provider=provider
        )

        vector_store.add_chunks(
            selected_chapter_chunks
        )

        lesson_query = (

            f"Create instructor guide for Chapter "

            f"{selected_chapter['chapter_number']}: "

            f"{selected_chapter['chapter_title']}"

        )

        retrieved_chunks = vector_store.search(

            lesson_query,

            k=20

        )

        progress.progress(45)

        # -------------------------
        # Lesson Generation
        # -------------------------

        status.write("Generating instructor guide...")

        instructor_guide = generate_instructor_guide(

            selected_chapter=selected_chapter,

            retrieved_chunks=retrieved_chunks,

            provider=provider,

            ollama_model=ollama_model

        )

        progress.progress(65)

        # -------------------------
        # Evaluation
        # -------------------------

        status.write("Evaluating lesson...")

        evaluation = evaluate_lesson(

            instructor_guide=instructor_guide,

            retrieved_chunks=retrieved_chunks,

            provider=provider,

            ollama_model=ollama_model

        )

        progress.progress(80)

        # -------------------------
        # Rewrite if Needed
        # -------------------------

        status.write("Checking quality...")

        instructor_guide, was_rewritten = rewrite_lesson_if_needed(

            instructor_guide=instructor_guide,

            retrieved_chunks=retrieved_chunks,

            evaluation=evaluation,

            provider=provider,

            ollama_model=ollama_model

        )

        if was_rewritten:

            status.write("Re-evaluating rewritten lesson...")

            evaluation = evaluate_lesson(

                instructor_guide=instructor_guide,

                retrieved_chunks=retrieved_chunks,

                provider=provider,

                ollama_model=ollama_model

            )

        progress.progress(90)

        # -------------------------
        # PDF
        # -------------------------

        status.write("Generating PDF...")

        os.makedirs(
            "outputs/lessons",
            exist_ok=True
        )

        output_path = (

            f"outputs/lessons/"

            f"chapter_{selected_chapter['chapter_number']}_"

            f"instructor_guide.pdf"

        )

        generate_lesson_pdf(

            instructor_guide=instructor_guide,

            output_path=output_path

        )

        # -------------------------
        # Database
        # -------------------------

        lesson_id = db.save_lesson(

            chapter_id=chapter_id,

            instructor_guide=instructor_guide,

            output_path=output_path,

            generation_model=(
                ollama_model
                if provider == OLLAMA_PROVIDER
                else "gpt-5.5"
            )

        )

        db.save_evaluation(

            lesson_id=lesson_id,

            evaluation=evaluation

        )

        progress.progress(100)

        status.success("Lesson generated successfully!")

        # -------------------------
        # Results
        # -------------------------

        st.subheader("Evaluation Results")

        st.json(evaluation)

        st.success(
            "Lesson and evaluation saved to MongoDB."
        )

        if was_rewritten:

            st.info(
                "The lesson was automatically rewritten after evaluation."
            )

        else:

            st.success(
                "The lesson passed evaluation without rewrite."
            )

        with open(output_path, "rb") as pdf_file:

            st.download_button(

                label="Download PDF",

                data=pdf_file,

                file_name=(
                    f"chapter_{selected_chapter['chapter_number']}_"
                    f"instructor_guide.pdf"
                ),

                mime="application/pdf"

            )
