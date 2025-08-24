# database/models.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "interview_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    domain TEXT NOT NULL,
                    experience_level TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    domain TEXT NOT NULL,
                    questions_asked INTEGER DEFAULT 0,
                    avg_score REAL DEFAULT 0.0,
                    session_duration INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    difficulty_level TEXT NOT NULL,
                    expected_keywords TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Answers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER,
                    user_answer TEXT NOT NULL,
                    semantic_score REAL,
                    keyword_score REAL,
                    structure_score REAL,
                    overall_score REAL,
                    feedback TEXT,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES questions (id)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, name: str, email: str, domain: str, experience_level: str) -> int:
        """Create a new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, domain, experience_level)
                VALUES (?, ?, ?, ?)
            ''', (name, email, domain, experience_level))
            return cursor.lastrowid
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def create_session(self, user_id: int, domain: str) -> int:
        """Create a new interview session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (user_id, domain)
                VALUES (?, ?)
            ''', (user_id, domain))
            return cursor.lastrowid
    
    def save_question(self, session_id: int, question_text: str, 
                     question_type: str, difficulty_level: str, 
                     expected_keywords: str = "") -> int:
        """Save a question to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO questions (session_id, question_text, question_type, 
                                     difficulty_level, expected_keywords)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, question_text, question_type, difficulty_level, expected_keywords))
            return cursor.lastrowid
    
    def save_answer(self, question_id: int, user_answer: str, 
                   semantic_score: float, keyword_score: float, 
                   structure_score: float, overall_score: float, 
                   feedback: str) -> int:
        """Save user answer and evaluation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO answers (question_id, user_answer, semantic_score, 
                                   keyword_score, structure_score, overall_score, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (question_id, user_answer, semantic_score, keyword_score, 
                  structure_score, overall_score, feedback))
            return cursor.lastrowid
    
    def get_user_progress(self, user_id: int) -> List[Dict]:
        """Get user's session history and progress"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.*, AVG(a.overall_score) as session_avg_score
                FROM sessions s
                LEFT JOIN questions q ON s.id = q.session_id
                LEFT JOIN answers a ON q.id = a.question_id
                WHERE s.user_id = ?
                GROUP BY s.id
                ORDER BY s.session_date DESC
            ''', (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
