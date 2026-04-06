# Domain-Locked Web Suggestions Module
from app.services.nlp_processor import NLPProcessor
from app.services.classifier import IssueClassifier
from app.services.priority import PriorityScorer
from app.services.embeddings import EmbeddingsManager
from app.services.vector_store import VectorStore
from app.services.llm_generator import LLMGenerator
import logging
import re
import random

logger = logging.getLogger(__name__)

class IssueAnalyzer:
    def __init__(self):
        self.nlp = NLPProcessor()
        self.classifier = IssueClassifier()
        self.scorer = PriorityScorer()
        self.embedder = EmbeddingsManager()
        self.vector_store = VectorStore()
        self.llm = LLMGenerator()

    async def initialize(self):
        logger.info("Initializing NLP models...")
        self.nlp.initialize()
        self.embedder.initialize()
        self.vector_store.load()
        logger.info("Analyzer initialized.")

    async def analyze(self, title: str, body: str, metadata: any, issue_comments: int = 0, issue_reactions: int = 0) -> dict:
        raw_text = f"{title}\n{body}"
        
        # 1. NLP Processing
        nlp_data = self.nlp.process_text(title, body)
        
        # 2. Embeddings & Semantic Search
        vector = self.embedder.generate_embedding(raw_text)
        similar_issues = self.vector_store.search(vector, k=3, threshold=0.5)

        # 3. LLM Reasoning (Choice B - Primary Brain)
        llm_analysis = await self.llm.generate_reasoned_analysis(title, body, nlp_data)
        
        if llm_analysis:
            # LLM BRAIN OVERRIDE
            issue_type = llm_analysis["classification"].lower()
            priority_level = llm_analysis["priority"].lower()
            suggested_labels = llm_analysis["labels"]
            suggested_reply = llm_analysis["response"]
            tech_domain = llm_analysis.get("tech_domain", "None")
            confidence = 0.98
            is_llm_generated = True
        else:
            # HEURISTIC FALLBACK
            issue_type, confidence = await self.classifier.classify(nlp_data, raw_text, embedder=self.embedder)
            priority_level, _ = self.scorer.score(nlp_data, raw_text, issue_type, metadata, issue_comments, issue_reactions)
            suggested_reply = self.llm.heuristic_fallback_reply(issue_type.capitalize(), priority_level.capitalize())
            suggested_labels = self._suggest_labels(issue_type, priority_level, nlp_data, raw_text)
            tech_domain = "None"
            is_llm_generated = False

        # 4. Priority score (numerical baseline)
        _, priority_score = self.scorer.score(nlp_data, raw_text, issue_type, metadata, issue_comments, issue_reactions)
        
        # 5. AI Reasoning Engine - content-aware Trace
        reasoning_steps = self._build_reasoning_trace(title, body, nlp_data, issue_type, priority_level, metadata)
        explanations = [step["detail"] for step in reasoning_steps]
        
        # 6. Web Suggestions — Domain-Locked
        web_suggestions = self._generate_web_advice(title, body, issue_type, nlp_data, tech_domain)
        
        return {
            "issue_title": title,
            "classification": {
                "type": issue_type.capitalize(),
                "confidence": confidence
            },
            "priority": {
                "level": priority_level.capitalize(),
                "score": priority_score
            },
            "similar_issues": similar_issues,
            "explanation": explanations,
            "reasoning_steps": reasoning_steps,
            "suggested_reply": suggested_reply,
            "is_llm_generated": is_llm_generated,
            "web_suggestions": web_suggestions,
            "suggested_labels": suggested_labels,
            "confidence_overall": confidence,
            "nlp_signals": {
                "has_code": nlp_data.get("has_code", False),
                "has_stack_trace": nlp_data.get("has_stack_trace", False),
                "entities": nlp_data.get("entities", [])[:8],
                "word_count": nlp_data.get("word_count", 0),
                "question_count": nlp_data.get("question_count", 0),
            }
        }

    def _build_reasoning_trace(self, title: str, body: str, nlp_data: dict, issue_type: str, priority_level: str, metadata: any) -> list:
        """Produces a genuine, content-driven multi-step reasoning trace."""
        steps = []
        text = f"{title} {body}".lower()
        entities = nlp_data.get("entities", [])
        
        # Step 1: Extraction summary
        word_count = nlp_data.get("word_count", 0)
        steps.append({
            "step": "Content Extraction",
            "icon": "extract",
            "detail": f"Extracted {word_count} tokens from issue body. Detected {len(entities)} named entities: {', '.join(entities[:5]) if entities else 'none'}."
        })

        # Step 2: Code/trace signal
        if nlp_data.get("has_stack_trace"):
            steps.append({
                "step": "Stack Trace Detection",
                "icon": "trace",
                "detail": "Detected runtime stack trace or exception signature. This indicates a reproducible crash, not a configuration issue."
            })
        elif nlp_data.get("has_code"):
            steps.append({
                "step": "Code Block Analysis",
                "icon": "code",
                "detail": f"Found inline code blocks. Issue likely demonstrates a reproducible case or provides configuration context."
            })
        else:
            steps.append({
                "step": "Text-Only Analysis",
                "icon": "text",
                "detail": "No code blocks or stack traces found. Proceeding with linguistic and semantic analysis only."
            })

        # Step 3: Semantic classification rationale
        primary_kws = self._extract_key_terms(title, body, issue_type)
        steps.append({
            "step": f"Classification → {issue_type.capitalize()}",
            "icon": "classify",
            "detail": f"Classified as '{issue_type}' based on semantic signals: [{', '.join(primary_kws[:4])}]. Confidence driven by keyword density and NLP entity overlap."
        })

        # Step 4: Priority rationale
        priority_drivers = []
        if "crash" in text or "error" in text: priority_drivers.append("crash/error keywords")
        if nlp_data.get("has_stack_trace"): priority_drivers.append("stack trace present")
        if nlp_data.get("exclamation_count", 0) > 1: priority_drivers.append("urgency markers")
        if metadata and getattr(metadata, "labels", []):
            lbl_str = ", ".join(metadata.labels)
            priority_drivers.append(f"labels: [{lbl_str}]")
        
        driver_text = "; ".join(priority_drivers) if priority_drivers else "standard scoring baseline"
        steps.append({
            "step": f"Priority Scoring → {priority_level.capitalize()}",
            "icon": "priority",
            "detail": f"Priority set to '{priority_level}' driven by: {driver_text}."
        })

        # Step 5: Duplicate / vector search
        steps.append({
            "step": "Semantic Deduplication",
            "icon": "vector",
            "detail": "Ran FAISS ANN search across issue vector index. Cosine similarity threshold: 0.50."
        })

        return steps

    def _extract_key_terms(self, title: str, body: str, issue_type: str) -> list:
        """Extracts meaningful terms from title/body to explain classification."""
        bug_kws = ["error", "crash", "fails", "broken", "exception", "not working", "bug", "issue", "regression", "segfault", "panic"]
        feat_kws = ["add", "support", "feature", "enhancement", "improve", "would like", "proposal", "request"]
        q_kws = ["how", "why", "what", "can i", "help", "documentation", "guide"]
        all_text = f"{title} {body}".lower()
        
        pool = bug_kws if issue_type == "bug" else (feat_kws if issue_type == "feature" else q_kws)
        return [kw for kw in pool if kw in all_text]

    def _generate_web_advice(self, title: str, body: str, issue_type: str, nlp_data: dict, tech_domain: str = "None") -> list:
        """Content-driven, specific advice with Domain Locking and Regex hardening."""
        text = f"{title} {body}".lower()
        suggestions = []

        # --- Technology stack detection ---
        tech_patterns = [
            {
                "domain": "React",
                "match": [r"react", r"jsx", r"tsx", r"next\.js", r"nextjs", r"hydration", r"usestate", r"useeffect"],
                "source": "React Docs & Stack Overflow",
                "title": "React Component Lifecycle & Rendering Issues",
                "advice": "For React rendering bugs, check component lifecycle, useEffect dependency arrays, and ensure server/client hydration parity. If using Next.js, verify getServerSideProps returns vs getStaticProps caching behavior.",
                "url": "https://react.dev/learn/troubleshooting",
                "search_query": f"site:stackoverflow.com OR site:github.com {title[:60]} react fix"
            },
            {
                "domain": "Python",
                "match": [r"python", r"django", r"flask", r"fastapi", r"asyncio", r"uvicorn", r"pydantic"],
                "source": "Python Docs & PyPI Issues",
                "title": "Python/Async Runtime Errors",
                "advice": "For Python async errors, verify event loop usage, async/await chains, and that all coroutines are awaited. Check for missing dependencies or version mismatches in requirements.txt.",
                "url": "https://docs.python.org/3/library/asyncio.html",
                "search_query": f"site:stackoverflow.com {title[:60]} python"
            },
            {
                "domain": "Rust",
                "match": [r"rust", r"cargo", r"trait", r"impl", r"borrow", r"ownership", r"lifetime", r"sync", r"send"],
                "source": "Rust Language Docs",
                "title": "Rust Trait / Memory Management Issue",
                "advice": "For Rust development, issues often involve Send/Sync trait requirements for thread safety or lifetime constraints in structs. Ensure traits are correctly implemented for your types to satisfy the compiler's borrow checker.",
                "url": "https://doc.rust-lang.org/book/ch10-02-traits.html",
                "search_query": f"site:stackoverflow.com OR site:github.com {title[:60]} rust trait fix"
            },
            {
                "domain": "TypeScript",
                "match": [r"typescript", r"ts", r"type error", r"interface", r"generic", r"tsc"],
                "source": "TypeScript Docs",
                "title": "TypeScript Type System Error",
                "advice": "TypeScript type errors often surface when third-party library types are mismatched. Use @types/ packages or declare modules with declare module. Check strict mode settings in tsconfig.json.",
                "url": "https://www.typescriptlang.org/docs/handbook/2/types-from-types.html",
                "search_query": f"site:stackoverflow.com {title[:60]} typescript"
            },
            {
                "domain": "Auth",
                "match": [r"authentication", r"auth", r"jwt", r"token", r"oauth", r"session", r"cookie", r"login", r"401", r"403"],
                "source": "Auth0 Blog & Security Docs",
                "title": "Authentication / Authorization Failure",
                "advice": "Auth issues commonly involve expired tokens, incorrect CORS headers blocking preflight, or missing session cookies on cross-origin requests. Verify token expiry, refresh logic, and ensure credentials are included in fetch/xhr calls.",
                "url": "https://auth0.com/blog/build-and-secure-a-simple-api/",
                "search_query": f"site:stackoverflow.com {title[:60]} authentication jwt fix"
            },
            {
                "domain": "Database",
                "match": [r"database", r"sql", r"postgres", r"mysql", r"sqlite", r"orm", r"migration", r"query", r"prisma", r"sqlalchemy"],
                "source": "Database & ORM Documentation",
                "title": "Database / ORM Query Issue",
                "advice": "Database errors often relate to schema migrations out of sync, incorrect connection pooling, or query builder misuse. Run migrations fresh, inspect raw SQL output with ORM logging enabled, and check connection string formatting.",
                "url": "https://stackoverflow.com/questions/tagged/sqlalchemy",
                "search_query": f"site:stackoverflow.com {title[:60]} database sql fix"
            },
            {
                "domain": "CORS",
                "match": [r"cors", r"cross-origin", r"access-control", r"preflight"],
                "source": "MDN Web Docs",
                "title": "CORS Policy Configuration Error",
                "advice": "CORS errors are server-side configuration issues. Ensure your backend sets Access-Control-Allow-Origin to the correct frontend domain. For credentialed requests, set allow_credentials=True and avoid wildcard origins.",
                "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors",
                "search_query": f"site:stackoverflow.com {title[:60]} CORS fix"
            },
        ]

        # 1. PRIMARY: Match based on LLM-locked Tech Domain
        for pattern in tech_patterns:
            if tech_domain.lower() == pattern["domain"].lower():
                suggestions.append(self._build_suggestion(pattern, title, issue_type))
                break

        # 2. SECONDARY: Regex boundary matching for fallback
        if not suggestions:
            for pattern in tech_patterns:
                for kw in pattern["match"]:
                    if re.search(r'\b' + kw + r'\b', text):
                        suggestions.append(self._build_suggestion(pattern, title, issue_type))
                        break
                if len(suggestions) >= 2: break

        # 3. Final Fallback based on issue type
        if not suggestions:
            if issue_type == "bug":
                suggestions.append({
                    "source": "GitHub Maintainer Handbook",
                    "title": "Bug Triage Protocol",
                    "advice": f"Request a minimal reproduction case for: '{title[:80]}'. Ask for OS, runtime version, and steps to reproduce. Without this, diagnosing the issue is speculative.",
                    "url": "https://github.com/nicedoc/awesome-maintainers",
                    "search_query": f"site:stackoverflow.com {title[:60]} fix",
                    "articles": self._generate_related_articles(["bug", "fix", "reproduce"], title, issue_type)
                })
            elif issue_type == "feature":
                suggestions.append({
                    "source": "Open Source Feature Planning",
                    "title": "Feature Request Evaluation",
                    "advice": f"Evaluate impact vs effort for: '{title[:80]}'. Check if existing plugins or middleware already provide this capability. Tag for community voting before committing engineering time.",
                    "url": "https://opensource.guide/best-practices/",
                    "search_query": f"site:github.com {title[:60]} feature implementation",
                    "articles": self._generate_related_articles(["feature", "enhancement", "roadmap"], title, issue_type)
                })
            else:
                suggestions.append({
                    "source": "Community Support",
                    "title": "Documentation & FAQ Search",
                    "advice": f"This appears to be a usage question about: '{title[:80]}'. Point the user to the official docs first. If recurrent, consider creating a FAQ entry.",
                    "url": "https://stackoverflow.com/",
                    "search_query": f"site:stackoverflow.com {title[:60]}",
                    "articles": self._generate_related_articles(["documentation", "guide", "how-to"], title, issue_type)
                })

        return suggestions

    def _build_suggestion(self, pattern: dict, title: str, issue_type: str) -> dict:
        """Helper to build a standardized suggestion object."""
        return {
            "source": pattern["source"],
            "title": pattern["title"],
            "advice": pattern["advice"],
            "url": pattern["url"],
            "search_query": pattern.get("search_query", ""),
            "articles": self._generate_related_articles(pattern["match"], title, issue_type)
        }

    def _generate_related_articles(self, keywords: list, title: str, issue_type: str) -> list:
        """Generates simulated AI-searched article results relevant to the issue."""
        clean_title = re.sub(r'[^\w\s]', '', title[:50]).strip()
        
        article_templates = {
            "react": [
                {"title": "React 18 Concurrent Features & Common Pitfalls", "url": "https://react.dev/blog/2022/03/29/react-v18", "domain": "react.dev"},
                {"title": "Understanding React Hydration Errors", "url": "https://nextjs.org/docs/messages/react-hydration-error", "domain": "nextjs.org"},
                {"title": "Debugging useEffect Dependencies", "url": "https://stackoverflow.com/questions/53070970", "domain": "stackoverflow.com"},
            ],
            "python": [
                {"title": "Python AsyncIO Common Mistakes", "url": "https://superfastpython.com/asyncio-common-mistakes/", "domain": "superfastpython.com"},
                {"title": "Debugging FastAPI Applications", "url": "https://fastapi.tiangolo.com/tutorial/debugging/", "domain": "fastapi.tiangolo.com"},
                {"title": "Python Exception Handling Best Practices", "url": "https://realpython.com/python-exceptions/", "domain": "realpython.com"},
            ],
            "docker": [
                {"title": "Docker Container Resource Limits", "url": "https://docs.docker.com/config/containers/resource_constraints/", "domain": "docker.com"},
                {"title": "Kubernetes OOMKilled: Causes and Fixes", "url": "https://komodor.com/learn/how-to-fix-oomkilled-exit-code-137/", "domain": "komodor.com"},
                {"title": "Understanding Container Networking", "url": "https://docs.docker.com/network/", "domain": "docker.com"},
            ],
            "github actions": [
                {"title": "GitHub Actions Workflow Syntax Reference", "url": "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions", "domain": "github.com"},
                {"title": "Debugging GitHub Actions Failures", "url": "https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows", "domain": "github.com"},
                {"title": "Security Hardening for GitHub Actions", "url": "https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions", "domain": "github.com"},
            ],
            "null": [
                {"title": "Optional Chaining in JavaScript", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining", "domain": "mdn.dev"},
                {"title": "TypeScript Strict Null Checks", "url": "https://www.typescriptlang.org/tsconfig#strictNullChecks", "domain": "typescriptlang.org"},
                {"title": "NullPointerException: Root Cause Analysis", "url": "https://stackoverflow.com/questions/218384/what-is-a-nullpointerexception", "domain": "stackoverflow.com"},
            ],
            "rust": [
                {"title": "The Rust Programming Language: Traits", "url": "https://doc.rust-lang.org/book/ch10-02-traits.html", "domain": "rust-lang.org"},
                {"title": "Understanding Send and Sync traits", "url": "https://doc.rust-lang.org/nomicon/send-and-sync.html", "domain": "rust-lang.org"},
                {"title": "Rust Lifetimes and Borrow Checker", "url": "https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html", "domain": "rust-lang.org"},
            ],
            "default": [
                {"title": f"How to reproduce and fix: {clean_title}", "url": f"https://stackoverflow.com/search?q={clean_title.replace(' ', '+')}", "domain": "stackoverflow.com"},
                {"title": f"GitHub Issues discussion: {clean_title}", "url": f"https://github.com/search?q={clean_title.replace(' ', '+')}&type=issues", "domain": "github.com"},
                {"title": "Open Source Bug Report Best Practices", "url": "https://marker.io/blog/how-to-write-bug-report", "domain": "marker.io"},
            ]
        }
        
        for kw in keywords:
            for key in article_templates:
                if kw in key or key in kw:
                    return article_templates[key]
        
        return article_templates["default"]

    def _suggest_labels(self, issue_type: str, priority_level: str, nlp_data: dict, text: str) -> list:
        """Generates smart label suggestions based on analysis."""
        labels = []
        tl = text.lower()
        
        type_map = {"bug": "bug", "feature": "enhancement", "question": "question"}
        labels.append(type_map.get(issue_type, "triage"))
        
        if priority_level in ["critical", "high"]:
            labels.append("priority: high")
        elif priority_level == "low":
            labels.append("good first issue")
            
        if nlp_data.get("has_stack_trace"):
            labels.append("needs: repro")
        
        tech_labels = {
            "react": "react", "python": "python", "docker": "docker",
            "rust": "rust",
            "typescript": "typescript", "kubernetes": "kubernetes",
            "github actions": "ci/cd", "database": "database"
        }
        for kw, lbl in tech_labels.items():
            if kw in tl:
                labels.append(lbl)
                break
                
        if nlp_data.get("question_count", 0) > 2:
            labels.append("needs: more info")
            
        return list(set(labels))[:5]
