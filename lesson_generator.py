import os

from dotenv import load_dotenv
from openai import OpenAI

from example_loader import load_human_examples


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_context_from_chunks(chunks):
    """
    Converts retrieved textbook chunks into source context for the LLM.
    """

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
    model="gpt-5.5"
):
    """
    Generates long-form instructor teaching notes using:
    - textbook chunks as factual source
    - human lesson examples as style guide
    """

    textbook_context = build_context_from_chunks(retrieved_chunks)
    human_examples = load_human_examples()

    prompt = f"""
You are an expert lecturer and curriculum designer.

Your task is to create instructor-ready teaching notes from the selected textbook chapter.

The guide should help an instructor teach the chapter clearly, practically, and efficiently.
It should be detailed enough to teach from, but not unnecessarily long.

Important source rules:
- HUMAN EXAMPLES are only for style, structure, tone, and level of detail.
- SOURCE CHUNKS are the only factual source for the new lesson.
- Do not copy textbook sections word-for-word.
- Do not invent textbook-specific facts, figures, tables, examples, cases, formulas, or page numbers.
- Do not include images or tables for now.

Selected chapter:
Chapter {selected_chapter["chapter_number"]}: {selected_chapter["chapter_title"]}
Textbook pages: {selected_chapter["start_page"]} to {selected_chapter["end_page"]}

HUMAN-WRITTEN LESSON EXAMPLES:
{human_examples}

SOURCE CHUNKS:
{textbook_context}

Create the instructor guide using this structure:

1. Chapter Title

2. Learning Objectives
Rewrite 6 to 10 learning objectives clearly for students.

3. Chapter Overview
Give a detailed overview of the chapter and why it matters.

4. Key Concepts and Teaching Notes
Break the chapter into major topics.
For each topic:
• Explain the concept clearly.
• State what the instructor should emphasize.
• Mention important terms, models, formulas, laws, frameworks, or processes only if they appear in the source chunks.
• Suggest how the instructor should explain it in class.

5. Suggested Lecture Flow
Create a timed lecture plan for a standard 90-minute class.
Use this format:
Time:
Topic:
Instructor action:
Student engagement:

6. Common Student Misunderstandings
Identify likely confusing areas and explain how the instructor can clarify them.
Only use misunderstandings that logically follow from the provided content.

7. Instructor Tips
Give practical advice for teaching the chapter effectively.

8. Final Chapter Summary
Summarize the most important takeaways.

Formatting rules:
- Do not use Markdown heading symbols like # or ##.
- Do not use Markdown tables.
- Use clean numbered section headings.
- Use bullet points where helpful.
- Keep paragraphs short and readable.
- The final output should look like a polished instructor handout.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a careful academic instructional design assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

    )

    return response.choices[0].message.content
