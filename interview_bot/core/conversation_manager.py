# core/conversation_manager.py
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sqlite3
from database.models import DatabaseManager
from .question_generator import QuestionGenerator
from .answer_evaluator import AnswerEvaluator
from config.settings import Config

class ConversationManager:
    """Manages the flow of interview conversations"""
    
    def __init__(self):
        self.config = Config()
        self.db = DatabaseManager()
        self.question_generator = QuestionGenerator()
        self.answer_evaluator = AnswerEvaluator()
        
        # Session state
        self.current_sessions = {}  # Store active sessions
    
    def start_interview_session(self, user_id: int, domain: str, 
                               job_description: str = "", 
                               session_preferences: Dict = None) -> Dict:
        """Start a new interview session"""
        
        if session_preferences is None:
            session_preferences = {
                "num_questions": 5,
                "question_types": ["technical", "behavioral", "situational"],
                "difficulty_progression": True
            }
        
        # Create session in database
        session_id = self.db.create_session(user_id, domain)
        
        # Get user profile for personalization
        user_profile = self.db.get_user(user_id)
        if not user_profile:
            return {"status": "error", "message": "User not found"}
        
        # Generate initial questions
        questions = self.question_generator.generate_questions(
            domain=domain,
            experience_level=user_profile["experience_level"],
            job_description=job_description,
            num_questions=session_preferences["num_questions"],
            question_types=session_preferences["question_types"]
        )
        
        # Save questions to database
        for question in questions:
            question_id = self.db.save_question(
                session_id=session_id,
                question_text=question["question"],
                question_type=question["type"],
                difficulty_level=question["difficulty"],
                expected_keywords=json.dumps(question["expected_keywords"])
            )
            question["db_id"] = question_id
        
        # Initialize session state
        session_state = {
            "session_id": session_id,
            "user_id": user_id,
            "domain": domain,
            "questions": questions,
            "current_question_index": 0,
            "answers": [],
            "evaluations": [],
            "start_time": datetime.now(),
            "session_preferences": session_preferences,
            "status": "active"
        }
        
        self.current_sessions[session_id] = session_state
        
        return {
            "status": "success",
            "session_id": session_id,
            "first_question": questions[0] if questions else None,
            "total_questions": len(questions),
            "session_info": {
                "domain": domain,
                "user_name": user_profile["name"],
                "experience_level": user_profile["experience_level"]
            }
        }
    
    def process_answer(self, session_id: int, answer: str) -> Dict:
        """Process user answer and provide feedback"""
        
        if session_id not in self.current_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.current_sessions[session_id]
        current_index = session["current_question_index"]
        
        if current_index >= len(session["questions"]):
            return {"status": "error", "message": "No more questions in session"}
        
        current_question = session["questions"][current_index]
        
        # Evaluate the answer
        evaluation = self.answer_evaluator.evaluate_answer(current_question, answer)
        
        # Save answer and evaluation to database
        self.db.save_answer(
            question_id=current_question["db_id"],
            user_answer=answer,
            semantic_score=evaluation["semantic_score"],
            keyword_score=evaluation["keyword_score"],
            structure_score=evaluation["structure_score"],
            overall_score=evaluation["overall_score"],
            feedback=evaluation["feedback"]
        )
        
        # Update session state
        session["answers"].append({
            "question_id": current_question["id"],
            "answer": answer,
            "timestamp": datetime.now()
        })
        session["evaluations"].append(evaluation)
        session["current_question_index"] += 1
        
        # Determine next action
        if session["current_question_index"] < len(session["questions"]):
            # Get next question
            next_question = session["questions"][session["current_question_index"]]
            
            # Generate follow-up question if needed
            followup_question = None
            if evaluation["overall_score"] < 0.5:  # Poor answer
                followup_question = self.question_generator.generate_followup_question(
                    current_question["question"], answer, evaluation["overall_score"]
                )
            
            return {
                "status": "question_answered",
                "evaluation": evaluation,
                "next_question": next_question,
                "followup_question": followup_question,
                "progress": {
                    "current": session["current_question_index"],
                    "total": len(session["questions"]),
                    "percentage": (session["current_question_index"] / len(session["questions"])) * 100
                }
            }
        else:
            # Session completed
            return self._complete_session(session_id)
    
    def _complete_session(self, session_id: int) -> Dict:
        """Complete the interview session and provide summary"""
        
        session = self.current_sessions[session_id]
        
        # Calculate session metrics
        session_metrics = self.answer_evaluator.calculate_session_metrics(session["evaluations"])
        
        # Update session in database
        end_time = datetime.now()
        duration = (end_time - session["start_time"]).total_seconds()
        
        # Generate comprehensive feedback
        comprehensive_feedback = self._generate_session_feedback(session, session_metrics)
        
        # Update session status
        session["status"] = "completed"
        session["end_time"] = end_time
        session["duration"] = duration
        session["final_metrics"] = session_metrics
        
        return {
            "status": "session_completed",
            "session_summary": {
                "total_questions": len(session["questions"]),
                "average_score": session_metrics["session_average"],
                "duration_minutes": round(duration / 60, 1),
                "strongest_area": session_metrics["strongest_area"],
                "weakest_area": session_metrics["weakest_area"],
                "performance_level": self._get_overall_performance_level(session_metrics["session_average"])
            },
            "detailed_metrics": session_metrics,
            "comprehensive_feedback": comprehensive_feedback,
            "recommendations": self._generate_recommendations(session, session_metrics)
        }
    
    def _generate_session_feedback(self, session: Dict, metrics: Dict) -> str:
        """Generate comprehensive session feedback"""
        
        feedback_parts = []
        
        # Overall performance
        avg_score = metrics["session_average"]
        if avg_score >= 0.8:
            feedback_parts.append("Excellent performance! You demonstrated strong knowledge and communication skills.")
        elif avg_score >= 0.6:
            feedback_parts.append("Good job overall! You showed solid understanding with room for improvement.")
        elif avg_score >= 0.4:
            feedback_parts.append("Fair performance. Focus on the areas highlighted below for improvement.")
        else:
            feedback_parts.append("This session highlighted several areas for development. Use this as a learning opportunity.")
        
        # Strengths and weaknesses
        feedback_parts.append(f"Your strongest area was {metrics['strongest_area'].lower()}.")
        if metrics["weakest_area"] != metrics["strongest_area"]:
            feedback_parts.append(f"Focus on improving {metrics['weakest_area'].lower()}.")
        
        # Specific insights
        evaluations = session["evaluations"]
        if evaluations:
            high_scoring = [e for e in evaluations if e["overall_score"] >= 0.7]
            if high_scoring:
                feedback_parts.append(f"You performed well on {len(high_scoring)} out of {len(evaluations)} questions.")
        
        return " ".join(feedback_parts)
    
    def _generate_recommendations(self, session: Dict, metrics: Dict) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Based on performance areas
        if metrics["semantic_average"] < 0.6:
            recommendations.append("Practice answering questions more directly and relevantly to what's being asked.")
        
        if metrics["keyword_average"] < 0.6:
            recommendations.append("Study technical terminology and concepts specific to your domain.")
        
        if metrics["structure_average"] < 0.6:
            recommendations.append("Work on structuring your answers using frameworks like STAR (Situation, Task, Action, Result).")
        
        # Based on question types
        question_type_scores = {}
        for i, evaluation in enumerate(session["evaluations"]):
            question_type = session["questions"][i]["type"]
            if question_type not in question_type_scores:
                question_type_scores[question_type] = []
            question_type_scores[question_type].append(evaluation["overall_score"])
        
        for q_type, scores in question_type_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.5:
                if q_type == "technical":
                    recommendations.append("Focus on technical concepts and hands-on practice in your domain.")
                elif q_type == "behavioral":
                    recommendations.append("Prepare specific examples from your experience using the STAR method.")
                elif q_type == "situational":
                    recommendations.append("Practice thinking through hypothetical scenarios systematically.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Continue practicing regularly to maintain and improve your interview skills.")
        
        recommendations.append("Review the detailed feedback for each question to understand specific areas for improvement.")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_overall_performance_level(self, score: float) -> str:
        """Get performance level description"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def get_session_status(self, session_id: int) -> Optional[Dict]:
        """Get current session status"""
        # First check in-memory sessions
        if session_id in self.current_sessions:
            return self.current_sessions[session_id]
        
        # If not in memory, try to restore from database
        try:
            session_data = self._restore_session_from_db(session_id)
            if session_data:
                self.current_sessions[session_id] = session_data
                return session_data
        except Exception as e:
            print(f"Error restoring session {session_id}: {e}")
        
        return None
    
    def _restore_session_from_db(self, session_id: int) -> Optional[Dict]:
        """Restore session data from database"""
        try:
            # Get session info from database
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Get session basic info
                cursor.execute("""
                    SELECT s.*, u.name, u.experience_level 
                    FROM sessions s 
                    JOIN users u ON s.user_id = u.id 
                    WHERE s.id = ?
                """, (session_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
                    return None
                
                # Get questions for this session
                cursor.execute("""
                    SELECT * FROM questions WHERE session_id = ? ORDER BY id
                """, (session_id,))
                
                question_rows = cursor.fetchall()
                if not question_rows:
                    return None
                
                # Convert to expected format
                questions = []
                for row in question_rows:
                    questions.append({
                        "id": row[0],
                        "db_id": row[0],
                        "question": row[2],
                        "type": row[3],
                        "difficulty": row[4],
                        "expected_keywords": json.loads(row[5]) if row[5] else []
                    })
                
                # Get answered questions to determine current position
                cursor.execute("""
                    SELECT q.id FROM questions q
                    JOIN answers a ON q.id = a.question_id
                    WHERE q.session_id = ?
                    ORDER BY a.answered_at
                """, (session_id,))
                
                answered_questions = [row[0] for row in cursor.fetchall()]
                current_question_index = len(answered_questions)
                
                # Reconstruct session state
                session_state = {
                    "session_id": session_id,
                    "user_id": session_row[1],
                    "domain": session_row[3],
                    "questions": questions,
                    "current_question_index": current_question_index,
                    "answers": [],  # Could restore these too if needed
                    "evaluations": [],  # Could restore these too if needed
                    "start_time": datetime.now(),  # Approximate
                    "session_preferences": {
                        "num_questions": len(questions),
                        "question_types": list(set([q["type"] for q in questions])),
                        "difficulty_progression": True
                    },
                    "status": "active" if current_question_index < len(questions) else "completed"
                }
                
                return session_state
                
        except Exception as e:
            print(f"Error restoring session from database: {e}")
            return None
    
    def pause_session(self, session_id: int) -> Dict:
        """Pause an active session"""
        if session_id not in self.current_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.current_sessions[session_id]
        session["status"] = "paused"
        session["pause_time"] = datetime.now()
        
        return {"status": "success", "message": "Session paused"}
    
    def resume_session(self, session_id: int) -> Dict:
        """Resume a paused session"""
        if session_id not in self.current_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.current_sessions[session_id]
        if session["status"] != "paused":
            return {"status": "error", "message": "Session is not paused"}
        
        session["status"] = "active"
        
        # Get current question
        current_index = session["current_question_index"]
        if current_index < len(session["questions"]):
            current_question = session["questions"][current_index]
            return {
                "status": "success",
                "current_question": current_question,
                "progress": {
                    "current": current_index,
                    "total": len(session["questions"])
                }
            }
        else:
            return {"status": "error", "message": "No more questions in session"}
    
    def end_session_early(self, session_id: int) -> Dict:
        """End session before all questions are answered"""
        if session_id not in self.current_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.current_sessions[session_id]
        
        if session["evaluations"]:
            # Generate partial summary
            partial_metrics = self.answer_evaluator.calculate_session_metrics(session["evaluations"])
            session["status"] = "ended_early"
            
            return {
                "status": "session_ended_early",
                "partial_summary": {
                    "questions_answered": len(session["evaluations"]),
                    "total_questions": len(session["questions"]),
                    "average_score": partial_metrics["session_average"]
                },
                "message": "Session ended early. You can review your progress and continue practicing."
            }
        else:
            session["status"] = "cancelled"
            return {"status": "session_cancelled", "message": "Session cancelled with no answers recorded."}

# Update core/__init__.py
from .user_manager import UserManager
from .question_generator import QuestionGenerator
from .answer_evaluator import AnswerEvaluator
from .conversation_manager import ConversationManager

__all__ = ['UserManager', 'QuestionGenerator', 'AnswerEvaluator', 'ConversationManager']