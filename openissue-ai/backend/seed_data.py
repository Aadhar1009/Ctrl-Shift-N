"""Seed data for the vector store - realistic GitHub issues."""

SEED_ISSUES = [
    {
        "id": "1",
        "title": "Application crashes on startup with NullPointerException",
        "body": """When I try to start the application, it immediately crashes with a NullPointerException.

Stack trace:
```
java.lang.NullPointerException
    at com.app.core.Initializer.init(Initializer.java:45)
    at com.app.Main.main(Main.java:12)
```

Environment:
- Java 17
- macOS 14.0
- Version 2.3.1

This is blocking our production deployment.""",
        "type": "bug",
        "priority": "critical"
    },
    {
        "id": "2", 
        "title": "Add dark mode support",
        "body": """It would be great to have a dark mode option in the settings.

Many users work late at night and the bright interface can be straining on the eyes.

Suggested implementation:
- Add toggle in settings
- Persist preference
- Support system preference detection""",
        "type": "feature",
        "priority": "medium"
    },
    {
        "id": "3",
        "title": "How do I configure the database connection?",
        "body": """I'm new to this project and I can't figure out how to set up the database.

The documentation mentions a config file but I don't see where to put my credentials.

Can someone point me to the right documentation or provide an example?""",
        "type": "question",
        "priority": "low"
    },
    {
        "id": "4",
        "title": "Memory leak in image processing module",
        "body": """After processing about 100 images, memory usage climbs to 8GB and never goes down.

I've attached a heap dump showing the issue. The ImageProcessor class seems to be holding references to all processed images.

Steps to reproduce:
1. Start the application
2. Process 100+ images
3. Observe memory in task manager

This is causing our server to crash every few hours.""",
        "type": "bug",
        "priority": "high"
    },
    {
        "id": "5",
        "title": "Support for GraphQL API",
        "body": """We'd love to see GraphQL support alongside the existing REST API.

Benefits:
- More efficient data fetching
- Better typing support
- Reduced over-fetching

Happy to contribute if there's interest!""",
        "type": "feature",
        "priority": "medium"
    },
    {
        "id": "6",
        "title": "Authentication fails with special characters in password",
        "body": """Users with special characters like @, #, or $ in their passwords cannot log in.

Error message: "Invalid credentials"

But when I change to a simple password, login works fine.

This seems like an encoding issue. Urgent as it's affecting many users.""",
        "type": "bug",
        "priority": "high"
    },
    {
        "id": "7",
        "title": "Add export to PDF functionality",
        "body": """Users have been requesting the ability to export reports as PDF.

Requirements:
- Include all charts and graphs
- Proper formatting
- Header/footer with date
- Page numbers

This would help with sharing reports in meetings.""",
        "type": "feature",
        "priority": "medium"
    },
    {
        "id": "8",
        "title": "What's the recommended Node.js version?",
        "body": """The README doesn't specify which Node.js version to use.

I tried with Node 18 and got some warnings, but it seems to work.

Should I use Node 16, 18, or 20?""",
        "type": "question",
        "priority": "low"
    },
    {
        "id": "9",
        "title": "Security vulnerability in dependency",
        "body": """npm audit is reporting a critical vulnerability:

```
lodash  <4.17.21
Severity: critical
Prototype Pollution - https://github.com/advisories/GHSA-jf85-cpcp-j695
```

This needs to be addressed ASAP as it could allow remote code execution.""",
        "type": "bug",
        "priority": "critical"
    },
    {
        "id": "10",
        "title": "Implement webhook notifications",
        "body": """We need the ability to send webhook notifications when certain events occur.

Events to support:
- New user registration
- Order completed
- Payment failed
- Inventory low

This would help integrate with Slack, Discord, and other services.""",
        "type": "feature",
        "priority": "medium"
    },
    {
        "id": "11",
        "title": "API returns 500 error on large payloads",
        "body": """When sending requests larger than 1MB, the API returns a 500 Internal Server Error.

Expected: Return 413 Payload Too Large with helpful message
Actual: 500 error with no body

This is confusing for API consumers.""",
        "type": "bug",
        "priority": "medium"
    },
    {
        "id": "12",
        "title": "How to run tests locally?",
        "body": """I cloned the repo and want to run the tests before submitting a PR.

I tried:
- npm test (not found)
- yarn test (errors)
- make test (no makefile)

What's the correct command?""",
        "type": "question",
        "priority": "low"
    },
    {
        "id": "13",
        "title": "Add multi-language support (i18n)",
        "body": """Our user base is expanding globally and we need internationalization support.

Languages needed:
- Spanish
- French  
- German
- Japanese
- Chinese (Simplified)

We should use a standard i18n library and have translation files that contributors can help with.""",
        "type": "feature",
        "priority": "high"
    },
    {
        "id": "14",
        "title": "Login page shows blank after OAuth redirect",
        "body": """After authenticating with Google OAuth, users are redirected back to a blank login page.

The URL has the correct tokens but the page doesn't render.

Console shows:
```
Uncaught TypeError: Cannot read property 'user' of undefined
```

This broke in version 2.4.0.""",
        "type": "bug",
        "priority": "high"
    },
    {
        "id": "15",
        "title": "Improve search performance",
        "body": """Search is very slow when we have more than 10,000 records.

Current: ~5 seconds
Expected: <500ms

We should consider:
- Adding database indexes
- Implementing elasticsearch
- Caching frequent searches""",
        "type": "feature",
        "priority": "medium"
    },
    {
        "id": "16",
        "title": "TypeError when clicking submit button twice",
        "body": """If you click the submit button twice quickly, you get:

```
TypeError: Cannot read properties of null (reading 'value')
    at handleSubmit (Form.js:42)
```

Workaround: Add debouncing or disable button after first click.""",
        "type": "bug",
        "priority": "low"
    },
    {
        "id": "17",
        "title": "Add rate limiting to API",
        "body": """We need rate limiting to prevent abuse and ensure fair usage.

Proposed limits:
- 100 requests/minute for free tier
- 1000 requests/minute for paid tier
- Custom limits for enterprise

Should return 429 with Retry-After header when exceeded.""",
        "type": "feature",
        "priority": "high"
    },
    {
        "id": "18",
        "title": "Database migration fails on PostgreSQL 15",
        "body": """The migration script fails on PostgreSQL 15 with:

```
ERROR: syntax error at or near "GROUP"
LINE 42: ...GROUP BY user_id...
```

This is because of the new reserved keyword handling in PG15.

Workaround: Use double quotes around GROUP.

Blocking new deployments.""",
        "type": "bug",
        "priority": "critical"
    },
    {
        "id": "19",
        "title": "Can I use this with Docker?",
        "body": """Is there an official Docker image or Dockerfile?

I want to deploy this in Kubernetes but need a containerized version.

If there's no official image, any tips on creating one?""",
        "type": "question",
        "priority": "low"
    },
    {
        "id": "20",
        "title": "Add keyboard shortcuts",
        "body": """Power users would benefit from keyboard shortcuts:

- Ctrl+S: Save
- Ctrl+N: New item
- Ctrl+/: Open command palette
- Esc: Close modal

This would greatly improve productivity for users who prefer keyboard navigation.""",
        "type": "feature",
        "priority": "low"
    }
]

def seed_vector_store():
    """Seed the vector store with sample issues."""
    from vector_store import get_vector_store
    
    store = get_vector_store()
    
    if store.get_stats()["total_issues"] >= len(SEED_ISSUES):
        print(f"Vector store already seeded with {store.get_stats()['total_issues']} issues")
        return
    
    print(f"Seeding vector store with {len(SEED_ISSUES)} sample issues...")
    store.add_issues_batch(SEED_ISSUES)
    print("Seeding complete!")

if __name__ == "__main__":
    seed_vector_store()
