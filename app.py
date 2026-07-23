import os
import streamlit as st
from ui.sidebar import render_sidebar
from processing.pdf_processor import (
    extract_text_from_pdf,
    combine_pages,
)
from processing.toc_parser import (
    extract_toc_lines,
    parse_toc,
)
from processing.chapter_extractor import (
    extract_chapters_from_pages,
)
from services.lesson_service import (
    generate_complete_lesson,
)
from services.pdf_generator import (
    generate_lesson_pdf,
)
from database.database import DatabaseManager
from config import OPENAI_PROVIDER

from ui.textbook import (
    render_book_information,
    render_table_of_contents,
)

from ui.chapter import (
    select_chapter,
    render_chapter_information,
    render_chapter_preview,
)

from ui.generation import (
    render_chunks,
    render_rag_context,
    render_evaluation,
    render_statistics,
    render_lesson_editor,
)

# Page configuration
st.set_page_config(
    page_title="Capstone AI Teaching Assistant",
    layout="wide"
)

# Render sidebar
render_sidebar()

# Workflow instructions
st.info(
    """
    Workflow

    1️⃣ Upload textbook
    2️⃣ Review detected chapters
    3️⃣ Select chapter
    4️⃣ Generate lesson
    5️⃣ Review and edit
    6️⃣ Export PDF
    """
)

st.title("Capstone AI Teaching Assistant")
st.caption(
    "Generate instructor-ready lesson guides using Retrieval-Augmented Generation (RAG)."
)

# Initialize database
try:
    db = DatabaseManager()
    database_enabled = True
except Exception:
    db = None
    database_enabled = False

# Provider settings
provider = OPENAI_PROVIDER
ollama_model = None

# Initialize session state with cleaner approach
defaults = {
    "instructor_guide": None,
    "evaluation": None,
    "selected_chapter_chunks": [],
    "retrieved_chunks": [],
    "edited_lesson": None,
    "generation_settings": {},  # Store settings used for generation
}

