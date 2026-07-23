#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("Testing lesson generation...")
print(f"Provider: {os.getenv('MODEL_PROVIDER', 'Not set')}")

try:
    from services.lesson_service import generate_complete_lesson
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test chapter
test_chapter = {
    "chapter_number": 1,
    "chapter_title": "Test Chapter",
    "text": "This is a test chapter content for debugging.",
    "start_page": 1,
    "end_page": 2,
    "sections": []
}

print("\nGenerating lesson...")
try:
    result = generate_complete_lesson(
        selected_chapter=test_chapter,
        provider="OpenAI",
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
    print(f"\n✅ SUCCESS!")
    print(f"Lesson length: {len(lesson)} characters")
    print(f"Preview: {lesson[:300] if lesson else 'EMPTY'}...")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
