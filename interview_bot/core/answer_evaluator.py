# core/answer_evaluator.py
from groq import Groq
import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from config.settings import Config
from utils.evaluation_metrics import EvaluationMetrics

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Also download punkt_tab for newer NLTK versions
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except:
        pass  # Ignore if punkt_tab doesn't exist in this NLTK version

class AnswerEvaluator:
    def __init__(self):
        self.config = Config()
        self.client = Groq(api_key=self.config.GROQ_API_KEY)
        
        # Initialize models
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.stop_words = set(stopwords.words('english'))
        self.evaluation_metrics = EvaluationMetrics()
    
    def evaluate_answer(self, question: Dict, user_answer: str) -> Dict:
        """Comprehensive answer evaluation"""
        
        if len(user_answer.strip()) < self.config.MIN_ANSWER_LENGTH:
            return self._create_evaluation_result(
                0.1, 0.1, 0.1, 0.1,
                "Answer is too short. Please provide a more detailed response.",
                None  # No NLP metrics for short answers
            )
        
        # Multi-dimensional evaluation
        semantic_score = self._evaluate_semantic_similarity(question, user_answer)
        keyword_score = self._evaluate_keyword_coverage(question, user_answer)
        structure_score = self._evaluate_answer_structure(user_answer)
        
        # Advanced NLP metrics evaluation
        nlp_metrics = self._calculate_advanced_nlp_metrics(question, user_answer)
        
        # Generate AI-powered feedback
        ai_feedback = self._generate_ai_feedback(question, user_answer)
        
        # Calculate overall score with weights (including NLP metrics)
        overall_score = (
            semantic_score * 0.3 +
            keyword_score * 0.25 +
            structure_score * 0.25 +
            nlp_metrics['composite_nlp_score'] * 0.2
        )
        
        return self._create_evaluation_result(
            semantic_score, keyword_score, structure_score, 
            overall_score, ai_feedback, nlp_metrics
        )
    
    def _evaluate_semantic_similarity(self, question: Dict, user_answer: str) -> float:
        """Evaluate semantic similarity using TF-IDF"""
        
        try:
            # Create reference text from question and expected elements
            reference_elements = []
            
            if question.get("sample_answer"):
                reference_elements.append(question["sample_answer"])
            
            if question.get("expected_keywords"):
                keyword_context = " ".join(question["expected_keywords"])
                reference_elements.append(f"Key topics: {keyword_context}")
            
            if question.get("evaluation_criteria"):
                criteria_context = " ".join(question["evaluation_criteria"])
                reference_elements.append(f"Important aspects: {criteria_context}")
            
            # Add the question itself as reference
            reference_elements.append(question.get('question', ''))
            
            if not reference_elements:
                return 0.5  # Neutral score if no reference available
            
            reference_text = " ".join(reference_elements)
            
            # Calculate TF-IDF similarity
            texts = [user_answer, reference_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Normalize to 0-1 range and add baseline score
            similarity_score = max(0.2, min(1.0, similarity + 0.3))  # Add baseline
            
            return similarity_score
            
        except Exception as e:
            print(f"Semantic evaluation error: {e}")
            return 0.5
    
    def _evaluate_keyword_coverage(self, question: Dict, user_answer: str) -> float:
        """Evaluate coverage of expected keywords"""
        
        expected_keywords = question.get("expected_keywords", [])
        if not expected_keywords:
            return 0.7  # Default score if no keywords specified
        
        # Preprocess user answer
        user_text = user_answer.lower()
        user_words = set(word_tokenize(user_text))
        user_words = {word for word in user_words if word not in self.stop_words and word.isalnum()}
        
        # Check keyword coverage
        matched_keywords = 0
        total_keywords = len(expected_keywords)
        
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            # Check for exact match or partial match
            if (keyword_lower in user_text or 
                keyword_lower in user_words or
                any(keyword_lower in word for word in user_words)):
                matched_keywords += 1
        
        coverage_score = matched_keywords / total_keywords if total_keywords > 0 else 0.7
        return min(1.0, coverage_score)
    
    def _evaluate_answer_structure(self, user_answer: str) -> float:
        """Evaluate answer structure and organization"""
        
        sentences = sent_tokenize(user_answer)
        words = word_tokenize(user_answer)
        
        structure_score = 0.0
        
        # Length appropriateness (1-3 sentences too short, >10 might be too verbose)
        if 3 <= len(sentences) <= 8:
            structure_score += 0.3
        elif len(sentences) > 1:
            structure_score += 0.2
        
        # Word count appropriateness (30-200 words is ideal)
        word_count = len([word for word in words if word.isalnum()])
        if 30 <= word_count <= 200:
            structure_score += 0.3
        elif 20 <= word_count <= 300:
            structure_score += 0.2
        
        # Check for structured approach indicators
        structure_indicators = [
            r'\b(first|firstly|second|secondly|third|thirdly|finally|lastly)\b',
            r'\b(however|therefore|moreover|furthermore|additionally)\b',
            r'\b(for example|such as|specifically|particularly)\b',
            r'\b(in conclusion|to summarize|overall)\b'
        ]
        
        for pattern in structure_indicators:
            if re.search(pattern, user_answer, re.IGNORECASE):
                structure_score += 0.1
        
        return min(1.0, structure_score)
    
    def _calculate_advanced_nlp_metrics(self, question: Dict, user_answer: str) -> Dict:
        """Calculate advanced NLP metrics (ROUGE, BLEU, F1)"""
        
        try:
            # Get reference texts for comparison
            reference_texts = []
            
            # Use sample answer as primary reference
            if question.get("sample_answer"):
                reference_texts.append(question["sample_answer"])
            
            # Create reference from expected keywords and criteria
            if question.get("expected_keywords") or question.get("evaluation_criteria"):
                reference_elements = []
                
                if question.get("expected_keywords"):
                    reference_elements.extend(question["expected_keywords"])
                
                if question.get("evaluation_criteria"):
                    reference_elements.extend(question["evaluation_criteria"])
                
                # Create a coherent reference text from keywords/criteria
                reference_text = f"A good answer should include: {', '.join(reference_elements)}."
                reference_texts.append(reference_text)
            
            # Fallback: use question as reference
            if not reference_texts:
                reference_texts.append(question.get('question', ''))
            
            # Calculate ROUGE scores using the first (best) reference
            primary_reference = reference_texts[0] if reference_texts else ""
            rouge_scores = self.evaluation_metrics.calculate_rouge_scores(
                user_answer, primary_reference
            )
            
            # Calculate BLEU score using all references
            bleu_score = self.evaluation_metrics.calculate_bleu_score(
                user_answer, reference_texts
            )
            
            # Create mock predictions and ground truth for F1 calculation
            # This is a simplified approach - in production, you'd have actual training data
            predicted_score = self._calculate_answer_quality_score(user_answer)
            reference_score = 0.8  # Assume good reference answers score 0.8
            
            f1_metrics = self.evaluation_metrics.evaluate_answer_quality_metrics(
                [predicted_score], [reference_score]
            )
            
            # Calculate composite NLP score
            composite_score = (
                rouge_scores['rouge1'] * 0.3 +
                rouge_scores['rougeL'] * 0.3 +
                bleu_score * 0.25 +
                f1_metrics['f1_score'] * 0.15
            )
            
            return {
                'rouge_scores': rouge_scores,
                'bleu_score': round(bleu_score, 3),
                'f1_metrics': f1_metrics,
                'composite_nlp_score': round(composite_score, 3),
                'baseline_comparison': {
                    'user_vs_reference': round(composite_score, 3),
                    'performance_category': self._categorize_nlp_performance(composite_score)
                }
            }
            
        except Exception as e:
            print(f"Advanced NLP metrics error: {e}")
            # Return default scores on error
            return {
                'rouge_scores': {'rouge1': 0.5, 'rouge2': 0.4, 'rougeL': 0.45},
                'bleu_score': 0.5,
                'f1_metrics': {'f1_score': 0.5, 'accuracy': 0.5, 'correlation': 0.0},
                'composite_nlp_score': 0.5,
                'baseline_comparison': {
                    'user_vs_reference': 0.5,
                    'performance_category': 'Average'
                }
            }
    
    def _calculate_answer_quality_score(self, user_answer: str) -> float:
        """Calculate a simple quality score for F1 metric calculation"""
        # This is a simplified quality assessment
        word_count = len(user_answer.split())
        sentence_count = len(sent_tokenize(user_answer))
        
        # Basic quality indicators
        quality_score = 0.0
        
        # Length appropriateness
        if 30 <= word_count <= 200:
            quality_score += 0.3
        elif 20 <= word_count <= 300:
            quality_score += 0.2
        
        # Sentence structure
        if 2 <= sentence_count <= 8:
            quality_score += 0.3
        
        # Vocabulary diversity
        unique_words = len(set(user_answer.lower().split()))
        if unique_words / max(word_count, 1) > 0.5:
            quality_score += 0.2
        
        # Presence of connecting words
        connecting_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally']
        if any(word in user_answer.lower() for word in connecting_words):
            quality_score += 0.2
        
        return min(1.0, quality_score)
    
    def _categorize_nlp_performance(self, composite_score: float) -> str:
        """Categorize NLP performance based on composite score"""
        if composite_score >= 0.8:
            return "Excellent"
        elif composite_score >= 0.6:
            return "Good"
        elif composite_score >= 0.4:
            return "Average"
        else:
            return "Needs Improvement"
    
    def _generate_ai_feedback(self, question: Dict, user_answer: str) -> str:
        """Generate detailed feedback using AI"""
        
        prompt = f"""
        Analyze this interview answer and provide constructive feedback:
        
        Question: {question.get('question', '')}
        Question Type: {question.get('type', 'general')}
        Expected Keywords: {', '.join(question.get('expected_keywords', []))}
        
        User's Answer: {user_answer}
        
        Provide specific, actionable feedback in 2-3 sentences focusing on:
        1. What was done well
        2. What could be improved
        3. Specific suggestions for better answers
        
        Keep feedback constructive and encouraging.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert interview coach providing helpful feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback feedback
            return self._generate_fallback_feedback(question, user_answer)
    
    def _generate_fallback_feedback(self, question: Dict, user_answer: str) -> str:
        """Generate basic feedback when AI is unavailable"""
        
        feedback_parts = []
        
        # Length feedback
        word_count = len(user_answer.split())
        if word_count < 20:
            feedback_parts.append("Consider providing more detail in your response.")
        elif word_count > 150:
            feedback_parts.append("Try to be more concise while maintaining key points.")
        else:
            feedback_parts.append("Good answer length.")
        
        # Keyword feedback
        expected_keywords = question.get("expected_keywords", [])
        if expected_keywords:
            mentioned_keywords = []
            for keyword in expected_keywords:
                if keyword.lower() in user_answer.lower():
                    mentioned_keywords.append(keyword)
            
            if mentioned_keywords:
                feedback_parts.append(f"Great job mentioning: {', '.join(mentioned_keywords)}.")
            else:
                feedback_parts.append(f"Consider including these key concepts: {', '.join(expected_keywords[:3])}.")
        
        # Structure feedback
        if ". " in user_answer or ":" in user_answer:
            feedback_parts.append("Good structure with clear points.")
        else:
            feedback_parts.append("Try organizing your answer with clear, separate points.")
        
        return " ".join(feedback_parts)
    
    def _create_evaluation_result(self, semantic_score: float, keyword_score: float,
                                structure_score: float, overall_score: float,
                                feedback: str, nlp_metrics: Dict = None) -> Dict:
        """Create standardized evaluation result"""
        
        # Determine performance level
        if overall_score >= 0.8:
            performance_level = "Excellent"
            color = "green"
        elif overall_score >= 0.6:
            performance_level = "Good"
            color = "blue"
        elif overall_score >= 0.4:
            performance_level = "Fair"
            color = "orange"
        else:
            performance_level = "Needs Improvement"
            color = "red"
        
        result = {
            "semantic_score": round(semantic_score, 3),
            "keyword_score": round(keyword_score, 3),
            "structure_score": round(structure_score, 3),
            "overall_score": round(overall_score, 3),
            "performance_level": performance_level,
            "color": color,
            "feedback": feedback,
            "strengths": self._identify_strengths(semantic_score, keyword_score, structure_score),
            "improvements": self._identify_improvements(semantic_score, keyword_score, structure_score)
        }
        
        # Add NLP metrics if available
        if nlp_metrics:
            result["nlp_metrics"] = nlp_metrics
        
        return result
    
    def _identify_strengths(self, semantic_score: float, keyword_score: float, 
                          structure_score: float) -> List[str]:
        """Identify answer strengths"""
        strengths = []
        
        if semantic_score > 0.7:
            strengths.append("Strong content relevance")
        if keyword_score > 0.7:
            strengths.append("Good use of technical terminology")
        if structure_score > 0.7:
            strengths.append("Well-organized response")
        
        return strengths if strengths else ["Shows understanding of the topic"]
    
    def _identify_improvements(self, semantic_score: float, keyword_score: float,
                             structure_score: float) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        if semantic_score < 0.5:
            improvements.append("Address the question more directly")
        if keyword_score < 0.5:
            improvements.append("Include more relevant technical terms")
        if structure_score < 0.5:
            improvements.append("Improve answer organization and flow")
        
        return improvements if improvements else ["Continue practicing to build confidence"]
    
    def batch_evaluate_answers(self, questions_and_answers: List[Tuple[Dict, str]]) -> List[Dict]:
        """Evaluate multiple answers efficiently"""
        results = []
        
        for question, answer in questions_and_answers:
            evaluation = self.evaluate_answer(question, answer)
            evaluation["question_id"] = question.get("id")
            results.append(evaluation)
        
        return results
    
    def calculate_session_metrics(self, evaluations: List[Dict]) -> Dict:
        """Calculate overall session performance metrics"""
        
        if not evaluations:
            return {
                "session_average": 0.0,
                "strongest_area": "None",
                "weakest_area": "None",
                "total_questions": 0
            }
        
        # Calculate averages
        semantic_avg = np.mean([e["semantic_score"] for e in evaluations])
        keyword_avg = np.mean([e["keyword_score"] for e in evaluations])
        structure_avg = np.mean([e["structure_score"] for e in evaluations])
        overall_avg = np.mean([e["overall_score"] for e in evaluations])
        
        # Identify strongest and weakest areas
        scores = {
            "Content Relevance": semantic_avg,
            "Technical Knowledge": keyword_avg,
            "Communication Structure": structure_avg
        }
        
        strongest_area = max(scores, key=scores.get)
        weakest_area = min(scores, key=scores.get)
        
        return {
            "session_average": round(overall_avg, 3),
            "semantic_average": round(semantic_avg, 3),
            "keyword_average": round(keyword_avg, 3),
            "structure_average": round(structure_avg, 3),
            "strongest_area": strongest_area,
            "weakest_area": weakest_area,
            "total_questions": len(evaluations),
            "performance_distribution": {
                "excellent": len([e for e in evaluations if e["overall_score"] >= 0.8]),
                "good": len([e for e in evaluations if 0.6 <= e["overall_score"] < 0.8]),
                "fair": len([e for e in evaluations if 0.4 <= e["overall_score"] < 0.6]),
                "needs_improvement": len([e for e in evaluations if e["overall_score"] < 0.4])
            }
        }
