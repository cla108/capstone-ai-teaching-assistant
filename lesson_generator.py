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
    teaching_style = "Practical and interactive",
    model="gpt-5.5"
):
    """
    Generates long-form instructor teaching notes using:
    - textbook chunks as factual source
    - human lesson examples as style guide
    """

    textbook_context = build_context_from_chunks(retrieved_chunks)
    #human_examples = load_human_examples()

    prompt = f"""
You are an expert lecturer, curriculum designer, and teaching assistant. 

Your task is to create an instructor-ready teaching guide from the textbook chapter provided. 

The guide should help an instructor teach the chapter clearly, practically, and efficiently. It should be detailed enough to teach from, but not unnecessarily long. 

Use ONLY the provided textbook chapter/context as the main source. You may use general teaching knowledge to improve explanations and activities, but do not invent textbook-specific facts. 

If the textbook includes figures, tables, examples, cases, formulas, or study questions, reference them directly and explain how the instructor should use them. 

Examples: Use Figure 3-1 to explain the framework. Refer to Table 3-2 when discussing the data. Use Example 3-1 to demonstrate the concept. Use the case study at the end of the chapter for class discussion. 

Do not copy large sections of the textbook word-for-word. Summarize and transform the content into teaching material. 

CHAPTER INFORMATION: 

Chapter Title/Number: {selected_chapter}  

Teaching Style: {teaching_style} 

TEXTBOOK CHAPTER/RETRIEVED CONTEXT: 

{textbook_context} 

Create the instructor guide using this structure: 

1. Chapter Title 

2. Chapter Objectives. Rewrite the learning objectives clearly for students. 

3. Chapter Overview Give a concise overview of the chapter and why it matters. 

4. Key Concepts and Teaching Notes Break the chapter into major topics. 

For each topic: • Explain the concept clearly. • State what the instructor should emphasize. • Mention important terms, models, formulas, laws, frameworks, or processes. • Reference relevant textbook figures, tables, examples, or cases where available. • Suggest how the instructor should explain it in class. 

5. Important Textbook References List important figures, tables, examples, formulas, boxed sections, and cases found in the chapter. 

For each one, include: Name: What it shows: How the instructor should use it: 

6. Suggested Lecture Flow Create a timed lecture plan for. 

Use this format: Time: Topic: Instructor action: Student engagement/activity: 

7. Class Activities Create practical activities based on the chapter. 

For each activity: Activity name: Purpose: Instructions: Expected learning outcome: 

Discussion Questions Create discussion questions that encourage analysis and application. 

Quick Assessment / Quiz Questions Create quiz questions with answers. 

Include: • Definition questions • Concept questions • Application questions 

10. Case Study Guidance If the chapter includes a case study: • Identify the main issue. • Connect it to chapter concepts. • Suggest instructor questions. • Provide possible answer direction. 

Common Student Misunderstandings Identify confusing areas and explain how the instructor can clarify them. 

Instructor Tips Give practical advice for teaching the chapter effectively. 

Final Chapter Summary Summarize the most important takeaways. 

𝐅𝐎𝐑𝐌𝐀𝐓𝐓𝐈𝐍𝐆 𝐑𝐔𝐋𝐄𝐒 — 𝐌𝐔𝐒𝐓 𝐅𝐎𝐋𝐋𝐎𝐖 

The output must look like a polished, copy-and-paste-ready Word document. 

Do not use Markdown heading symbols such as #, ##, or ###. 

Do not use Markdown bold symbols such as bold. 

Do not use Markdown table formatting unless absolutely necessary. 

Use clean numbered section headings, such as: 

Chapter Title 

Chapter Objectives 

Chapter Overview 

Make major section headings visually clear by using bold-style text where possible


Use lettered subheadings for major topics inside Section 4


Use simple bullet points with the bullet symbol: 

• First point • Second point • Third point 

Use clear spacing between sections and subsections. 

Avoid dense paragraphs. Break long content into short, readable paragraphs. 

When listing textbook references, use this format: 

Figure/Table/Example Name What it shows: How to use it: 

For lecture flow, use this format instead of tables: 

Time: 0 –10 minutes Topic: Introduction Instructor action: Explain the importance of the topic. Student engagement: Ask students an opening question. 

For activities, use this format: 

Activity 1: Activity Name Purpose: Instructions: Expected learning outcome: 

For quiz questions, use this format: 

Definition Questions 

Question Answer: 

Question Answer: 

Concept Questions 

3. Question Answer: 

Application Questions 

4. Question Answer: 

Maintain a professional, clean, instructor-friendly tone. 

The final output should resemble a teaching handout or instructor manual, not a chat response. 

𝐂𝐎𝐍𝐓𝐄𝐍𝐓 𝐑𝐔𝐋𝐄𝐒 

Keep the tone professional, clear, and instructor-friendly. 

Do not produce a textbook rewrite. 

Do not invent figures, tables, examples, cases, page numbers, or textbook-specific facts. 

If a figure, table, example, or case is mentioned but not fully visible, say: 

“The instructor may refer to this item if visible in the textbook.” 

If information is missing, say it is not provided in the retrieved chapter. 

Use headings, subheadings, bullets, and spacing for readability. 

Make the output practical for real classroom teaching. 

Before finalizing the answer, check that:  

• The document has all 13 required sections.  

• The formatting is clean and Word-ready.  

• There are no Markdown heading symbols.  

• There are no unnecessary asterisks.  

• Textbook references are only based on the provided chapter/context.  

• The lecture flow matches.

• The guide is practical for an instructor to teach from
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
