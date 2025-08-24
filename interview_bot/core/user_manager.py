# core/user_manager.py
from typing import Dict, List, Optional
from database.models import DatabaseManager
from config.settings import Config

class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.config = Config()
    
    def create_user_profile(self, name: str, email: str, domain: str, 
                           experience_level: str) -> Dict:
        """Create a new user profile"""
        if domain not in self.config.SUPPORTED_DOMAINS:
            raise ValueError(f"Domain '{domain}' not supported. Choose from: {self.config.SUPPORTED_DOMAINS}")
        
        if experience_level not in ["Beginner", "Intermediate", "Advanced"]:
            raise ValueError("Experience level must be: Beginner, Intermediate, or Advanced")
        
        try:
            user_id = self.db.create_user(name, email, domain, experience_level)
            return {
                "user_id": user_id,
                "name": name,
                "email": email,
                "domain": domain,
                "experience_level": experience_level,
                "status": "success"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile by ID"""
        return self.db.get_user(user_id)
    
    def get_user_analytics(self, user_id: int) -> Dict:
        """Get comprehensive user analytics"""
        progress = self.db.get_user_progress(user_id)
        
        if not progress:
            return {
                "total_sessions": 0,
                "average_score": 0.0,
                "improvement_trend": "No data",
                "strong_areas": [],
                "areas_for_improvement": []
            }
        
        # Calculate metrics
        total_sessions = len(progress)
        scores = [p.get('session_avg_score', 0) for p in progress if p.get('session_avg_score')]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Calculate improvement trend
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / len(scores[-3:])  # Last 3 sessions
            early_avg = sum(scores[:3]) / len(scores[:3])     # First 3 sessions
            trend = "Improving" if recent_avg > early_avg else "Needs Focus"
        else:
            trend = "Insufficient data"
        
        return {
            "total_sessions": total_sessions,
            "average_score": round(average_score, 2),
            "improvement_trend": trend,
            "recent_sessions": progress[:5],  # Last 5 sessions
            "score_history": scores
        }
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> Dict:
        """Update user preferences and settings"""
        # This would typically update preferences in the database
        # For now, we'll return a success response
        return {
            "status": "success",
            "message": "Preferences updated successfully",
            "preferences": preferences
        }
    
    def get_personalized_recommendations(self, user_id: int) -> List[str]:
        """Get personalized recommendations based on user performance"""
        analytics = self.get_user_analytics(user_id)
        recommendations = []
        
        if analytics["average_score"] < 0.6:
            recommendations.extend([
                "Focus on structuring your answers using the STAR method (Situation, Task, Action, Result)",
                "Practice explaining technical concepts in simple terms",
                "Work on providing specific examples from your experience"
            ])
        
        if analytics["total_sessions"] < 3:
            recommendations.append("Continue regular practice to build confidence")
        
        if analytics["improvement_trend"] == "Needs Focus":
            recommendations.append("Review feedback from previous sessions and work on identified weak areas")
        
        return recommendations if recommendations else ["Keep up the great work! Continue practicing regularly."]

# core/__init__.py
from .user_manager import UserManager

__all__ = ['UserManager']