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


def generate_instructor_guide(
    selected_chapter,
    retrieved_chunks,
    difficulty_level="Undergraduate Year 1",
    lecture_duration="90 minutes",
    model="gpt-4.1-mini"
):
    context = build_context_from_chunks(retrieved_chunks)

    prompt = f"""
You are creating condensed instructor teaching notes based on a textbook chapter.

This is NOT a quiz.
This is NOT an activity plan.
This is NOT a lecture flow.
This is NOT a list of discussion questions.

Your goal:
Rewrite the chapter into a shorter, clearer instructor-facing guide.

Rules:
- Use ONLY the provided textbook content.
- Do NOT add external facts.
- Do NOT invent examples.
- Do NOT include quizzes, activities, or assessments.
- Preserve the major ideas from the chapter.
- Explain complex concepts clearly and directly.
- Use a professional academic tone.
- Follow the output schema exactly.

Selected chapter:
Chapter {selected_chapter["chapter_number"]}: {selected_chapter["chapter_title"]}
Textbook pages: {selected_chapter["start_page"]} to {selected_chapter["end_page"]}

Target level: {difficulty_level}
Suggested duration: {lecture_duration}

SOURCE CHUNKS:
{context}

Output schema:

# Instructor Guide

## Chapter Information
- Chapter:
- Title:
- Textbook pages:
- Target level:
- Suggested duration:

## Learning Objectives
Write 4 to 6 learning objectives based only on the chapter content.

## Chapter Overview
Write a short overview of the chapter and its purpose.

## Detailed Summary
Write a clear narrative summary of the chapter content.
The summary should be much shorter than the original chapter, but detailed enough for an instructor to teach from.
Break down complex ideas in a straightforward way.

## Figures, Images, and Tables
Attach extracted boxed objects from the chapter.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a careful instructional design assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
