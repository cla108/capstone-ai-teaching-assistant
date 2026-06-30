import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class DatabaseManager:

    def __init__(self):

        self.client = MongoClient(
            os.getenv("MONGO_URI")
        )

        self.db = self.client[
            os.getenv("MONGO_DB_NAME")
        ]

        self.textbooks = self.db["textbooks"]
        self.chapters = self.db["chapters"]
        self.lessons = self.db["lessons"]
        self.evaluations = self.db["evaluations"]

    ####################################################
    # TEXTBOOKS
    ####################################################

    def get_textbook(self, filename):

        return self.textbooks.find_one({
            "filename": filename
        })

    def save_textbook(
        self,
        filename,
        total_pages,
        total_chapters
    ):

        existing = self.get_textbook(filename)

        if existing:
            return existing["_id"]

        result = self.textbooks.insert_one({

            "filename": filename,

            "total_pages": total_pages,

            "total_chapters": total_chapters,

            "uploaded_at": datetime.utcnow()

        })

        return result.inserted_id

    ####################################################
    # CHAPTERS
    ####################################################

    def get_chapter(
        self,
        textbook_id,
        chapter_number
    ):

        return self.chapters.find_one({

            "textbook_id": textbook_id,

            "chapter_number": chapter_number

        })

    def save_chapter(
        self,
        textbook_id,
        chapter
    ):

        existing = self.get_chapter(

            textbook_id,

            chapter["chapter_number"]

        )

        if existing:
            return existing["_id"]

        result = self.chapters.insert_one({

            "textbook_id": textbook_id,

            "chapter_number": chapter["chapter_number"],

            "chapter_title": chapter["chapter_title"],

            "start_page": chapter["start_page"],

            "end_page": chapter["end_page"],

            "created_at": datetime.utcnow()

        })

        return result.inserted_id

    ####################################################
    # LESSONS
    ####################################################

    def save_lesson(

        self,

        chapter_id,

        instructor_guide,

        output_path,

        generation_model

    ):

        result = self.lessons.insert_one({

            "chapter_id": chapter_id,

            "lesson": instructor_guide,

            "generation_model": generation_model,

            "pdf_path": output_path,

            "created_at": datetime.utcnow()

        })

        return result.inserted_id

    ####################################################
    # EVALUATIONS
    ####################################################

    def save_evaluation(

        self,

        lesson_id,

        evaluation

    ):

        evaluation["lesson_id"] = lesson_id

        evaluation["created_at"] = datetime.utcnow()

        self.evaluations.insert_one(
            evaluation
        )
