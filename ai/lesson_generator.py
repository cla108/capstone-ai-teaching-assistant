from config import OPENAI_PROVIDER
from ai.llm import chat_completion


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
    teaching_style="Practical and interactive",
    difficulty="Intermediate",
    lesson_duration="90 minutes",
    output_type="Instructor Guide",
    include_activities=True,
    include_discussion=True,
    include_quiz=True,
    include_homework=False,
    include_case_study=True,
    provider=OPENAI_PROVIDER,
    ollama_model=None,
):
    """
    Generates instructor-ready teaching material from retrieved textbook
    context.

    Supports configurable lesson options and both OpenAI and Ollama
    providers through ai/llm.py.
    """

    textbook_context = build_context_from_chunks(retrieved_chunks)

    activities_instruction = (
        """
Create practical classroom activities based on the chapter.

For each activity, use this format:

Activity 1: Activity Name
Purpose:
Instructions:
Expected learning outcome:
"""
        if include_activities
        else """
Do not create classroom activities. In the Class Activities section,
state that activities were not requested.
"""
    )

    discussion_instruction = (
        """
Create analytical and application-based discussion questions based only
on the provided chapter content.
"""
        if include_discussion
        else """
Do not create discussion questions. In the Discussion Questions section,
state that discussion questions were not requested.
"""
    )

    quiz_instruction = (
        """
Create definition, concept, and application questions with answers.

Use this format:

Definition Questions

1. Question
Answer:

Concept Questions

2. Question
Answer:

Application Questions

3. Question
Answer:
"""
        if include_quiz
        else """
Do not create quiz questions. In the Quick Assessment / Quiz Questions
section, state that a quiz was not requested.
"""
    )

    homework_instruction = (
        """
Create a short homework or independent-learning task based only on the
provided chapter.

Include:

Homework title:
Purpose:
Instructions:
Expected submission:
"""
        if include_homework
        else """
Do not create a homework activity.
"""
    )

    case_study_instruction = (
        """
If the chapter includes a case study, include:

• Main issue
• Connection to chapter concepts
• Instructor questions
• Possible answer direction

If no case study is provided, state that no case study is included in
the retrieved chapter.
"""
        if include_case_study
        else """
Do not provide case study guidance. In the Case Study Guidance section,
state that case study guidance was not requested.
"""
    )

    prompt = f"""
You are an expert lecturer, curriculum designer, and teaching assistant.

Create a polished {output_type.lower()} from the provided textbook
chapter.

The material must help an instructor teach the chapter clearly,
practically, and efficiently.

Use only the provided chapter and retrieved context as the textbook
source.

You may use general teaching knowledge to improve explanations,
activities, sequencing, and classroom delivery. However, do not invent
textbook-specific facts, figures, tables, examples, cases, formulas,
models, page numbers, or references.

CHAPTER INFORMATION

Chapter Title/Number:
{selected_chapter}

Audience Difficulty Level:
{difficulty}

Lesson Duration:
{lesson_duration}

Teaching Style:
{teaching_style}

Output Type:
{output_type}

TEXTBOOK CHAPTER / RETRIEVED CONTEXT

{textbook_context}

INSTRUCTOR GUIDE REQUIREMENTS

Produce a polished, copy-and-paste-ready instructor guide with the
following sections.

1. Chapter Title

Provide the chapter number and title using the information supplied.

2. Chapter Objectives

Rewrite the chapter objectives clearly for students.

Adjust the wording and expected depth to the selected difficulty level:
{difficulty}.

If objectives are not explicitly provided, infer reasonable objectives
only from the supplied chapter content.

3. Chapter Overview

Briefly explain what the chapter covers and why it matters.

Keep the overview concise and appropriate for a {difficulty} audience.

4. Key Concepts and Teaching Notes

Break the chapter into major topics using lettered subheadings.

For each topic, include:

• A clear explanation of the concept
• What the instructor should emphasize
• Important terms, models, formulas, laws, frameworks, or processes
• Relevant textbook figures, tables, examples, formulas, boxed sections,
  or cases, if provided
• Practical suggestions for explaining the topic in class
• A level of explanation appropriate for {difficulty} learners

Do not add concepts that are not supported by the retrieved context.

5. Important Textbook References

List important figures, tables, examples, formulas, boxed sections, and
cases mentioned in the chapter.

Use this format:

Figure/Table/Example Name

What it shows:

How to use it:

Only include references that are supported by the supplied context.

If an item is mentioned but not visible in the retrieved context, state:

“The instructor may refer to this item if visible in the textbook.”

6. Suggested Lecture Flow

Create a timed lecture plan for a class lasting {lesson_duration}.

The complete sequence should fit within the selected lesson duration.

Use this format:

Time: 0–10 minutes

Topic:

Instructor action:

Student engagement/activity:

Include realistic time allocations for introduction, explanation,
examples, activities, assessment, and conclusion.

7. Class Activities

{activities_instruction}

Activities must match the selected difficulty level and teaching style.

8. Discussion Questions

{discussion_instruction}

Questions should encourage analysis, explanation, comparison, and
application rather than simple repetition.

9. Quick Assessment / Quiz Questions

{quiz_instruction}

Questions must reflect the chapter content and the selected difficulty
level.

Do not create questions about information that is absent from the
retrieved context.

10. Case Study Guidance

{case_study_instruction}

11. Common Student Misunderstandings

Identify likely confusing areas based on the chapter content.

For each misunderstanding:

• Explain the likely confusion
• Explain why students may misunderstand it
• Suggest how the instructor can clarify it

Do not claim that students commonly misunderstand something unless it is
a reasonable teaching inference from the supplied material.

12. Instructor Tips

Give practical advice for teaching the chapter effectively.

Adapt the recommendations to:

• Difficulty level: {difficulty}
• Lesson duration: {lesson_duration}
• Teaching style: {teaching_style}

13. Final Chapter Summary

Summarize the most important chapter takeaways.

Keep the summary concise, clear, and suitable for reviewing the lesson.

OPTIONAL HOMEWORK

{homework_instruction}

If homework is requested, place it after Section 13 under the heading:

Optional Homework

FORMATTING RULES

• Do not use Markdown heading symbols such as #, ##, or ###.
• Do not use Markdown bold symbols such as double asterisks.
• Do not use Markdown table formatting unless absolutely necessary.
• Use clean numbered section headings.
• Use lettered subheadings inside Section 4.
• Use bullet points with the symbol •.
• Keep paragraphs short and instructor-friendly.
• Use clear spacing between sections and subsections.
• Do not copy large textbook passages word-for-word.
• Summarize and transform the material into teaching content.
• Do not invent textbook-specific information.
• If information is missing from the retrieved context, explicitly state
  that it is not provided.
• The output must look like a professional teaching handout or instructor
  manual, not a conversational AI response.
• Do not mention prompts, retrieval systems, RAG, chunks, or the language
  model in the final document.

CONTENT RULES

• Use the supplied textbook context as the factual source.
• Do not invent figures, tables, examples, cases, formulas, or page
  numbers.
• Do not create textbook quotations unless the exact quotation appears in
  the context.
• Distinguish textbook information from general teaching suggestions.
• Keep the guide practical for real classroom delivery.
• Ensure the lecture plan fits within {lesson_duration}.
• Ensure explanations match the {difficulty} difficulty level.
• Follow the requested teaching style: {teaching_style}.

FINAL QUALITY CHECK

Before finalizing, confirm internally that:

• All 13 required sections are included.
• Optional sections follow the selected settings.
• Textbook references are based only on the provided context.
• The lecture flow fits within {lesson_duration}.
• The level of explanation matches {difficulty}.
• The guide is practical for classroom teaching.
• The formatting is clean and Word-ready.
• No Markdown heading symbols are present.
• No unsupported textbook-specific details are included.
"""

    return chat_completion(
        provider=provider,
        task="generation",
        system_prompt=(
            "You are a careful academic instructional design assistant. "
            "Follow the supplied textbook context closely and never invent "
            "textbook-specific information."
        ),
        user_prompt=prompt,
        ollama_model=ollama_model,
        temperature=0.3,
    )
