#!/usr/bin/env python3
"""
Test if lesson generation works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")
try:
    from services.lesson_service import generate_complete_lesson
    print("✅ generate_complete_lesson imported")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Create a minimal test chapter
test_chapter = {
    "chapter_number": 1,
    "chapter_title": "Test Chapter",
    "text": "This is a test chapter content. It has some words for testing.",
    "start_page": 1,
    "end_page": 2,
    "sections": []
}

print("\nTesting lesson generation with mock data...")
try:
    result = generate_complete_lesson(
        selected_chapter=test_chapter,
        provider="openai",  # or "ollama" if you're using that
        teaching_style="Practical",
        difficulty="Intermediate",
        lesson_duration="60 minutes",
        output_type="Instructor Guide",
        include_activities=True,
        include_discussion=True,
        include_quiz=True,
        include_homework=False,
        include_case_study=True
    )
    
    lesson = result.get("lesson", "")
    print(f"\n✅ Lesson generated!")
    print(f"Lesson length: {len(lesson)} characters")
    print(f"First 200 characters: {lesson[:200] if lesson else 'EMPTY'}")
    print(f"Chunks created: {len(result.get('chunks', []))}")
    print(f"Chunks retrieved: {len(result.get('retrieved_chunks', []))}")
    
except Exception as e:
    print(f"❌ Generation failed: {e}")
    import traceback
    traceback.print_exc()
