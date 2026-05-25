import streamlit as st

from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, normalize_toc_lines, parse_toc


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
