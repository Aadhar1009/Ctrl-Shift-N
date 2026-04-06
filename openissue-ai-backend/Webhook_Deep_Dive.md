# Webhook Deep Dive: The Pulse of OpenIssue AI

The GitHub Webhook is the "Nervous System" of OpenIssue AI. It allows your backend to react in real-time to events on GitHub. This document explains the **Bit-by-Bit** technical implementation of our secure, production-grade webhook system.

---

## 🛡️ Bit 1: The Security Layer (HMAC Verification)
**What it is:** A cryptographic handshake that ensures the request actually came from GitHub.

**How we did it:**
The code in `github_webhook.py` extracts the `X-Hub-Signature-256` header. We then use your `GITHUB_WEBHOOK_SECRET` to calculate a hash of the raw request body using the **HMAC-SHA256** algorithm.
-   **Old Prototype**: Accepted any POST request.
-   **New Production**: If `Calculated_Hash != Received_Hash`, the request is rejected with a `401 Unauthorized`. This prevents malicious actors from "pretending" to be GitHub and wasting your AI credits.

---

## ⚡ Bit 2: The Async Orchestrator (FastAPI BackgroundTasks)
**What it is:** A "Fire and Forget" architecture that keeps the system fast and stable.

**How we did it:**
GitHub has a strict timeout (usually 10 seconds). LLM reasoning can take 2-5 seconds. If we waited for the AI to finish before replying to GitHub, we risked a timeout.
-   **Bit-by-Bit Flow**: 
    1.  Request arrives.
    2.  Backend validates the signature.
    3.  Backend immediately sends a `200 OK` + `{"status": "processing"}`.
    4.  The `analyze_and_reply` logic is handed to a **Background Worker**.
    5.  GitHub is happy, and the AI "thinks" in parallel.

---

## 🔍 Bit 3: Event Filtering & Logic
**What it is:** Ensuring the bot only acts when it needs to.

**How we did it:**
GitHub sends webhooks for *everything* (comments, PRs, stars). We implemented a strict filter:
```python
if payload.get("action") == "opened":
    # Trigger AI pipeline
```
This is critical. Without this, if the bot posted a comment, GitHub would send a "comment_created" webhook, the bot would analyze the comment, post another comment, and enter an **infinite loop**. We've "locked" the primary triage to the **Issue Opening** event.

---

## 🧠 Bit 4: Integrating the Multi-Choice AI Brain
**What it is:** Bringing Choice C + B into the real-world flow.

**How we did it:**
Inside the webhook's background task, we call `IssueAnalyzer.analyze()`. 
-   **Choice C (Vector Math)** is called first to get a mathematical baseline.
-   **Choice B (Gemini)** is called to perform the high-level reasoning.
-   The webhook logic then formats these two results into a **Professional GitHub Comment** template.

---

## 🛰️ Bit 5: The "Reply" Service (REST Integration)
**What it is:** Posting the analysis back to GitHub.

**How we did it:**
We use the `httpx` library to send an authenticated `POST` request to:
`https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments`
We include your `GITHUB_TOKEN` in the headers. This is the final step where the "AI Analysis" becomes a "Public Comment" for the world to see.

---

### 🛡️ Why This Design Wins:
1.  **Security**: HMAC signatures make it un-hackable.
2.  **Concurrency**: Background tasks mean it can handle 100s of issues at once.
3.  **Reliability**: Precise event filtering prevents "Bot Loops."
4.  **Production Readiness**: This is the exact architecture used by top-tier tools like Sentry or Linear.
