"""Issue analyzer with classification, priority scoring, and explainability."""

import re
from typing import Literal
from vector_store import get_vector_store

IssueType = Literal["bug", "feature", "question"]
Priority = Literal["low", "medium", "high", "critical"]

# Keyword patterns for classification
BUG_KEYWORDS = [
    r'\berror\b', r'\bbug\b', r'\bcrash\b', r'\bfail\b', r'\bfailed\b', r'\bfailing\b',
    r'\bbroken\b', r'\bfix\b', r'\bissue\b', r'\bproblem\b', r'\bexception\b',
    r'\bnot working\b', r'\bdoesn\'t work\b', r'\bwon\'t\b', r'\bcan\'t\b',
    r'\bunexpected\b', r'\bincorrect\b', r'\bwrong\b', r'\bregression\b',
    r'\btraceback\b', r'\bstack trace\b', r'\bsegfault\b', r'\bsegmentation\b',
    r'\bnull\b', r'\bundefined\b', r'\bNaN\b', r'\b500\b', r'\b404\b', r'\b403\b'
]

FEATURE_KEYWORDS = [
    r'\bfeature\b', r'\brequest\b', r'\benhancement\b', r'\bimprovement\b',
    r'\badd\b', r'\bimplement\b', r'\bsupport\b', r'\bnew\b', r'\bwould be nice\b',
    r'\bshould\b', r'\bcould\b', r'\bwish\b', r'\bproposal\b', r'\bidea\b',
    r'\ballow\b', r'\benable\b', r'\bintegrate\b', r'\bextend\b'
]

QUESTION_KEYWORDS = [
    r'\bhow\b', r'\bwhy\b', r'\bwhat\b', r'\bwhen\b', r'\bwhere\b',
    r'\bhelp\b', r'\bquestion\b', r'\bconfused\b', r'\bdocumentation\b',
    r'\bexplain\b', r'\bunderstand\b', r'\bclarify\b', r'\bexample\b',
    r'\btutorial\b', r'\bguide\b', r'\?$'
]

# Priority indicators
HIGH_PRIORITY_KEYWORDS = [
    r'\bcritical\b', r'\burgent\b', r'\bsecurity\b', r'\bvulnerability\b',
    r'\bdata loss\b', r'\bproduction\b', r'\bblocking\b', r'\bbreaking\b',
    r'\bcrash\b', r'\bdown\b', r'\boutage\b', r'\bemergency\b',
    r'\bsevere\b', r'\basap\b', r'\bimmediately\b'
]

MEDIUM_PRIORITY_KEYWORDS = [
    r'\bperformance\b', r'\bslow\b', r'\bmemory\b', r'\bimportant\b',
    r'\bregression\b', r'\bbreaks\b', r'\baffects\b'
]

LOW_PRIORITY_KEYWORDS = [
    r'\bminor\b', r'\btypo\b', r'\bcosmetic\b', r'\bnice to have\b',
    r'\blow priority\b', r'\bwhenever\b', r'\bno rush\b', r'\bsmall\b'
]

CORE_FUNCTIONALITY_KEYWORDS = [
    r'\bauth\b', r'\blogin\b', r'\bapi\b', r'\bdatabase\b', r'\bcore\b',
    r'\bmain\b', r'\bpayment\b', r'\bcheckout\b', r'\bsecurity\b', r'\buser\b'
]

def count_matches(text: str, patterns: list[str]) -> int:
    """Count how many patterns match in text."""
    text_lower = text.lower()
    return sum(1 for p in patterns if re.search(p, text_lower))

def classify_issue(title: str, body: str) -> tuple[IssueType, float, list[str]]:
    """Classify issue type with confidence and reasoning."""
    text = f"{title} {body}".lower()
    reasons = []
    
    bug_score = count_matches(text, BUG_KEYWORDS)
    feature_score = count_matches(text, FEATURE_KEYWORDS)
    question_score = count_matches(text, QUESTION_KEYWORDS)
    
    # Boost scores based on title (more important)
    title_lower = title.lower()
    if count_matches(title_lower, BUG_KEYWORDS) > 0:
        bug_score += 3
        reasons.append("Bug-related keywords found in title")
    if count_matches(title_lower, FEATURE_KEYWORDS) > 0:
        feature_score += 3
        reasons.append("Feature-related keywords found in title")
    if count_matches(title_lower, QUESTION_KEYWORDS) > 0:
        question_score += 3
        reasons.append("Question-related keywords found in title")
    
    # Check for code blocks/stack traces (strong bug indicator)
    if '```' in body or 'Traceback' in body or 'Error:' in body:
        bug_score += 4
        reasons.append("Contains error stack trace or code block")
    
    # Calculate confidence
    total = bug_score + feature_score + question_score + 1  # +1 to avoid division by zero
    
    if bug_score >= feature_score and bug_score >= question_score:
        confidence = min(0.95, 0.5 + (bug_score / total) * 0.5)
        if not reasons:
            reasons.append("Detected failure-related keywords in body")
        return "bug", confidence, reasons
    elif feature_score >= question_score:
        confidence = min(0.95, 0.5 + (feature_score / total) * 0.5)
        if not reasons:
            reasons.append("Detected enhancement-related keywords")
        return "feature", confidence, reasons
    else:
        confidence = min(0.95, 0.5 + (question_score / total) * 0.5)
        if not reasons:
            reasons.append("Detected question patterns")
        return "question", confidence, reasons

