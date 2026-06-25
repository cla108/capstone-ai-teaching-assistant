# LessonPlan AI

LessonPlan AI is an AI-powered teaching assistant that automatically generates instructor-ready lesson guides from textbook chapters.

The system combines local PDF processing, Retrieval-Augmented Generation (RAG), semantic search, and GPT-5.5 to transform textbook chapters into structured instructor guides.

---

# Features

- Upload a textbook PDF
- Automatic Table of Contents detection
- Automatic chapter extraction
- Dynamic page offset detection
- Recursive + Semantic Chunking
- Vector database using FAISS
- Retrieval-Augmented Generation (RAG)
- Human lesson examples (Few-shot Prompting)
- Instructor guide generation using GPT-5.5
- Automatic lesson evaluation
- Hallucination detection
- Automatic lesson refinement
- Export lesson guide as PDF

---

# Project Pipeline

```
PDF
 │
 ▼
Text Extraction
 │
 ▼
TOC Parsing
 │
 ▼
Chapter Extraction
 │
 ▼
Dynamic Page Mapping
 │
 ▼
Recursive + Semantic Chunking
 │
 ▼
OpenAI Embeddings
 │
 ▼
FAISS Vector Database
 │
 ▼
Semantic Retrieval (RAG)
 │
 ▼
Human Lesson Examples
 │
 ▼
GPT-5.5 Lesson Generator
 │
 ▼
Lesson Evaluation
 │
 ▼
Automatic Rewrite (if required)
 │
 ▼
PDF Export
```

---

# Technologies

- Python
- Streamlit
- OpenAI API
- GPT-5.5
- text-embedding-3-small
- FAISS
- LangChain
- PyPDFium2
- ReportLab

---

# Installation

Clone the repository.

```bash
git clone <repository-url>
cd LessonPlan_AI
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# OpenAI API Key

Create a `.env` file in the project root.

```
OPENAI_API_KEY=your_api_key_here
```

The application uses:

- GPT-5.5 for lesson generation
- text-embedding-3-small for semantic embeddings

---

# Running the Application

```bash
streamlit run app.py
```

---

# Testing

Run the complete pipeline test.

```bash
python test_pipeline.py
```

The test validates:

- PDF extraction
- TOC parsing
- Chapter extraction
- Recursive + semantic chunking
- FAISS vector retrieval
- Instructor guide generation
- Lesson evaluation
- Automatic rewrite
- PDF generation

---

# Lesson Evaluation

Every generated lesson is automatically evaluated.

The evaluator measures:

- Hallucination rate
- Coverage of textbook concepts
- Structural completeness
- Overall quality score

If the lesson does not satisfy the quality thresholds, it is automatically rewritten before exporting the final PDF.

---

# Current Version

Version 1.0

Implemented:

- Local PDF processing
- Automatic TOC parsing
- Dynamic chapter extraction
- Recursive + Semantic Chunking
- RAG
- Few-shot prompting
- GPT-5.5 lesson generation
- Automatic evaluation
- Hallucination detection
- Automatic lesson refinement
- PDF export

---

# Future Work

- Local embedding models
- Local language models
- Automatic figure and table extraction
- Citation-aware lesson generation
- Multi-chapter lesson generation
- Interactive instructor editing

---

# Author

Clara Castro, Ebuka Onuoha

Capstone Project

Langara College
