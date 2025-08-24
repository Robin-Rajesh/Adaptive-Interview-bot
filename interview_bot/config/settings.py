# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Database
    DATABASE_PATH = "interview_bot.db"
    
    # Model Settings
    GROQ_MODEL = "llama3-8b-8192"  # Fast and capable model for interview questions
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Evaluation Thresholds
    SIMILARITY_THRESHOLD = 0.7
    MIN_ANSWER_LENGTH = 10
    MAX_QUESTIONS_PER_SESSION = 10
    
    # Domains
    SUPPORTED_DOMAINS = [
        "Software Engineering",
        "Data Science",
        "Product Management",
        "Marketing",
        "Finance",
        "Human Resources",
        "Sales",
        "Design"
    ]