def calculate_priority(title: str, body: str, issue_type: IssueType, 
                       similar_issues: list[dict]) -> tuple[Priority, float, list[str]]:
    """Calculate priority with score and reasoning."""
    text = f"{title} {body}".lower()
    reasons = []
    score = 50  # Base score
    
    # Keyword-based scoring
    high_matches = count_matches(text, HIGH_PRIORITY_KEYWORDS)
    medium_matches = count_matches(text, MEDIUM_PRIORITY_KEYWORDS)
    low_matches = count_matches(text, LOW_PRIORITY_KEYWORDS)
    core_matches = count_matches(text, CORE_FUNCTIONALITY_KEYWORDS)
    
    if high_matches > 0:
        score += high_matches * 15
        reasons.append(f"Contains {high_matches} high-priority indicator(s)")
    
    if medium_matches > 0:
        score += medium_matches * 8
    
    if low_matches > 0:
        score -= low_matches * 10
        reasons.append("Contains low-priority indicators")
    
    if core_matches > 0:
        score += core_matches * 10
        reasons.append("Mentions core functionality")
    
    # Bug type boost
    if issue_type == "bug":
        score += 15
        reasons.append("Bugs typically require faster response")
    
    # Similar high-priority issues boost
    high_similarity_issues = [s for s in similar_issues if s.get("similarity", 0) > 0.8]
    if high_similarity_issues:
        max_sim = max(s["similarity"] for s in high_similarity_issues)
        score += 10
        reasons.append(f"High similarity ({max_sim:.2f}) with existing issue")
    
    # Text length consideration (longer = more detailed = potentially more serious)
    if len(body) > 500:
        score += 5
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Convert to priority level
    if score >= 80:
        priority = "critical"
    elif score >= 60:
        priority = "high"
    elif score >= 40:
        priority = "medium"
    else:
        priority = "low"
    
    return priority, score / 100, reasons

def generate_explanation(
    issue_type: IssueType,
    type_confidence: float,
    type_reasons: list[str],
    priority: Priority,
    priority_score: float,
    priority_reasons: list[str],
    similar_issues: list[dict]
) -> list[str]:
    """Generate human-readable explanation bullets."""
    explanations = []
    
    # Type explanation
    explanations.append(f"Classified as **{issue_type}** with {type_confidence:.0%} confidence")
    explanations.extend(type_reasons[:2])
    
    # Priority explanation
    explanations.append(f"Priority set to **{priority}** (score: {priority_score:.0%})")
    explanations.extend(priority_reasons[:2])
    
    # Similarity explanation
    if similar_issues:
        top = similar_issues[0]
        explanations.append(
            f"Most similar to issue #{top['id']} ({top['similarity']:.0%} match)"
        )
    
    return explanations

def generate_suggested_reply(
    title: str,
    issue_type: IssueType,
    priority: Priority,
    similar_issues: list[dict]
) -> str:
    """Generate a suggested GitHub auto-reply comment."""
    
    type_labels = {
        "bug": "🐛 Bug Report",
        "feature": "✨ Feature Request", 
        "question": "❓ Question"
    }
    
    priority_labels = {
        "critical": "🔴 Critical",
        "high": "🟠 High Priority",
        "medium": "🟡 Medium Priority",
        "low": "🟢 Low Priority"
    }
    
    reply_parts = [
        f"Thank you for opening this issue!",
        f"",
        f"**Auto-triage results:**",
        f"- Type: {type_labels.get(issue_type, issue_type)}",
        f"- Priority: {priority_labels.get(priority, priority)}",
    ]
    
    if similar_issues:
        top_similar = similar_issues[0]
        if top_similar["similarity"] > 0.75:
            reply_parts.extend([
                f"",
                f"**Related issues:**",
                f"- #{top_similar['id']}: {top_similar['title'][:60]}... ({top_similar['similarity']:.0%} similar)"
            ])
            if top_similar["similarity"] > 0.85:
                reply_parts.append(f"",)
                reply_parts.append(f"⚠️ This issue appears to be very similar to #{top_similar['id']}. Please check if it addresses your concern.")
    
    if issue_type == "bug" and priority in ["high", "critical"]:
        reply_parts.extend([
            f"",
            f"This has been flagged as a **{priority}-priority bug** and will be reviewed shortly."
        ])
    elif issue_type == "question":
        reply_parts.extend([
            f"",
            f"For questions, you may also find helpful information in our documentation or discussions."
        ])
    
    reply_parts.extend([
        f"",
        f"---",
        f"*🤖 Automated triage by OpenIssue AI*"
    ])
    
    return "\n".join(reply_parts)

async def analyze_issue(title: str, body: str) -> dict:
    """Full analysis pipeline for an issue."""
    store = get_vector_store()
    
    # Get similar issues
    similar_issues = store.search_similar(title, body, k=3)
    
    # Classify
    issue_type, type_confidence, type_reasons = classify_issue(title, body)
    
    # Calculate priority
    priority, priority_score, priority_reasons = calculate_priority(
        title, body, issue_type, similar_issues
    )
    
    # Generate explanation
    explanation = generate_explanation(
        issue_type, type_confidence, type_reasons,
        priority, priority_score, priority_reasons,
        similar_issues
    )
    
    # Generate suggested reply
    suggested_reply = generate_suggested_reply(
        title, issue_type, priority, similar_issues
    )
    
    # Overall confidence (weighted average)
    overall_confidence = (type_confidence * 0.6 + priority_score * 0.4)
    
    return {
        "type": issue_type,
        "type_confidence": type_confidence,
        "priority": priority,
        "priority_score": priority_score,
        "confidence": overall_confidence,
        "similar_issues": similar_issues,
        "explanation": explanation,
        "suggested_reply": suggested_reply
    }