for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# File upload
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

    # Save textbook to database if enabled
    if database_enabled:
        textbook_id = db.save_textbook(
            filename=uploaded_file.name,
            total_pages=len(pages),
            total_chapters=len(chapters)
        )
    else:
        textbook_id = None

    st.success("Textbook processed successfully.")

    # Create tabs - Chat tab is commented out until implemented
    tab1, tab2, tab3 = st.tabs([
        "📖 Chapter",
        "🧩 RAG Pipeline",
        "📄 Instructor Guide"
    ])
    # Fourth tab for future chat feature
    # tab1, tab2, tab3, tab4 = st.tabs([
    #     "📖 Chapter",
    #     "🧩 RAG Pipeline",
    #     "📄 Instructor Guide",
    #     "💬 Ask the Textbook"
    # ])

    # Tab 1: Chapter Selection and Preview
    with tab1:
        render_book_information(
            pages,
            chapters
        )

        render_table_of_contents(
            chapters
        )

        selected_chapter = select_chapter(
            chapters
        )

        if database_enabled and selected_chapter:
            chapter_id = db.save_chapter(
                textbook_id=textbook_id,
                chapter=selected_chapter
            )
        else:
            chapter_id = None

        render_chapter_information(
            selected_chapter
        )

        render_chapter_preview(
            selected_chapter
        )

        # Moved Lesson Settings inside Tab 1
        st.divider()
        st.subheader("⚙️ Lesson Settings")

        col1, col2 = st.columns(2)

        with col1:
            difficulty = st.selectbox(
                "Difficulty Level",
                [
                    "Beginner",
                    "Intermediate",
                    "Advanced",
                ],
                index=1,
                key="difficulty"
            )

            lesson_duration = st.selectbox(
                "Lesson Duration",
                [
                    "30 minutes",
                    "60 minutes",
                    "90 minutes",
                    "120 minutes",
                ],
                index=2,
                key="duration"
            )

            output_type = st.selectbox(
                "Output Type",
                [
                    "Instructor Guide",
                    "Lecture Notes",
                    "Student Handout",
                ],
                key="output_type"
            )

        with col2:
            teaching_style = st.selectbox(
                "Teaching Style",
                [
                    "Practical and interactive",
                    "Lecture-based",
                    "Discussion-based",
                    "Case-study focused",
                    "Problem-based learning",
                ],
                key="teaching_style"
            )

            include_activities = st.checkbox(
                "Include Class Activities",
                value=True,
                key="activities"
            )

            include_discussion = st.checkbox(
                "Include Discussion Questions",
                value=True,
                key="discussion"
            )

            include_quiz = st.checkbox(
                "Include Quiz",
                value=True,
                key="quiz"
            )

            include_homework = st.checkbox(
                "Include Homework",
                value=False,
                key="homework"
            )

            include_case_study = st.checkbox(
                "Include Case Study Guidance",
                value=True,
                key="case_study"
            )

        # Generate button moved inside Tab 1
        generate = st.button(
            "🚀 Generate Instructor Guide",
            type="primary",
            use_container_width=True,
            key="generate_button"
        )

    # Generation logic with smoother progress
    if generate and selected_chapter:
        try:
            # Initialize progress tracking with more granular steps
            progress = st.progress(0)
            status = st.empty()

            # Step 1: Reading chapter content
            status.write("📖 Reading chapter content...")
            progress.progress(10)

            # Step 2: Chunking
            status.write("✂️ Chunking content...")
            progress.progress(30)

            # Step 3: Retrieving relevant context
            status.write("🔍 Retrieving relevant context...")
            progress.progress(50)

            # Step 4: Generating lesson
            status.write("📝 Generating lesson content...")
            progress.progress(70)

            # Store settings for later display
            st.session_state.generation_settings = {
                "difficulty": difficulty,
                "duration": lesson_duration,
                "teaching_style": teaching_style,
                "output_type": output_type,
                "include_activities": include_activities,
                "include_discussion": include_discussion,
                "include_quiz": include_quiz,
                "include_homework": include_homework,
                "include_case_study": include_case_study,
            }




            result = generate_complete_lesson(
                selected_chapter=selected_chapter,
                provider=provider,
                ollama_model=ollama_model,
                teaching_style=teaching_style,
                difficulty=difficulty,
                lesson_duration=lesson_duration,
                output_type=output_type,
                include_activities=include_activities,
                include_discussion=include_discussion,
                include_quiz=include_quiz,
                include_homework=include_homework,
                include_case_study=include_case_study,
            )

            # Extract everything from the single result
            st.session_state.selected_chapter_chunks = result.get("chunks", [])
            st.session_state.retrieved_chunks = result.get("retrieved_chunks", [])
            st.session_state.instructor_guide = result.get("lesson", "")

            # Safely extract and validate evaluation
            evaluation = result.get("evaluation", {})
            if not isinstance(evaluation, dict):
                evaluation = {}

            # Ensure all numeric values are actually numbers
            for key in ["hallucination_rate", "coverage_score", "structure_score", "overall_score"]:
                if key in evaluation and isinstance(evaluation[key], list):
                    evaluation[key] = evaluation[key][0] if evaluation[key] else 0.0
                elif key in evaluation and not isinstance(evaluation[key], (int, float)):
                    try:
                        evaluation[key] = float(evaluation[key])
                    except (ValueError, TypeError):
                        evaluation[key] = 0.0

            # Ensure list fields are lists
            for key in ["missing_concepts", "unsupported_claim_examples"]:
                if key in evaluation and not isinstance(evaluation[key], list):
                    evaluation[key] = [evaluation[key]] if evaluation[key] else []

            st.session_state.evaluation = evaluation




            # Step 5: Evaluating
            status.write("🔍 Evaluating lesson quality...")
            progress.progress(90)

            # Final step
            status.success("✅ Lesson generated successfully!")
            progress.progress(100)

            # Store in session state for persistence across tabs
            st.session_state.edited_lesson = st.session_state.instructor_guide

        except Exception as e:
            st.error(f"❌ Error generating lesson: {str(e)}")
            st.exception(e)
            progress.empty()  # Remove progress bar on error

    # Tab 2: RAG Pipeline
    with tab2:
        if st.session_state.selected_chapter_chunks:
            render_chunks(
                st.session_state.selected_chapter_chunks
            )
            render_rag_context(
                st.session_state.retrieved_chunks
            )
        else:
            st.info("💡 Generate a lesson first to see the RAG pipeline in action.")

    # Tab 3: Instructor Guide
    with tab3:
        if st.session_state.instructor_guide:
            # Display settings summary
            st.subheader("📋 Lesson Configuration")
            st.json(st.session_state.generation_settings)

            # Display evaluation
            st.subheader("📊 Lesson Evaluation")
            render_evaluation(
                st.session_state.evaluation
            )

            # Allow editing
            st.session_state.edited_lesson = render_lesson_editor(
                st.session_state.instructor_guide
            )

            render_statistics(
                len(st.session_state.selected_chapter_chunks),
                len(st.session_state.retrieved_chunks),
                provider
            )

            # Export PDF section
            st.divider()
            st.subheader("📄 Export PDF")

            # PDF Export Button - Only saves lesson when clicked
            if st.button(
                "📄 Generate PDF",
                type="primary",
                use_container_width=True,
                key="pdf_button"
            ):
                with st.spinner("Generating PDF..."):
                    # Create output directory
                    os.makedirs(
                        "outputs/lessons",
                        exist_ok=True
                    )

                    # Generate output path
                    chapter_num = selected_chapter.get('chapter_number', 'unknown')
                    output_path = (
                        f"outputs/lessons/"
                        f"chapter_{chapter_num}_"
                        f"instructor_guide.pdf"
                    )

                    # Generate PDF
                    generate_lesson_pdf(
                        instructor_guide=st.session_state.edited_lesson,
                        output_path=output_path
                    )

                    # Save to database only when PDF is generated
                    if database_enabled and chapter_id:
                        lesson_id = db.save_lesson(
                            chapter_id=chapter_id,
                            instructor_guide=st.session_state.edited_lesson,
                            output_path=output_path,
                            generation_model=provider
                        )

                        db.save_evaluation(
                            lesson_id=lesson_id,
                            evaluation=st.session_state.evaluation
                        )

                    st.success("✅ PDF generated successfully!")

                    # Provide download button
                    with open(output_path, "rb") as pdf_file:
                        st.download_button(
                            "⬇️ Download Instructor Guide",
                            pdf_file,
                            file_name=f"chapter_{chapter_num}_instructor_guide.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
        else:
            st.info("💡 Generate a lesson first to see the instructor guide.")

    # Tab 4: Chat with Textbook (COMING SOON)
    # with tab4:
    #     st.info("💬 Coming soon: Ask questions about the textbook using RAG.")
    #     st.caption("This feature will allow you to have a conversation with your textbook content.")

else:
    # No file uploaded
    st.info("👆 Please upload a textbook PDF to begin.")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit and OpenAI")
