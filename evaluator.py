import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_context_from_chunks(chunks):
    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"""
SOURCE CHUNK {chunk["chunk_id"]}
Chapter: {chunk["chapter_number"]} - {chunk["chapter_title"]}
Pages: {chunk["start_page"]} to {chunk["end_page"]}

{chunk["text"]}
"""
        )

    return "\n\n".join(context_parts)


def evaluate_lesson(
    instructor_guide,
    retrieved_chunks,
    model="gpt-4o-mini"
):
    """
    Evaluates generated lesson for:
    - hallucination / grounding
    - coverage
    - structure
    """

    context = build_context_from_chunks(retrieved_chunks)

    prompt = f"""
You are evaluating an AI-generated instructor guide.

Compare the generated instructor guide against the retrieved textbook content.

Important:
- The retrieved textbook chunks are the only factual source.
- Do not judge based on external knowledge.
- Be strict but fair.

Evaluate the guide using these criteria:

1. Hallucination / Grounding
Check whether factual claims in the guide are supported by the source chunks.

2. Coverage
Check whether the guide covers the major concepts present in the retrieved chunks.

3. Structure
Check whether the guide includes these required sections:
- Chapter Title
- Learning Objectives
- Chapter Overview
- Key Concepts and Teaching Notes
- Suggested Lecture Flow
- Common Student Misunderstandings
- Instructor Tips
- Final Chapter Summary

Return ONLY valid JSON with this structure:

{{
  "total_factual_claims": 0,
  "supported_claims": 0,
  "partially_supported_claims": 0,
  "unsupported_claims": 0,
  "hallucination_rate": 0.0,
  "coverage_score": 0.0,
  "structure_score": 0.0,
  "overall_score": 0.0,
  "missing_concepts": [],
  "unsupported_claim_examples": [],
  "feedback": ""
}}

RETRIEVED TEXTBOOK CONTENT:
{context}

GENERATED INSTRUCTOR GUIDE:
{instructor_guide}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a strict academic content evaluator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw_output = response.choices[0].message.content

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "total_factual_claims": None,
            "supported_claims": None,
            "partially_supported_claims": None,
            "unsupported_claims": None,
            "hallucination_rate": None,
            "coverage_score": None,
            "structure_score": None,
            "overall_score": None,
            "missing_concepts": [],
            "unsupported_claim_examples": [],
            "feedback": raw_output
        }


def rewrite_lesson_if_needed(
    instructor_guide,
    retrieved_chunks,
    evaluation,
    model="gpt-5.5",
    hallucination_threshold=0.20,
    coverage_threshold=0.80
):
    """
    Rewrites the lesson if hallucination is too high or coverage is too low.
    """

    hallucination_rate = evaluation.get("hallucination_rate")
    coverage_score = evaluation.get("coverage_score")

    needs_rewrite = False

    if hallucination_rate is not None and hallucination_rate > hallucination_threshold:
        needs_rewrite = True

    if coverage_score is not None and coverage_score < coverage_threshold:
        needs_rewrite = True

    if not needs_rewrite:
        return instructor_guide, False

    context = build_context_from_chunks(retrieved_chunks)

    prompt = f"""
Rewrite the instructor guide using the evaluator feedback.

Rules:
- Use only the retrieved textbook content.
- Remove unsupported claims.
- Improve coverage of missing concepts.
- Keep the same required structure.
- Do not add external examples or textbook-specific facts that are not in the chunks.

EVALUATOR FEEDBACK:
{evaluation}

RETRIEVED TEXTBOOK CONTENT:
{context}

ORIGINAL INSTRUCTOR GUIDE:
{instructor_guide}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a careful academic lesson editor."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content, True
