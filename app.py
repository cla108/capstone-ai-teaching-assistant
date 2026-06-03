import streamlit as st

from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, normalize_toc_lines, parse_toc
from chapter_extractor import extract_chapters_from_pages
from chunker import create_chapter_chunks
from visual_extractor import extract_images_from_pdf

st.set_page_config(
    page_title="Capstone AI",
    layout="wide"
)

st.title("Capstone AI - Textbook Structure Detector")

uploaded_file = st.file_uploader(
    "Upload a textbook PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("PDF uploaded successfully.")

    with st.spinner("Extracting text from PDF..."):
        pages = extract_text_from_pdf(uploaded_file)
        full_text = combine_pages(pages)

    st.subheader("PDF Summary")
    st.write(f"Pages processed: {len(pages)}")
    st.write(f"Characters extracted: {len(full_text):,}")

    st.subheader("First 100 Lines Extracted")
    st.text_area(
        "Raw extracted text preview",
        "\n".join(full_text.splitlines()[:100]),
        height=300
    )

    with st.spinner("Extracting table of contents..."):
        toc_lines = extract_toc_lines(full_text)
        normalized_entries = normalize_toc_lines(toc_lines)
        structure = parse_toc(toc_lines)
        chapters = extract_chapters_from_pages(pages, structure)

    st.subheader("Raw TOC Lines")
    st.text_area(
        "TOC Preview",
        "\n".join(toc_lines[:200]),
        height=300
    )

    st.subheader("Normalized TOC Entries")
    st.text_area(
        "Normalized Entries",
        "\n".join(normalized_entries[:120]),
        height=400
    )

    st.subheader("Parsed Structure")

    if not structure:
        st.warning("No structure detected yet.")

    for part in structure:
        st.markdown(f"## {part['part']}")

        for chapter in part["chapters"]:
            st.markdown(
                f"### Chapter {chapter['chapter_number']}: "
                f"{chapter['chapter_title']} "
                f"(p. {chapter['start_page']})"
            )

            for section in chapter["sections"]:
                st.write(
                    f"- {section['section_title']} "
                    f"(p. {section['start_page']})"
                )

    st.subheader("Extracted Chapter Text")

    chapter_options = [
        f"Chapter {chapter['chapter_number']}: {chapter['chapter_title']}"
        for chapter in chapters
    ]

    selected_chapter_label = st.selectbox(
        "Select chapter to preview",
        chapter_options
    )

    selected_index = chapter_options.index(selected_chapter_label)
    selected_chapter = chapters[selected_index]

    st.write(f"Start page: {selected_chapter['start_page']}")
    st.write(f"End page: {selected_chapter['end_page']}")
    st.write(f"Characters: {len(selected_chapter['text']):,}")
    st.write(f"Total extracted chapters: {len(chapters)}")

    preview_length = st.slider(
        "Preview length",
        min_value=1000,
        max_value=10000,
        value=3000,
        step=1000
    )

    st.text_area(
        "Chapter text preview",
        selected_chapter["text"][:preview_length],
        height=400
    )

    st.subheader("Chapter Chunking Preview")

    max_words = st.slider(
        "Max words per chunk",
        min_value=200,
        max_value=1000,
        value=500,
        step=100
    )

    overlap_words = st.slider(
        "Overlap words",
        min_value=0,
        max_value=200,
        value=75,
        step=25
    )

    selected_chapter_chunks = create_chapter_chunks(
        selected_chapter,
        max_words=max_words,
        overlap_words=overlap_words
    )

    st.write(f"Total chunks for selected chapter: {len(selected_chapter_chunks)}")

    chunk_options = [
        f"Chunk {chunk['chunk_id']}"
        for chunk in selected_chapter_chunks
    ]

    selected_chunk_label = st.selectbox(
        "Select chunk to preview",
        chunk_options
    )

    selected_chunk_index = chunk_options.index(selected_chunk_label)
    selected_chunk = selected_chapter_chunks[selected_chunk_index]

    st.text_area(
        "Chunk preview",
        selected_chunk["text"],
        height=300
    )

    st.subheader("Semantic Retrieval Test")

    query = st.text_input(
        "Ask a question about the selected chapter",
        placeholder="Example: What is the role of transportation in the supply chain?"
    )

    if st.button("Retrieve relevant chunks"):
        from vector_store import VectorStore

        if not query.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Creating embeddings and searching chunks..."):
                vector_store = VectorStore()
                vector_store.add_chunks(selected_chapter_chunks)
                results = vector_store.search(query, k=3)

            st.write("Top retrieved chunks:")

            for result in results:
                st.markdown(
                    f"**Chunk {result['chunk_id']} | "
                    f"Similarity: {result['similarity_score']:.3f}**"
                )

                st.text_area(
                    f"Retrieved chunk {result['chunk_id']}",
                    result["text"][:2000],
                    height=250
                )






    st.subheader("Images in This Chapter")

    if st.button("Extract chapter images"):

        with st.spinner("Extracting images from selected chapter..."):

            chapter_images = extract_images_from_pdf(
                uploaded_file,
                selected_chapter["start_page"],
                selected_chapter["end_page"],
                selected_chapter["chapter_number"],
                page_offset=23 # Adjust this offset based on the actual page numbering in the PDF

            )

        if not chapter_images:
            st.info("No images found in this chapter.")

        else:
            st.write(f"Images found: {len(chapter_images)}")

            for image in chapter_images:

                if image["type"] == "image":


                    st.markdown(
                        f"**Textbook Page {image['textbook_page_number']} "
                        f"(PDF Page {image['pdf_page_number']})**"
                    )


                    st.image(
                        image["image_path"],
                        use_container_width=True
                    )

                else:
                    st.warning(
                        f"Could not extract image from page "
                        f"{image['page_number']}"
                    )
