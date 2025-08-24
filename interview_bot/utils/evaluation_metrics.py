# utils/evaluation_metrics.py
from typing import List, Dict
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

class EvaluationMetrics:
    """Utility class for calculating various evaluation metrics"""
    
    def __init__(self):
        # Try to import rouge-score, fall back to simple implementation if not available
        try:
            from rouge_score import rouge_scorer
            self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            self.use_rouge_package = True
        except ImportError:
            print("Warning: rouge-score package not found. Using simplified ROUGE implementation.")
            self.use_rouge_package = False
    
    def calculate_rouge_scores(self, generated_text: str, reference_text: str) -> Dict:
        """Calculate ROUGE scores for generated text"""
        if self.use_rouge_package:
            try:
                scores = self.rouge_scorer.score(reference_text, generated_text)
                return {
                    "rouge1": round(scores['rouge1'].fmeasure, 3),
                    "rouge2": round(scores['rouge2'].fmeasure, 3),
                    "rougeL": round(scores['rougeL'].fmeasure, 3)
                }
            except Exception as e:
                print(f"Error using rouge-score package: {e}. Falling back to simple implementation.")
                self.use_rouge_package = False
        
        # Simplified implementation without rouge-score dependency
        generated_words = set(generated_text.lower().split())
        reference_words = set(reference_text.lower().split())
        
        if not reference_words:
            return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
        
        overlap = generated_words.intersection(reference_words)
        rouge1 = len(overlap) / len(reference_words) if reference_words else 0
        
        return {
            "rouge1": round(rouge1, 3),
            "rouge2": round(rouge1 * 0.8, 3),  # Approximation
            "rougeL": round(rouge1 * 0.9, 3)   # Approximation
        }
    
    def calculate_bleu_score(self, generated_text: str, reference_texts: List[str]) -> float:
        """Calculate BLEU score (simplified implementation)"""
        
        generated_words = generated_text.lower().split()
        
        if not generated_words:
            return 0.0
        
        # Calculate precision for each reference
        precisions = []
        for reference in reference_texts:
            reference_words = reference.lower().split()
            if not reference_words:
                continue
            
            matches = sum(1 for word in generated_words if word in reference_words)
            precision = matches / len(generated_words) if generated_words else 0
            precisions.append(precision)
        
        return max(precisions) if precisions else 0.0
    
    def evaluate_answer_quality_metrics(self, predictions: List[float], 
                                       ground_truth: List[float], 
                                       threshold: float = 0.6) -> Dict:
        """Evaluate answer quality prediction metrics"""
        
        # Convert scores to binary classification (good/bad)
        pred_binary = [1 if score >= threshold else 0 for score in predictions]
        true_binary = [1 if score >= threshold else 0 for score in ground_truth]
        
        # Calculate metrics
        accuracy = accuracy_score(true_binary, pred_binary)
        f1 = f1_score(true_binary, pred_binary, average='weighted')
        
        # Calculate correlation
        correlation = np.corrcoef(predictions, ground_truth)[0, 1] if len(predictions) > 1 else 0
        
        return {
            "accuracy": round(accuracy, 3),
            "f1_score": round(f1, 3),
            "correlation": round(correlation, 3),
            "mean_prediction": round(np.mean(predictions), 3),
            "mean_ground_truth": round(np.mean(ground_truth), 3)
        }
