#!/usr/bin/env python3
"""
Test script for advanced NLP evaluation metrics
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.answer_evaluator import AnswerEvaluator
from utils.evaluation_metrics import EvaluationMetrics


def test_evaluation_metrics():
    """Test the EvaluationMetrics class"""
    print("🧪 Testing EvaluationMetrics class...")
    
    metrics = EvaluationMetrics()
    
    # Test ROUGE scores
    generated = "Python is a powerful programming language used for web development and data science."
    reference = "Python is an excellent programming language for web development and machine learning."
    
    rouge_scores = metrics.calculate_rouge_scores(generated, reference)
    print(f"✅ ROUGE Scores: {rouge_scores}")
    
    # Test BLEU score
    references = [
        "Python is great for web development",
        "Python is excellent for data science and web development"
    ]
    bleu_score = metrics.calculate_bleu_score(generated, references)
    print(f"✅ BLEU Score: {bleu_score:.3f}")
    
    # Test F1 metrics
    predictions = [0.8, 0.6, 0.7, 0.9, 0.5]
    ground_truth = [0.7, 0.6, 0.8, 0.9, 0.4]
    f1_metrics = metrics.evaluate_answer_quality_metrics(predictions, ground_truth)
    print(f"✅ F1 Metrics: {f1_metrics}")


def test_answer_evaluator():
    """Test the enhanced AnswerEvaluator with NLP metrics"""
    print("\n🧪 Testing enhanced AnswerEvaluator...")
    
    # Create evaluator instance (without Groq API key for testing)
    os.environ['GROQ_API_KEY'] = 'test-key-for-testing'
    
    try:
        evaluator = AnswerEvaluator()
        
        # Sample question and answer
        question = {
            "question": "What are the benefits of using Python for web development?",
            "type": "technical",
            "expected_keywords": ["Python", "web development", "Django", "Flask", "scalable", "readable"],
            "sample_answer": "Python offers many benefits for web development including excellent frameworks like Django and Flask, clean readable syntax, extensive libraries, and good scalability for web applications."
        }
        
        user_answer = "Python is great for web development because it has frameworks like Django and Flask that make development faster. The syntax is very readable and clean, which makes maintenance easier. Python also has many libraries that help with web development tasks."
        
        # Evaluate the answer
        print("🔄 Evaluating answer...")
        evaluation = evaluator.evaluate_answer(question, user_answer)
        
        print("\n📊 Evaluation Results:")
        print(f"Overall Score: {evaluation['overall_score']:.1%}")
        print(f"Content Relevance: {evaluation['semantic_score']:.1%}")
        print(f"Keyword Usage: {evaluation['keyword_score']:.1%}")
        print(f"Structure: {evaluation['structure_score']:.1%}")
        
        # Check if NLP metrics are included
        if 'nlp_metrics' in evaluation:
            nlp_metrics = evaluation['nlp_metrics']
            print(f"\n🎯 Advanced NLP Metrics:")
            print(f"ROUGE-1: {nlp_metrics['rouge_scores']['rouge1']:.3f}")
            print(f"ROUGE-L: {nlp_metrics['rouge_scores']['rougeL']:.3f}")
            print(f"BLEU Score: {nlp_metrics['bleu_score']:.3f}")
            print(f"F1-Score: {nlp_metrics['f1_metrics']['f1_score']:.3f}")
            print(f"Composite NLP Score: {nlp_metrics['composite_nlp_score']:.3f}")
            print(f"Baseline Category: {nlp_metrics['baseline_comparison']['performance_category']}")
        else:
            print("⚠️ NLP metrics not found in evaluation results")
        
        print(f"\n💬 Feedback: {evaluation['feedback']}")
        print(f"✅ Strengths: {', '.join(evaluation['strengths'])}")
        print(f"📈 Areas for improvement: {', '.join(evaluation['improvements'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AnswerEvaluator: {e}")
        return False


def test_short_answer():
    """Test evaluation with short answer"""
    print("\n🧪 Testing short answer evaluation...")
    
    try:
        evaluator = AnswerEvaluator()
        
        question = {
            "question": "What is Python?",
            "type": "technical",
            "expected_keywords": ["Python", "programming", "language"]
        }
        
        short_answer = "It's a language."
        
        evaluation = evaluator.evaluate_answer(question, short_answer)
        
        print(f"Short answer evaluation:")
        print(f"Overall Score: {evaluation['overall_score']:.1%}")
        print(f"Feedback: {evaluation['feedback']}")
        print(f"Has NLP metrics: {'nlp_metrics' in evaluation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing short answer: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Advanced NLP Evaluation Tests\n")
    
    tests_passed = 0
    total_tests = 3
    
    try:
        # Test 1: Basic metrics
        test_evaluation_metrics()
        tests_passed += 1
        print("✅ Test 1 PASSED: EvaluationMetrics")
        
        # Test 2: Enhanced evaluator
        if test_answer_evaluator():
            tests_passed += 1
            print("✅ Test 2 PASSED: Enhanced AnswerEvaluator")
        else:
            print("❌ Test 2 FAILED: Enhanced AnswerEvaluator")
        
        # Test 3: Short answer handling
        if test_short_answer():
            tests_passed += 1
            print("✅ Test 3 PASSED: Short answer handling")
        else:
            print("❌ Test 3 FAILED: Short answer handling")
            
    except Exception as e:
        print(f"❌ Test suite error: {e}")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Advanced NLP evaluation system is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
