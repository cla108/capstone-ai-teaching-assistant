# LessonPlan AI

LessonPlan AI is an AI-powered teaching assistant that automatically generates instructor-ready lesson guides from textbook chapters.

The system combines PDF processing, Retrieval-Augmented Generation (RAG), semantic search, and GPT-5.5 to transform textbook content into structured teaching material.

---

## Features

- Upload any PDF textbook
- Automatically detect the Table of Contents
- Parse Parts, Chapters, and Sections
- Select a chapter from a dropdown menu
- Recursive + Semantic Chunking
- Vector search using FAISS
- Retrieval-Augmented Generation (RAG)
- Human-example guided lesson generation
- Export instructor guide as PDF

---

## Project Pipeline

```
PDF
    ↓
Text Extraction
    ↓
TOC Parsing
    ↓
Chapter Extraction
    ↓
Recursive + Semantic Chunking
    ↓
Vector Embeddings
    ↓
FAISS Retrieval
    ↓
GPT-5.5 Lesson Generation
    ↓
Instructor Guide PDF
```

---

## Repository Structure

```
LessonPlan_AI/

├── app.py
├── pdf_processor.py
├── toc_parser.py
├── chapter_extractor.py
├── page_mapper.py
├── chunker.py
├── vector_store.py
├── lesson_generator.py
├── pdf_generator.py
├── example_loader.py
├── examples/
├── outputs/
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone <repository-url>
cd LessonPlan_AI
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## OpenAI API Key

Create a `.env` file in the project root.

```
OPENAI_API_KEY=your_api_key_here
```

The application uses:

- GPT-5.5 for lesson generation
- text-embedding-3-small for semantic embeddings

---

## Running the Application

```bash
streamlit run app.py
```

---

## Workflow

1. Upload a textbook PDF.
2. The system extracts and parses the Table of Contents.
3. Select a chapter.
4. The chapter is recursively and semantically chunked.
5. Chunks are embedded and stored in a FAISS vector database.
6. Relevant chunks are retrieved using semantic search.
7. GPT-5.5 generates an instructor guide using:
   - Retrieved textbook content
   - Human-written lesson examples as style references
8. Download the generated lesson guide as a PDF.

---

## Technologies

- Python
- Streamlit
- OpenAI API
- GPT-5.5
- text-embedding-3-small
- FAISS
- LangChain SemanticChunker
- PyPDFium2
- PyMuPDF
- ReportLab

---

## Future Improvements

- Automatic extraction of textbook figures and tables
- Citation-aware lesson generation
- Lesson validation pipeline
- Multi-chapter lesson generation
- Interactive teaching activities
- Instructor customization options

---

## Authors

Clara Castro , Ebuka Onuoha

Capstone Project
Langara College
