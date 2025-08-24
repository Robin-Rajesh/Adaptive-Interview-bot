# core/question_generator.py
from groq import Groq
import json
import random
from typing import List, Dict, Optional
from config.settings import Config

class QuestionGenerator:
    def __init__(self):
        self.config = Config()
        self.client = Groq(api_key=self.config.GROQ_API_KEY)
        
        # Question templates by type
        self.question_templates = {
            "technical": {
                "Software Engineering": [
                    "Explain the concept of {concept} and provide a practical example",
                    "How would you design a {system_type} system?",
                    "What are the trade-offs between {option1} and {option2}?",
                    "Describe your approach to debugging a {problem_type} issue"
                ],
                "Data Science": [
                    "Explain when you would use {algorithm} vs {alternative}",
                    "How would you handle {data_issue} in a dataset?",
                    "Describe your approach to feature engineering for {problem_type}",
                    "What metrics would you use to evaluate a {model_type} model?"
                ]
            },
            "behavioral": [
                "Tell me about a time when you had to {situation}",
                "Describe a challenging project you worked on and how you overcame obstacles",
                "How do you handle conflicting priorities and tight deadlines?",
                "Give an example of when you had to work with a difficult team member"
            ],
            "situational": [
                "How would you handle a situation where {scenario}?",
                "What would you do if you discovered a critical bug in production?",
                "How would you approach learning a new technology quickly?",
                "Describe how you would prioritize features for a new product"
            ]
        }
    
    def generate_questions(self, domain: str, experience_level: str, 
                          job_description: str = "", num_questions: int = 5,
                          question_types: List[str] = None) -> List[Dict]:
        """Generate adaptive questions based on user profile"""
        
        if question_types is None:
            question_types = ["technical", "behavioral", "situational"]
        
        questions = []
        
        for i in range(num_questions):
            question_type = random.choice(question_types)
            difficulty = self._get_difficulty_level(experience_level, i)
            
            question_data = self._generate_single_question(
                domain, question_type, difficulty, job_description
            )
            
            questions.append({
                "id": i + 1,
                "question": question_data["question"],
                "type": question_type,
                "difficulty": difficulty,
                "expected_keywords": question_data["keywords"],
                "evaluation_criteria": question_data["criteria"],
                "sample_answer": question_data.get("sample_answer", "")
            })
        
        return questions
    
    def _get_difficulty_level(self, experience_level: str, question_number: int) -> str:
        """Determine difficulty level based on user experience and progression"""
        base_difficulty = {
            "Beginner": ["Easy", "Easy", "Medium"],
            "Intermediate": ["Easy", "Medium", "Medium", "Hard"],
            "Advanced": ["Medium", "Medium", "Hard", "Hard"]
        }
        
        difficulties = base_difficulty.get(experience_level, ["Medium"])
        return difficulties[question_number % len(difficulties)]
    
    def _generate_single_question(self, domain: str, question_type: str, 
                                 difficulty: str, job_description: str) -> Dict:
        """Generate a single question using OpenAI API"""
        
        prompt = self._build_question_prompt(domain, question_type, difficulty, job_description)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer creating high-quality interview questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            parsed_result = self._parse_question_response(content)
            
            # If parsing failed, use template generation
            if parsed_result is None:
                return self._generate_template_question(domain, question_type, difficulty)
            
            return parsed_result
            
        except Exception as e:
            # Fallback to template-based generation
            return self._generate_template_question(domain, question_type, difficulty)
    
    def _build_question_prompt(self, domain: str, question_type: str, 
                              difficulty: str, job_description: str) -> str:
        """Build prompt for question generation"""
        
        context = f"Job Description: {job_description}\n" if job_description else ""
        
        prompt = f"""
        Generate a {difficulty.lower()} {question_type} interview question for a {domain} position.
        
        {context}
        
        Requirements:
        - Question should be specific to {domain}
        - Difficulty level: {difficulty}
        - Type: {question_type}
        - Include relevant technical concepts for technical questions
        - For behavioral questions, focus on real-world scenarios
        
        Provide response in this JSON format:
        {{
            "question": "The interview question",
            "keywords": ["key", "terms", "to", "look", "for"],
            "criteria": ["evaluation", "criteria", "list"],
            "sample_answer": "Brief example of a good answer"
        }}
        """
        
        return prompt.strip()
    
    def _parse_question_response(self, content: str) -> Dict:
        """Parse the AI response to extract question data"""
        try:
            # Try to parse as JSON first
            data = json.loads(content)
            return {
                "question": data.get("question", ""),
                "keywords": data.get("keywords", []),
                "criteria": data.get("criteria", []),
                "sample_answer": data.get("sample_answer", "")
            }
        except json.JSONDecodeError:
            # Enhanced fallback parsing
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Look for a question line that doesn't contain "Here is" or similar phrases
            question = None
            for line in lines:
                # Skip introductory lines
                if any(phrase in line.lower() for phrase in ["here is", "this is", "here's", "question:"]):
                    continue
                # Look for a line that ends with ? or seems like a question
                if line.endswith('?') or len(line) > 20:
                    question = line
                    break
            
            # If no question found, use fallback template
            if not question or question == content.strip():
                return None  # This will trigger template generation
            
            return {
                "question": question,
                "keywords": [],
                "criteria": [],
                "sample_answer": ""
            }
    
    def _generate_template_question(self, domain: str, question_type: str, 
                                  difficulty: str) -> Dict:
        """Fallback template-based question generation"""
        
        # Define specific questions by domain and type
        specific_questions = {
            "technical": {
                "Software Engineering": {
                    "Easy": [
                        "What is the difference between a class and an object in object-oriented programming?",
                        "Explain what REST API is and give an example of how you would use it.",
                        "What is version control and why is it important in software development?",
                        "Describe the difference between frontend and backend development."
                    ],
                    "Medium": [
                        "How would you design a database schema for an e-commerce application?",
                        "Explain the concept of microservices and their advantages over monolithic architecture.",
                        "What are the SOLID principles and how do they improve code quality?",
                        "Describe how you would optimize a slow-running database query."
                    ],
                    "Hard": [
                        "Design a scalable system to handle 1 million concurrent users.",
                        "How would you implement a distributed cache across multiple servers?",
                        "Explain the CAP theorem and its implications for distributed systems.",
                        "Design a real-time messaging system like WhatsApp."
                    ]
                },
                "Data Science": {
                    "Easy": [
                        "What is the difference between supervised and unsupervised learning?",
                        "Explain what overfitting is and how to prevent it.",
                        "What are the key steps in the data science workflow?",
                        "Describe the difference between correlation and causation."
                    ],
                    "Medium": [
                        "How would you handle missing data in a dataset?",
                        "Explain the bias-variance tradeoff in machine learning.",
                        "What metrics would you use to evaluate a classification model?",
                        "Describe how you would approach feature selection for a predictive model."
                    ],
                    "Hard": [
                        "Design an end-to-end ML pipeline for a recommendation system.",
                        "How would you detect and handle concept drift in a production ML model?",
                        "Explain how you would build a real-time fraud detection system.",
                        "Design an A/B testing framework for measuring model performance."
                    ]
                }
            },
            "behavioral": [
                "Tell me about a time when you had to work with a difficult team member. How did you handle the situation?",
                "Describe a project where you had to learn a new technology quickly. How did you approach it?",
                "Give me an example of a time when you had to make a tough decision with limited information.",
                "Tell me about a time when you failed to meet a deadline. What happened and how did you handle it?",
                "Describe a situation where you had to convince others to accept your idea or approach.",
                "Tell me about a time when you received constructive criticism. How did you respond?"
            ],
            "situational": [
                "How would you handle a situation where a client suddenly changes the project requirements midway?",
                "What would you do if you discovered a critical security vulnerability in production code?",
                "How would you prioritize features when you have limited development resources?",
                "What steps would you take if you found out a team member was consistently underperforming?",
                "How would you approach debugging a system failure that's affecting multiple users?",
                "What would you do if you disagreed with your manager's technical decision?"
            ]
        }
        
        # Get appropriate question list
        if question_type == "technical":
            domain_questions = specific_questions["technical"].get(domain, specific_questions["technical"]["Software Engineering"])
            difficulty_questions = domain_questions.get(difficulty, domain_questions["Easy"])
            question = random.choice(difficulty_questions)
        else:
            questions_list = specific_questions.get(question_type, specific_questions["behavioral"])
            question = random.choice(questions_list)
        
        return {
            "question": question,
            "keywords": self._get_default_keywords(domain, question_type),
            "criteria": ["Clarity", "Relevance", "Specific examples", "Technical accuracy"],
            "sample_answer": ""
        }
    
    def _fill_template(self, template: str, domain: str, difficulty: str) -> str:
        """Fill question template with appropriate content"""
        
        # Simple template filling - in a real implementation, 
        # this would be more sophisticated
        replacements = {
            "{concept}": "object-oriented programming",
            "{system_type}": "scalable web",
            "{option1}": "REST",
            "{option2}": "GraphQL",
            "{problem_type}": "performance",
            "{algorithm}": "decision trees",
            "{alternative}": "neural networks",
            "{data_issue}": "missing values",
            "{model_type}": "classification",
            "{situation}": "lead a cross-functional team",
            "{scenario}": "a client changes requirements mid-project"
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def _get_default_keywords(self, domain: str, question_type: str) -> List[str]:
        """Get default keywords for evaluation"""
        
        domain_keywords = {
            "Software Engineering": ["code", "design", "architecture", "testing", "debugging"],
            "Data Science": ["data", "model", "analysis", "algorithm", "metrics"],
            "Product Management": ["user", "feature", "roadmap", "stakeholder", "metrics"],
            "Marketing": ["campaign", "audience", "conversion", "analytics", "brand"]
        }
        
        return domain_keywords.get(domain, ["experience", "approach", "example", "result"])
    
    def generate_followup_question(self, original_question: str, user_answer: str, 
                                 score: float) -> Optional[str]:
        """Generate follow-up question based on user's answer"""
        
        if score < 0.5:
            return f"Could you elaborate more on your answer to: '{original_question}'?"
        elif score > 0.8:
            return "That's a great answer! Can you share another example or go deeper into the technical details?"
        else:
            return None

# Add to core/__init__.py
from .user_manager import UserManager
from .question_generator import QuestionGenerator

__all__ = ['UserManager', 'QuestionGenerator']