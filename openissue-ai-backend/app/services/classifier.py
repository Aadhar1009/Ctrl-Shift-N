import re
import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class IssueClassifier:
    def __init__(self):
        self.category_seeds = {
            "bug": [
                "The application crashed with a stack trace or error message.",
                "Unexpected behavior, runtime panic, or segmentation fault.",
                "Functional regression where a feature stopped working correctly.",
                "System failure, broken UI, or data corruption."
            ],
            "feature": [
                "Request for a new functionality or enhancement.",
                "Proposal to add support for a new library or tool.",
                "Suggestion to improve user experience or add a button.",
                "Expansion of the existing API or core capabilities."
            ],
            "question": [
                "General inquiry about how the system works.",
                "Confusion about a specific configuration or setup.",
                "Seeking clarification on existing features.",
                "Asking the community for help and guidance."
            ],
            "query": [
                "How do I fetch or retrieve specific data from the API?",
                "What is the correct syntax for searching or filtering?",
                "Seeking specific information or data extraction methods.",
                "Inquiry about backend data structures and schemas."
            ],
            "procedure": [
                "What are the steps to deploy the application?",
                "How do I set up the development environment from scratch?",
                "Standard operating procedures for managing the system.",
                "Workflow guidance for CI/CD or production maintenance."
            ],
            "method": [
                "Seeking feedback on a code implementation or pattern.",
                "How should I structure this specific function or class?",
                "Review of a programming method or architectural choice.",
                "Inquiry about coding best practices within this repo."
            ]
        }

    def _cosine_similarity(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    async def classify(self, nlp_data: Dict[str, Any], raw_text: str, embedder=None) -> Tuple[str, float]:
        """
        Classifies an issue using Choice C (Semantic Similarity) with combined Heuristic Boosts.
        """
        text_lower = raw_text.lower()
        
        # 1. Immediate High-Confidence Fallbacks
        if nlp_data.get("has_stack_trace", False) or any(x in text_lower for x in ["panic", "segfault", "critical crash", "data loss"]):
            return "bug", 0.95

        # 2. Choice C: Semantic Vector Similarity
        if embedder:
            issue_vector = embedder.generate_embedding(raw_text)
            scores = {}
            for category, seeds in self.category_seeds.items():
                category_vectors = embedder.generate_batch(seeds)
                similarities = [self._cosine_similarity(issue_vector, cv) for cv in category_vectors]
                scores[category] = sum(similarities) / len(similarities)
            
            # Application of Heuristic Boosts (Merge from Team Changes)
            signals = {"bug": 0.0, "feature": 0.0, "question": 0.0}
            
            # Bug signals
            bug_keywords = ["crash", "error", "broken", "fails", "exception", "bug", "issue", "doesn't work", "regression", "panic", "freeze"]
            for kw in bug_keywords:
                if re.search(r'\b' + kw + r'\b', text_lower):
                    signals["bug"] += 0.05 # Minor boost
            
            # Feature signals
            feature_keywords = ["add", "support", "would like", "feature", "enhancement", "proposal", "improve", "wishlist", "request"]
            for kw in feature_keywords:
                if re.search(r'\b' + kw + r'\b', text_lower):
                    signals["feature"] += 0.05
            
            # Question signals
            if nlp_data.get("question_count", 0) > 0:
                signals["question"] += 0.1
            
            # Combine scores
            for cat, boost in signals.items():
                if cat in scores:
                    scores[cat] += boost

            # Winner selection
            max_category = max(scores.items(), key=lambda x: x[1])
            logger.info(f"Final Combined Scores: {scores}")
            
            if max_category[1] > 0.40:
                confidence = min(0.98, max_category[1] + 0.15)
                return max_category[0], round(confidence, 2)

        # 3. Final Fallback
        return "question", 0.40
