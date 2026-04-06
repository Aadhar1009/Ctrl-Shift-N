import httpx
import logging
import json
import re
from config import settings
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    async def generate_reasoned_analysis(self, title: str, body: str, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a structured JSON analysis using Gemini (Choice B Reasoning).
        Returns a dictionary containing classification, priority, labels, tech_domain, and the reply.
        """
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("GEMINI_API_KEY not found. LLM reasoning disabled.")
            return None

        prompt = f"""
        You are 'OpenIssue AI', a high-end Autonomous GitHub Maintainer.
        Your task is to analyze the following GitHub issue and return a valid JSON object.

        ISSUE DETAILS:
        Title: {title}
        Extracted Signals: {json.dumps(signals)}
        Body: {body[:1500]}

        INSTRUCTIONS:
        1. Classify the issue as exactly one of: [Bug, Feature, Question, Query, Procedure, Method].
        2. Determine Priority as exactly one of: [Low, Medium, High, Critical].
        3. Identify the 'tech_domain' as a specific technical category (e.g., 'React', 'Python', 'Rust', 'Docker', 'Auth', 'Database', 'TypeScript', 'CI/CD', 'None').
        4. Suggest 3-5 native GitHub labels.
        5. Write a professional, technical 'response' (under 200 words) in Markdown.

        RETURN ONLY THIS JSON FORMAT:
        {{
            "classification": "ClassificationType",
            "priority": "PriorityLevel",
            "labels": ["label1", "label2"],
            "tech_domain": "DomainName",
            "response": "Markdown response text here..."
        }}
        """

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract text parts
                json_text = data['candidates'][0]['content']['parts'][0]['text']
                # Clean potential markdown wrapping if any
                clean_json_text = re.sub(r'```json\n?|\n?```', '', json_text).strip()
                
                analysis_data = json.loads(clean_json_text)
                logger.info(f"LLM Reasoning Success: {analysis_data['classification']} / {analysis_data['tech_domain']}")
                return analysis_data

        except Exception as e:
            logger.error(f"LLM Reasoning Error: {str(e)}")
            return None

    def heuristic_fallback_reply(self, classification: str, priority: str) -> str:
        """Fallback deterministic response if LLM is offline."""
        responses = {
            "Bug": f"Thank you for reporting this **Bug**. Our initial analysis marked this as **{priority}**. A maintainer will investigate shortly.",
            "Feature": f"This sounds like a great **Feature** proposal! We've categorized this as **{priority}** priority.",
            "Question": f"Thanks for the **Question**. We've categorized this as **{priority}** priority. Documentation links are provided below."
        }
        return responses.get(classification, "Thank you for the issue! We are analyzing it now.")
