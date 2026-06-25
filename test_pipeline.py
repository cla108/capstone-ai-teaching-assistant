import os
import sys

from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, parse_toc
from chapter_extractor import extract_chapters_from_pages
from chunker import create_chapter_chunks
from vector_store import VectorStore
from lesson_generator import generate_instructor_guide
from evaluator import evaluate_lesson, rewrite_lesson_if_needed
from pdf_generator import generate_lesson_pdf


def main():
    print("\n=== Capstone AI Full Pipeline Test ===\n")

    pdf_path = input("Enter PDF path: ").strip()

    if not os.path.exists(pdf_path):
        print(f"\n❌ File not found: {pdf_path}")
        sys.exit(1)

    print("\n1. Extracting PDF text...")
    pages = extract_text_from_pdf(pdf_path)
    full_text = combine_pages(pages)
    print(f"✅ Pages extracted: {len(pages)}")
    print(f"✅ Characters extracted: {len(full_text):,}")

    print("\n2. Parsing table of contents...")
    toc_lines = extract_toc_lines(full_text)
    structure = parse_toc(toc_lines)
    chapters = extract_chapters_from_pages(pages, structure)

    print(f"✅ TOC lines detected: {len(toc_lines)}")
    print(f"✅ Chapters detected: {len(chapters)}")

    if not chapters:
        print("\n❌ No chapters detected. Check TOC parser or input PDF.")
        sys.exit(1)

    print("\nDetected chapters:")
    for i, chapter in enumerate(chapters, start=1):
        print(
            f"{i}. Chapter {chapter['chapter_number']}: "
            f"{chapter['chapter_title']} "
            f"(textbook pages {chapter['start_page']}-{chapter['end_page']})"
        )

    chapter_choice = input("\nSelect chapter number from list above: ").strip()

    try:
        chapter_index = int(chapter_choice) - 1
        selected_chapter = chapters[chapter_index]
    except Exception:
        print("\n❌ Invalid chapter selection.")
        sys.exit(1)

    print(
        f"\nSelected: Chapter {selected_chapter['chapter_number']} - "
        f"{selected_chapter['chapter_title']}"
    )

    print("\n3. Creating recursive + semantic chunks...")
    chunks = create_chapter_chunks(
        selected_chapter,
        max_words=500,
        overlap_words=75
    )
    print(f"✅ Chunks created: {len(chunks)}")

    if chunks:
        print(f"✅ First chunk word count: {chunks[0]['word_count']}")
        print(f"✅ Chunking method: {chunks[0].get('chunking_method')}")

    print("\n4. Building vector store...")
    vector_store = VectorStore()
    vector_store.add_chunks(chunks)
    print("✅ FAISS vector store created.")

    print("\n5. Retrieving relevant chunks...")
    lesson_query = (
        f"Create instructor guide for Chapter "
        f"{selected_chapter['chapter_number']}: "
        f"{selected_chapter['chapter_title']}"
    )

    retrieved_chunks = vector_store.search(lesson_query, k=20)
    print(f"✅ Retrieved chunks: {len(retrieved_chunks)}")

    print("\nTop retrieved chunks:")
    for result in retrieved_chunks[:3]:
        print(
            f"- Chunk {result['chunk_id']} | "
            f"Similarity: {result['similarity_score']:.3f}"
        )

    print("\n6. Generating instructor guide...")
    instructor_guide = generate_instructor_guide(
        selected_chapter=selected_chapter,
        retrieved_chunks=retrieved_chunks
    )
    print("✅ Instructor guide generated.")
    print("\nPreview:")
    print(instructor_guide[:1000])

    print("\n7. Evaluating instructor guide...")
    evaluation = evaluate_lesson(
        instructor_guide=instructor_guide,
        retrieved_chunks=retrieved_chunks
    )
    print("✅ Evaluation complete.")
    print(evaluation)

    print("\n8. Checking if rewrite is needed...")
    final_guide, was_rewritten = rewrite_lesson_if_needed(
        instructor_guide=instructor_guide,
        retrieved_chunks=retrieved_chunks,
        evaluation=evaluation
    )

    if was_rewritten:
        print("✅ Lesson was rewritten based on evaluator feedback.")

        print("\n9. Re-evaluating rewritten lesson...")
        evaluation = evaluate_lesson(
            instructor_guide=final_guide,
            retrieved_chunks=retrieved_chunks
        )
        print("✅ Re-evaluation complete.")
        print(evaluation)
    else:
        print("✅ No rewrite needed.")

    print("\n10. Generating PDF...")
    os.makedirs("outputs/lessons", exist_ok=True)

    output_path = (
        f"outputs/lessons/"
        f"test_chapter_{selected_chapter['chapter_number']}_instructor_guide.pdf"
    )

    generate_lesson_pdf(
        instructor_guide=final_guide,
        output_path=output_path
    )

    print(f"✅ PDF created: {output_path}")

    print("\n=== Pipeline Test Completed Successfully ===\n")


if __name__ == "__main__":
    main()
