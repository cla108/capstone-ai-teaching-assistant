# LessonPlan AI

LessonPlan AI is an AI-powered teaching assistant that automatically generates instructor-ready lesson guides from textbook chapters.

The system combines local PDF processing, Retrieval-Augmented Generation (RAG), recursive and semantic chunking, vector search with FAISS, GPT-5.5, and an automatic evaluation loop to produce high-quality instructor guides.

---

# Features

- Upload a textbook PDF
- Automatic Table of Contents (TOC) detection
- Automatic chapter extraction
- Dynamic page mapping
- Recursive + Semantic Chunking
- Semantic search using FAISS
- Retrieval-Augmented Generation (RAG)
- Instructor guide generation using GPT-5.5
- Automatic lesson evaluation
- Hallucination detection
- Automatic lesson refinement
- PDF export
- MongoDB lesson storage
- Dockerized MongoDB deployment

---

# Project Pipeline

```
PDF
 │
 ▼
Text Extraction (PyPDFium2)
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
FAISS Vector Index
 │
 ▼
Semantic Retrieval (RAG)
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
 │
 ▼
MongoDB Storage
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
- MongoDB
- Docker
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

Linux / macOS

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

# MongoDB (Docker)

Start MongoDB using Docker.

```bash
docker compose up -d
```

Verify that the container is running.

```bash
docker ps
```

---

# OpenAI API Key

Create a `.env` file in the project root.

```text
OPENAI_API_KEY=your_api_key_here

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=lessonplan_ai
```

The application uses:

- GPT-5.5 for lesson generation
- GPT-5.5 for lesson refinement
- GPT-4o-mini for lesson evaluation
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

The pipeline validates:

- PDF extraction
- TOC parsing
- Chapter extraction
- Recursive + semantic chunking
- FAISS vector retrieval
- Lesson generation
- Lesson evaluation
- Automatic rewrite
- PDF generation
- MongoDB connectivity

---

# Lesson Evaluation

Every generated lesson is automatically evaluated.

The evaluator measures:

- Hallucination rate
- Coverage of textbook concepts
- Structural completeness
- Overall quality score

Quality thresholds:

- Maximum hallucination rate: **20%**
- Minimum coverage score: **80%**

If either threshold is not met, the lesson is automatically rewritten using the evaluator's feedback and evaluated again before being exported.

---

# Database

MongoDB stores:

- Uploaded textbooks
- Extracted chapters
- Generated lessons
- Lesson evaluations

This provides persistent storage and maintains a history of generated instructor guides without affecting the RAG pipeline.

---

# Current Version

Version 1.1

Implemented:

- Local PDF processing
- Automatic TOC parsing
- Dynamic chapter extraction
- Recursive + semantic chunking
- FAISS vector search
- Retrieval-Augmented Generation (RAG)
- GPT-5.5 lesson generation
- Automatic lesson evaluation
- Hallucination detection
- Automatic lesson refinement
- PDF export
- MongoDB integration
- Docker deployment

---

# Future Work

- Local embedding models
- Local language models
- FAISS index persistence
- Automatic figure and table extraction
- Citation-aware lesson generation
- Multi-chapter lesson generation
- Interactive instructor editing
- Lesson version comparison

---

# Authors

Clara Castro
Ebuka Onuoha

Capstone Project

Post-Degree Diploma in Data Analytics

Langara College
