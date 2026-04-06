import hmac
import hashlib
import logging
import httpx
from typing import Dict, Any

from fastapi import HTTPException
from config import settings
from app.services.analyzer import IssueAnalyzer

logger = logging.getLogger(__name__)

class GitHubWebhookHandler:
    def __init__(self, analyzer: IssueAnalyzer):
        self.analyzer = analyzer

    def verify_signature(self, payload: bytes, signature_header: str) -> None:
        """Verify the payload signature using the webhook secret."""
        if not settings.GITHUB_WEBHOOK_SECRET:
            # For development without a secret configured, we might decide to allow it
            # But for production, we must reject or log. Let's strictly enforce if provided.
            logger.warning("GITHUB_WEBHOOK_SECRET is missing! Signature verification disabled.")
            return

        if not signature_header:
            raise HTTPException(status_code=403, detail="X-Hub-Signature-256 header missing")

        try:
            # Expected format: "sha256=..."
            algorithm, signature = signature_header.split("=", 1)
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid signature header format")

        if algorithm != "sha256":
            raise HTTPException(status_code=403, detail="Unsupported signature algorithm")

        mac = hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha256
        )
        expected_signature = mac.hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            logger.error("Webhook signature mismatch")
            raise HTTPException(status_code=403, detail="Invalid signature")

    async def process_webhook(self, event_type: str, payload_json: Dict[str, Any]) -> None:
        """Process incoming webhook. Should be spawned as a background task."""
        try:
            # We only care about issues being opened.
            if event_type != "issues":
                logger.info(f"Ignoring event type: {event_type}")
                return
            
            action = payload_json.get("action")
            if action != "opened":
                logger.info(f"Ignoring issue action: {action}")
                return

            issue_data = payload_json.get("issue", {})
            repo_data = payload_json.get("repository", {})

            if not issue_data or not repo_data:
                logger.error("Invalid webhook payload: Missing issue or repository data")
                return

            owner = repo_data.get("owner", {}).get("login")
            repo = repo_data.get("name")
            issue_num = issue_data.get("number")
            title = issue_data.get("title", "")
            body = issue_data.get("body", "") or "No description provided."
            author = issue_data.get("user", {}).get("login", "unknown")
            labels = [lbl.get("name") for lbl in issue_data.get("labels", [])]
            comments = issue_data.get("comments", 0)
            reactions = issue_data.get("reactions", {}).get("total_count", 0)

            logger.info(f"Processing webhook for issue #{issue_num} in {owner}/{repo}")

            # Mock metadata object to pass to analyzer (similar to fetch_github_issue)
            class MockMeta:
                def __init__(self, lbs, auth, rep):
                    self.labels = lbs
                    self.author = auth
                    self.repository = rep
            
            meta = MockMeta(labels, author, f"{owner}/{repo}")

            # Run the AI pipeline
            analysis_result = await self.analyzer.analyze(
                title=title,
                body=body,
                metadata=meta,
                issue_comments=comments,
                issue_reactions=reactions
            )

            # Post formatted comment and execute auto-admin tasks back if we have a token
            if settings.GITHUB_TOKEN:
                await self.execute_github_admin_actions(owner, repo, issue_num, body, analysis_result)
            else:
                logger.warning("GITHUB_TOKEN not set. Skipping automatic comment response.")

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}", exc_info=True)

    async def execute_github_admin_actions(self, owner: str, repo: str, issue_num: int, original_body: str, analysis: Dict[str, Any]) -> None:
        """Post the analysis result, assign labels, and auto-close duplicates natively via GitHub API."""
        base_api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "User-Agent": "OpenIssue-AI/2.0"
        }

        # ---------------------------------------------------------
        # 1. NATIVE AUTO-LABELING
        # ---------------------------------------------------------
        suggested_labels = analysis.get("suggested_labels", [])
        if suggested_labels:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.put(f"{base_api_url}/labels", headers=headers, json={"labels": suggested_labels})
                    logger.info(f"Successfully applied native labels left on #{issue_num}: {suggested_labels}")
            except Exception as e:
                logger.error(f"Error applying labels: {str(e)}")

        # ---------------------------------------------------------
        # 2. DUPLICATE AUTO-CLOSING
        # ---------------------------------------------------------
        similar_issues = analysis.get("similar_issues", [])
        duplicate_detected = False
        duplicate_ref = None
        
        if similar_issues:
            top_match = similar_issues[0]
            if top_match.get("similarity", 0) > 0.92:
                duplicate_detected = True
                duplicate_ref = top_match
                
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        # Close the issue
                        await client.patch(base_api_url, headers=headers, json={"state": "closed", "state_reason": "not_planned"})
                        # Apply 'duplicate' native label
                        await client.post(f"{base_api_url}/labels", headers=headers, json={"labels": ["duplicate"]})
                        logger.info(f"Auto-closed duplicate issue #{issue_num}")
                except Exception as e:
                    logger.error(f"Error auto-closing duplicate: {str(e)}")

        # ---------------------------------------------------------
        # 3. ACTIONABLE CHECKLIST (Nag Bot)
        # ---------------------------------------------------------
        classification_type = analysis.get("classification", {}).get("type", "Unknown")
        nlp_signals = analysis.get("nlp_signals", {})
        
        checklist_md = ""
        word_count = len(original_body.split())
        
        if classification_type == "Bug" and (word_count < 30 or not nlp_signals.get("has_stack_trace")):
            checklist_md = (
                "### 📋 Action Required: Missing Context\n"
                "> We noticed this looks like a bug report, but it's missing some crucial details required to fix it. "
                "Please reply to this issue with the following information filled out:\n\n"
                "- [ ] **Steps to reproduce:** What exactly did you do before it crashed?\n"
                "- [ ] **Expected vs Actual Behavior:** What did you expect to happen?\n"
                "- [ ] **Stack Trace / Logs:** Paste the exact console error inside triple backticks (\\`\\`\\`).\n"
                "- [ ] **OS & Versions:** (e.g. Mac OS, Node v18, etc.)\n\n"
                "*We will review this issue once the checklist is completed!* \n\n---\n"
            )

        # ---------------------------------------------------------
        # 4. AESTHETIC COMMENT FORMATTING
        # ---------------------------------------------------------
        priority_level = analysis.get("priority", {}).get("level", "Unknown")
        confidence = analysis.get("confidence_overall", 0.0)
        bot_reply = analysis.get("suggested_reply", "No automated reply available.")
        
        # Color-coded icons based on priority
        p_icon = "🟢" if priority_level == "Low" else "🟡" if priority_level == "Medium" else "🔴" if priority_level == "High" else "🚨"

        web_suggestions = analysis.get("web_suggestions", [])
        suggestions_md = ""
        if web_suggestions:
            suggestions_md = "\n### 📚 Helpful References\n"
            for sug in web_suggestions:
                suggestions_md += f"**{sug.get('title', 'Suggestion')}**\n"
                suggestions_md += f"> {sug.get('advice', '')}\n\n"
                if "articles" in sug and sug["articles"]:
                    for article in sug["articles"]:
                        suggestions_md += f"- [{article.get('title')}]({article.get('url')})\n"
                suggestions_md += "\n"

        duplicate_md = ""
        if duplicate_detected:
            bot_reply = f"**❌ Duplicate Detected!** This identical issue was already reported and tracked here: **#{duplicate_ref['id']} ({duplicate_ref['title']})**. \n\n*Closing this thread automatically to keep the repository clean!*"
            checklist_md = "" # Wipe out checklist if closing

        markdown_body = (
            "🤖 **OpenIssue AI Automated Triage**\n\n"
            f"**Classification:** `{classification_type}` (_Confidence: {int(confidence * 100)}%_)\n"
            f"**Priority:** {p_icon} `{priority_level}`\n\n"
            "--- \n\n"
        )
        
        if duplicate_detected:
            markdown_body += f"{bot_reply}\n\n---\n*This is an automated administrative action by OpenIssue AI.*"
        else:
            markdown_body += f"{checklist_md}### Assistant Reply\n{bot_reply}\n{suggestions_md}---\n*This is an automated response from the OpenIssue AI Triage System.*"

        # Post the comment
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(f"{base_api_url}/comments", headers=headers, json={"body": markdown_body})
                logger.info(f"Successfully posted triage comment on {owner}/{repo}/issues/{issue_num}")
        except Exception as e:
            logger.error(f"Error posting comment: {str(e)}")
