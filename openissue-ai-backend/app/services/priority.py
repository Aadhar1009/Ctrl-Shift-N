from typing import Tuple, Dict, Any
import re

class PriorityScorer:
    def score(self, nlp_data: Dict[str, Any], raw_text: str, issue_type: str, metadata: Any, comments: int = 0, reactions: int = 0) -> Tuple[str, int]:
        score = 0
        
        # Split title and body to apply positional weighting
        parts = raw_text.split("\n", 1)
        title = parts[0].lower() if len(parts) > 0 else ""
        body = parts[1].lower() if len(parts) > 1 else ""
        
        # ---------------------------------------------------------
        # 1. SEVERITY ROOT MATCHING (Exhaustive Combo)
        # ---------------------------------------------------------
        severity_map = {
            "critical": 35, "crash": 35, "blocker": 35, "blocking": 30,
            "urgent": 25, "asap": 25, "memory leak": 30, "security": 40,
            "data loss": 45, "regression": 30, "broken": 20, "production": 30,
            "outage": 45, "vulnerability": 45, "exploit": 45, "panic": 40,
            "fault": 30, "freeze": 25, "frozen": 25, "corrupt": 40, "not responding": 25
        }
        
        for root, pts in severity_map.items():
            if root in title:
                score += pts * 2.5  # Heavy weighting for title
            if root in body:
                score += pts * 1.0
                
        # ---------------------------------------------------------
        # 2. METADATA / HARD LABELS
        # ---------------------------------------------------------
        if metadata and getattr(metadata, 'labels', None):
            for label in metadata.labels:
                lbl = label.lower()
                if any(x in lbl for x in ["high", "critical", "p0", "p1", "blocker", "urgent", "security"]):
                    score += 50
                elif any(x in lbl for x in ["bug", "regression", "issue"]):
                    score += 25
                    
        # ---------------------------------------------------------
        # 3. CONTEXT MULTIPLIERS (Choice C Logic)
        # ---------------------------------------------------------
        if nlp_data.get('has_stack_trace', False):
            score += 35
            
        if nlp_data.get('has_code', False):
            score += 15
            
        if issue_type == "bug":
            score += 25
        elif issue_type == "feature":
            score -= 10
            
        exclamations = nlp_data.get('exclamation_count', 0)
        score += min(exclamations * 5, 25)
        
        # ---------------------------------------------------------
        # 4. COMMUNITY ENGAGEMENT (Engagement Signals)
        # ---------------------------------------------------------
        if comments > 10:
            score += 25
        elif comments > 4:
            score += 15
            
        if reactions > 5:
            score += 20
            
        # ---------------------------------------------------------
        # FINAL COMPUTATION
        # ---------------------------------------------------------
        score = max(0, min(100, int(score)))
        
        if score > 85:
            level = "Critical"
        elif score > 60:
            level = "High"
        elif score > 30:
            level = "Medium"
        else:
            level = "Low"
            
        return level, score
