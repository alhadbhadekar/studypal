import os
from dotenv import load_dotenv
from vectorize_book import vectorize_book_and_store_to_db, vectorize_chapters

load_dotenv()
CLASS_SUBJECT_NAME = os.getenv("CLASS_SUBJECT_NAME")

vectorize_book_and_store_to_db(
    class_subject_name=CLASS_SUBJECT_NAME,
    vector_db_name="book_vector_db"
)

vectorize_chapters(class_subject_name=CLASS_SUBJECT_NAME)