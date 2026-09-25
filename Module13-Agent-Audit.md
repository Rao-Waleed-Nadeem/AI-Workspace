# AI Workspace — Module 13 Complete Agent Audit & Repair Specification

## PURPOSE

This file is the implementation checklist for **Module 13 — Production Architecture & Hardening**.

The AI agent must:
1. inspect the existing AI Workspace;
2. determine what Module 13 already contains;
3. find missing, broken, duplicated, unsafe, or incomplete work;
4. modify only what is necessary;
5. preserve existing architecture and functionality;
6. test changed behavior;
7. report exactly what was checked, changed, skipped, and why.

**Do not rebuild Module 13 from scratch.**
**Do not assume existing code is correct merely because it exists.**
**Do not blindly overwrite existing files.**

The repository state is authoritative for implementation. This document defines the target state and audit checklist.

---

# 1. PROJECT CONTEXT

Project: **AI Workspace — AI Research & Knowledge Assistant**

Purpose: a deliberately small Full Stack AI application used to learn production-oriented AI application engineering.

Stack:
- Frontend: Next.js + TypeScript + React + Tailwind
- Frontend convention: `app/`, not `src/`
- Backend: FastAPI + Python
- ORM: SQLAlchemy
- Migrations: Alembic
- Database: PostgreSQL
- Vector capability: pgvector
- Primary AI provider: Groq
- Authentication: JWT
- Existing AI features: chat, streaming, structured output, tools, vision, documents, embeddings/vector retrieval/RAG, memory, image generation, speech

Environment:
- Windows
- Project root: `D:\AI Workspace`
- Backend venv: `backend\.venv`
- PostgreSQL commonly runs through Docker
- Free/low-cost AI usage is preferred
- Do not introduce Ollama unless explicitly requested
- Do not introduce unnecessary infrastructure

---

# 2. NON-NEGOTIABLE RULES

## Architecture

Preferred backend flow:

```text
Frontend
  ↓
API Route
  ↓
Schema / Validation
  ↓
Service
  ↓
Repository
  ↓
Database
```

AI flow:

```text
Service
  ↓
Provider abstraction
  ↓
Concrete provider
```

Routes must not contain substantial:
- SQL/database logic
- business logic
- provider-specific logic
- filesystem business logic
- large prompt-building logic

## Responsibilities

Routes: HTTP input/auth/service call/HTTP response.

Schemas: validation and response structure.

Services: business logic and orchestration.

Repositories: database access.

Providers: external AI API communication.

Models: database structure.

## Do not over-engineer

Do NOT introduce Redis, Kafka, Kubernetes, Celery, LangGraph, multi-agent systems, complex observability platforms, or microservices unless explicitly required.

In-memory rate limiting is acceptable for this single-instance/local learning project. Document that multi-instance production would require a shared limiter/store, but do not add Redis now.

## Continuation rule

Before editing:

```text
1. Inspect repository
2. Inspect current files
3. Detect existing Module 13 work
4. Compare against this specification
5. Identify gaps
6. Modify only gaps
7. Test
8. Report
```

Never duplicate existing functionality.

---

# 3. MODULE 13

```text
13.1 Architecture Audit
13.2 Error Handling
13.3 Logging
13.4 Configuration & Secrets
13.5 Rate Limiting / Abuse Protection
13.6 AI Cost / Token Awareness
13.7 Database Indexes & Query Review
13.8 Security Review
13.9 Testing Strategy
```

Module 13 is complete only when all nine areas have been reviewed, required fixes are implemented, relevant tests pass, and a final audit report is produced.

---

# 4. FILES TO REVIEW

Inspect these first.

## Core

```text
backend/app/core/config.py
backend/app/core/dependencies.py
backend/app/core/security.py
backend/app/core/errors.py
backend/app/core/error_handlers.py
backend/app/core/logging_config.py
backend/app/core/rate_limit.py
backend/app/core/token_budget.py
backend/app/core/ai_usage.py
```

Create missing files only when justified.

## Main

```text
backend/app/main.py
```

Review middleware, exception handlers, CORS, startup, router registration, public endpoints, and security headers.

## Routes

Inspect all route files under:

```text
backend/app/api/
backend/app/routes/
```

Priority:

```text
auth.py
chat.py
files.py
images.py
memory.py
speech.py
text_to_speech.py
```

Also inspect any additional route files.

## Services

Inspect all of:

```text
backend/app/services/
```

Priority:

```text
chat_service.py
auth_service.py
document_service.py
rag_service.py
retrieval_service.py
memory_service.py
image_service.py
speech_to_text_service.py
text_to_speech_service.py
```

## Repositories

Inspect:

```text
backend/app/repositories/
```

Priority:

```text
chat_repository.py
message_repository.py
document_repository.py
document_chunk_repository.py
memory_repository.py
```

Also inspect user/image/attachment repositories if present.

## Models

Inspect:

```text
backend/app/models/
```

Priority:

```text
user.py
chat.py
message.py
attachment.py
document.py
document_chunk.py
memory.py
generated_image.py
```

## Providers

Inspect:

```text
backend/app/providers/
```

Priority:

```text
base_provider.py
groq_provider.py
factory.py
groq_speech_to_text_provider.py
groq_text_to_speech_provider.py
```

Also inspect image providers.

## Tools

Inspect:

```text
backend/app/tools/
```

Especially calculator and the tool registry/execution code.

## Prompts

Inspect:

```text
backend/app/prompts/
```

Especially RAG, system, tool, vision, and structured-output prompts.

## Database

Inspect:

```text
backend/alembic/
backend/alembic/versions/
```

Always determine the actual current Alembic head before adding a migration.

## Frontend

Inspect:

```text
frontend/lib/api.ts
frontend/lib/auth.ts
frontend/lib/errors.ts
frontend/lib/useAuth.ts
```

Also inspect components that call AI endpoints, upload files, display errors, stream responses, handle images, speech, or memory.

## Configuration

Inspect:

```text
.env
.env.example
.gitignore
backend/requirements.txt
frontend/package.json
```

Never expose real secret values in the audit report.

---

# 5. LESSON 13.1 — ARCHITECTURE AUDIT

Verify:

```text
Frontend
 ↓
Route
 ↓
Schema
 ↓
Service
 ↓
Repository
 ↓
Database
```

and:

```text
Service
 ↓
Provider abstraction
 ↓
Concrete provider
```

Search route files for:

```text
db.query
db.execute
Session
Groq
httpx
requests
os.getenv
AI prompts
filesystem operations
business decisions
```

Routes should not contain substantial versions of these.

## Provider independence

Find direct provider construction such as:

```text
GroqProvider()
```

inside business services.

Prefer:

```text
BaseAIProvider
      ↑
GroqProvider
      ↑
factory
      ↑
service
```

Do not create duplicate factories.

## Large services

Review `chat_service.py`.

Do not split it merely because it is large. Extract only a clearly independent responsibility when extraction improves maintainability without changing behavior.

Document technical debt that is intentionally left untouched.

## Acceptance

- route responsibilities are clean;
- provider abstraction is preserved;
- no duplicate factories;
- service responsibilities are understandable;
- no unnecessary architecture was introduced.

---

# 6. LESSON 13.2 — ERROR HANDLING

Target response:

```json
{
  "error": {
    "code": "some_code",
    "message": "Human-readable message",
    "details": []
  }
}
```

Required categories:

```text
bad_request
unauthorized
forbidden
not_found
conflict
payload_too_large
unsupported_media_type
unprocessable_entity
rate_limited
provider_error
database_error
database_unavailable
internal_error
```

Prefer:

```text
backend/app/core/errors.py
backend/app/core/error_handlers.py
```

Base error:

```python
class AppError(Exception):
    status_code = 500
    code = "internal_error"
```

Specialized errors may include:

```text
ProviderError
DatabaseError
DatabaseUnavailableError
RateLimitError
```

Provider errors must not expose API keys or raw secrets.

Database errors must not expose SQL, connection strings, passwords, or stack traces to clients.

Operational DB failures should map to 503.

Validation errors should include structured field/message/type details.

Frontend `frontend/lib/errors.ts` should normalize API errors into a reusable `ApiError`. Avoid consuming `response.json()` twice.

Test invalid requests, auth failures, ownership failures, missing resources, invalid uploads, provider failures, DB failures, rate limits, and unexpected exceptions.

---

# 7. LESSON 13.3 — LOGGING

Logs should help diagnosis without leaking secrets.

Useful request fields:

```text
method
path
status
duration
```

Example:

```text
POST /chat/stream 200 1.42s
```

Never log:

```text
request body
Authorization header
JWT
API key
password
full uploaded document
full prompt
full AI response
```

Use INFO/WARNING/ERROR appropriately.

Be careful with exception tracebacks because third-party exceptions can contain sensitive values.

If a secret-redaction filter exists, ensure it does not suppress every message merely because it contains generic words such as `token`. Prefer not logging secret values in the first place and targeted redaction when needed.

Acceptance:

```text
normal request → useful log
4xx → warning
5xx → error
secrets → never logged
request body → never logged
authorization header → never logged
```

---

# 8. LESSON 13.4 — CONFIGURATION & SECRETS

Required environment configuration should include, where used:

```env
DATABASE_URL=
GROQ_API_KEY=
MODEL_NAME=
VISION_MODEL_NAME=
JWT_SECRET=
LOG_LEVEL=
CORS_ORIGINS=
AI_CONTEXT_WINDOW_TOKENS=
AI_MAX_INPUT_TOKENS=
AI_MAX_OUTPUT_TOKENS=
TOKEN_ESTIMATE_CHARS_PER_TOKEN=
AI_MAX_TOOL_CALLS=
AI_RATE_LIMIT_REQUESTS=
AI_RATE_LIMIT_WINDOW_SECONDS=
AUTH_RATE_LIMIT_REQUESTS=
AUTH_RATE_LIMIT_WINDOW_SECONDS=
```

Do not require every optional variable if the existing configuration architecture does not use it.

Real `.env` must be ignored by Git.

`.env.example` contains placeholders only.

Never hardcode:
- API keys
- JWT secrets
- database passwords
- user passwords

Required secrets should fail clearly when absent rather than silently using insecure defaults.

CORS must be explicit/configurable. Do not use wildcard origin with credentials.

---

# 9. LESSON 13.5 — RATE LIMITING

Protect expensive AI operations and auth endpoints.

## AI

Prefer per authenticated user.

Example configurable default:

```text
20 requests / 60 seconds
```

Apply to AI generation endpoints, not simple read endpoints.

## Auth

Prefer per client IP.

Example configurable default:

```text
10 requests / 60 seconds
```

Apply to register/login.

## Exceeded limit

Return:

```text
HTTP 429
code = rate_limited
Retry-After = N
```

Example:

```json
{
  "error": {
    "code": "rate_limited",
    "message": "Too many requests. Please try again later.",
    "details": []
  }
}
```

Do not add Redis in Module 13. Document its future need for multi-instance deployments.

---

# 10. LESSON 13.6 — AI COST / TOKEN AWARENESS

Even with free APIs, control:

```text
token usage
context window
chat history
prompt size
RAG context
tool definitions
tool calls
output size
```

Conceptual request:

```text
system prompt
+
chat history
+
memory
+
RAG context
+
tool definitions
+
current user message
+
output budget
```

must remain within a reasonable context budget.

## Token estimation

A provider-neutral estimator is acceptable.

Do NOT call character estimation exact tokenization.

Example configuration:

```env
TOKEN_ESTIMATE_CHARS_PER_TOKEN=4
```

## History

A token-aware history function should:

1. preserve the system message where possible;
2. prioritize recent conversation;
3. remove old messages when the budget is exceeded;
4. never remove the current user request;
5. never send unlimited history.

Target:

```text
trim_messages_to_budget(...)
```

## Budget

Example configurable project defaults:

```env
AI_CONTEXT_WINDOW_TOKENS=8192
AI_MAX_INPUT_TOKENS=6000
AI_MAX_OUTPUT_TOKENS=1200
```

Do not treat these as universal model limits.

## RAG

RAG context must have a hard total bound that includes:

```text
source labels
+
separators
+
chunk content
```

not only raw chunk characters.

## Tools

Bound tool-call loops.

Example:

```env
AI_MAX_TOOL_CALLS=3
```

Never allow an uncontrolled:

```text
LLM → tool → LLM → tool → ...
```

## Usage logging

If provider usage metadata exists, safely log:

```text
operation
prompt_tokens
completion_tokens
total_tokens
```

If not, use an estimate.

Never log the prompt itself.

Acceptance:

```text
short chat → works
long history → trimmed
large RAG context → bounded
tool calls → bounded
large request → useful error
usage logs → counts only
```

---

# 11. LESSON 13.7 — DATABASE INDEXES & QUERY REVIEW

Review foreign keys and actual query patterns before adding indexes.

Important relationships:

```text
User → Chat
Chat → Message
Message → Attachment
User → Document
Document → DocumentChunk
User → Memory
User → GeneratedImage
```

Common queries:

## Chats

```sql
WHERE user_id = ?
ORDER BY created_at DESC
```

Potential composite index:

```text
(user_id, created_at, id)
```

## Messages

```sql
WHERE chat_id = ?
ORDER BY id ASC
```

Potential:

```text
(chat_id, id)
```

## Documents

```sql
WHERE user_id = ?
ORDER BY created_at DESC
```

Potential:

```text
(user_id, created_at, id)
```

## Chunks

```sql
WHERE user_id = ?
AND document_id = ?
```

Potential:

```text
(user_id, document_id)
```

## Memory

Review user filtering and updated-time access. Preserve the existing one-current-value-per-user/key design.

## Attachments

Review whether:

```sql
WHERE message_id = ?
```

is common and indexed.

## Pagination

Avoid unrestricted `.all()` for growing user-facing collections.

Use:

```text
limit
offset
```

with reasonable bounds such as:

```text
limit: 1–100
offset: >= 0
```

Do not replace an existing correct cursor strategy with offset pagination.

## Ordering

Prefer deterministic ordering:

```text
created_at DESC, id DESC
```

when timestamps can collide.

## Vector queries

Review:

```text
embedding similarity
+
user ownership
+
document ownership
+
top-K
```

Never remove ownership filters for performance.

If an ANN index is added, verify:
- actual embedding dimension;
- actual distance metric;
- query operator;
- pgvector support.

For cosine distance, `vector_cosine_ops` is commonly appropriate, but verify the actual application query.

## Migration

Never edit old applied migrations.

Create a new migration with the actual current Alembic head.

Verify:

```text
upgrade
index existence
query behavior
```

and safely test downgrade in development when appropriate.

---

# 12. LESSON 13.8 — SECURITY REVIEW

Audit every item.

## Authentication

Check:

```text
registration
login
password hashing
JWT generation
JWT validation
expired JWT
invalid JWT
missing JWT
```

Never store plaintext passwords or log passwords.

## Authorization

Every user-owned resource must be scoped to current user:

```text
Chat
Message
Document
DocumentChunk
Memory
GeneratedImage
Attachment
```

Avoid insecure:

```python
get_by_id(resource_id)
```

without ownership enforcement.

Prefer ownership-aware queries or service checks.

## Uploads

Review:

```text
extension
MIME type
file size
content/signature
filename sanitization
generated storage name
ownership
storage exposure
```

Do not trust client filename/MIME/extension alone.

Do not publicly mount private upload directories.

## Prompts

Retrieved documents are untrusted content.

RAG prompt should establish that document content is reference material, not higher-priority instructions.

Never put secrets in prompts.

## Tools

Never allow arbitrary:

```text
eval()
exec()
os.system()
subprocess
shell commands
```

for AI-generated content.

Calculator should use a restricted evaluator/AST allowlist.

Tool registry should be allowlisted.

Arguments should be validated.

Tool loops should be bounded.

## Database

Prefer SQLAlchemy/parameterized queries.

Review raw SQL for injection.

Never expose database credentials.

## Secrets

Search source for suspicious patterns:

```text
api_key =
secret =
password =
token =
Bearer
sk-
```

Do not print discovered secret values in the final report.

If an actual secret is found:
1. do not echo it;
2. remove it from source;
3. move it to environment configuration;
4. recommend rotation if exposed/committed.

## CORS

Review:

```text
allow_origins
allow_credentials
allow_methods
allow_headers
```

Avoid wildcard origin with credentials.

## Security headers

At minimum consider:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

Do not add an oversized security framework.

---

# 13. LESSON 13.9 — TESTING STRATEGY

Do not build a huge framework.

Required categories:

```text
Unit
Integration
API
AI behavior
```

## Unit

Test deterministic logic:

```text
calculator
token estimation
message trimming
validation helpers
security helpers
```

Example files:

```text
backend/tests/unit/test_calculator.py
backend/tests/unit/test_token_budget.py
```

## Integration

Test multiple internal components:

```text
RAG context construction
repository + database
service + repository
```

Example:

```text
backend/tests/integration/test_rag_context.py
```

Do not require live external AI APIs for ordinary tests.

## API

Use FastAPI test client.

Test:

```text
root
register
login
protected endpoint without token
invalid token
wrong-resource ownership
validation failure
rate limit
```

Mock external providers where appropriate.

## AI behavior

Test deterministic application behavior rather than trying to prove an LLM is deterministic.

Examples:

```text
RAG prompt has document boundaries
RAG prompt treats documents as reference material
only allowed tools are registered
tool arguments are validated
history budget is respected
RAG context is bounded
```

## Organization

Preferred:

```text
backend/tests/
├── unit/
│   ├── test_calculator.py
│   └── test_token_budget.py
├── integration/
│   └── test_rag_context.py
├── api/
│   └── test_root.py
└── ai/
    └── test_rag_prompt.py
```

Add tests only where they protect real behavior.

## pytest

If not already configured:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

Use the existing dependency-management convention; do not create duplicate dependency files.

## Commands

From backend:

```powershell
python -m compileall -q app
python -m pytest -q
```

Focused:

```powershell
python -m pytest -q tests/unit
python -m pytest -q tests/integration
python -m pytest -q tests/api
python -m pytest -q tests/ai
```

If a test fails:
1. inspect the failure;
2. identify root cause;
3. fix root cause;
4. rerun focused test;
5. rerun relevant suite.

Never delete/weaken a failing test merely to get green.

---

# 14. CROSS-MODULE REGRESSION CHECK

Module 13 must not break earlier features.

Verify at least:

```text
Authentication
Chat
Streaming
Structured output
Tools
Vision
File upload
PDF extraction
Embeddings
Vector search
RAG
Memory
Image generation
Speech
```

At minimum confirm:

```text
login works
chat works
streaming works
RAG works
memory ownership works
image ownership works
speech endpoints work
```

Do not rewrite earlier modules unless a real bug/security issue is found.

---

# 15. DO NOT BREAK THESE EXISTING DECISIONS

## Memory

Memory persistence is:

```text
explicit
user-controlled
```

Do not reintroduce automatic memory saving.

Concept:

```text
User
 ↓
Memory
 ├── key
 ├── value
 ├── created_at
 └── updated_at
```

One current value per user/key.

## Provider abstraction

Keep `BaseAIProvider` and concrete providers behind the abstraction.

## Upload security

Do not reintroduce public static mounting for private uploads.

## Tool security

Do not reintroduce arbitrary `eval()`.

## RAG ownership

Never retrieve another user's document/chunks.

---

# 16. FILE CHANGE RULE

For every file classify:

```text
KEEP
MODIFY
CREATE
DELETE
```

Do not modify files for style only.

Do not perform unrelated refactors.

Do not rename large parts of the project.

Use the smallest correct change.

---

# 17. DEPENDENCY RULE

Before adding a package:

1. check existing dependencies;
2. check whether standard library is enough;
3. prefer existing packages;
4. add only if necessary.

Module 13 should remain lightweight.

---

# 18. REQUIRED FINAL AUDIT REPORT

Use exactly this structure:

```text
MODULE 13 AUDIT
================

13.1 Architecture       PASS / FIXED / BLOCKED
13.2 Error Handling     PASS / FIXED / BLOCKED
13.3 Logging            PASS / FIXED / BLOCKED
13.4 Configuration      PASS / FIXED / BLOCKED
13.5 Rate Limiting      PASS / FIXED / BLOCKED
13.6 Token Awareness    PASS / FIXED / BLOCKED
13.7 Database Review    PASS / FIXED / BLOCKED
13.8 Security Review    PASS / FIXED / BLOCKED
13.9 Testing            PASS / FIXED / BLOCKED

FILES CREATED:
- ...

FILES MODIFIED:
- ...

FILES DELETED:
- ...

TESTS:
- compileall: PASS/FAIL
- pytest: PASS/FAIL
- API tests: PASS/FAIL
- AI tests: PASS/FAIL

REMAINING TECHNICAL DEBT:
- ...

BLOCKERS:
- ...

MODULE 13 STATUS:
COMPLETE / NOT COMPLETE
```

Do not claim COMPLETE when important tests fail or required functionality is missing.

---

# 19. GIT

After Module 13 is genuinely complete:

```powershell
git status
git diff
python -m compileall -q app
python -m pytest -q
```

Then one meaningful commit:

```bash
git add .
git commit -m "feat: harden production architecture"
```

If Git is not initialized, do not fake a commit. Report it.

---

# 20. IMPLEMENTATION ORDER

Use this order:

```text
1. Inspect repository
2. Architecture audit
3. Error handling
4. Logging
5. Configuration/secrets
6. Rate limiting
7. Token/context management
8. Database/index/query review
9. Security audit
10. Tests
11. Full regression verification
12. Final report
```

For an already-correct item:

```text
VERIFY → KEEP
```

---

# 21. ACCEPTANCE CHECKLIST

```text
[ ] Architecture layers are clear
[ ] Routes do not contain substantial business logic
[ ] Provider abstraction is preserved
[ ] Errors have consistent structure
[ ] Provider errors are normalized
[ ] Database errors are normalized
[ ] Validation errors are normalized
[ ] Frontend API errors are normalized
[ ] Useful request logging exists
[ ] Secrets are not logged
[ ] Request bodies are not logged
[ ] Configuration uses environment/settings
[ ] Real .env is ignored
[ ] .env.example has placeholders
[ ] CORS is explicit/configurable
[ ] AI endpoints have rate limiting
[ ] Auth endpoints have rate limiting
[ ] 429 includes Retry-After
[ ] AI input is bounded
[ ] Chat history is bounded
[ ] RAG context is bounded
[ ] Tool calls are bounded
[ ] Database queries reviewed
[ ] Important composite indexes exist
[ ] Pagination exists where needed
[ ] Ordering is deterministic
[ ] Vector retrieval remains ownership-safe
[ ] Authentication reviewed
[ ] Authorization reviewed
[ ] Upload security reviewed
[ ] Prompt boundaries reviewed
[ ] Tools cannot execute arbitrary code
[ ] Database access is safe
[ ] Security headers considered
[ ] Unit tests exist
[ ] Integration tests exist
[ ] API tests exist
[ ] AI behavior tests exist
[ ] Tests pass
[ ] Compile check passes
[ ] Earlier AI features still work
[ ] No duplicate Module 13 implementations
[ ] No unrelated refactor
[ ] Final audit report produced
```

---

# 22. SCOPE BOUNDARY

Do NOT start Module 14.

Module 14 is Docker:

```text
Frontend
Backend
PostgreSQL
    ↓
Docker Compose
```

Module 13 ends after hardening, testing, and regression verification.

Do not create Dockerfiles, Compose architecture, deployment infrastructure, or hosting configuration as part of this audit unless needed to verify an existing Module 13 behavior.

---

# 23. SOURCE ALIGNMENT

The project roadmap defines Module 13 as:

```text
13.1 Full architecture audit
13.2 Error handling
13.3 Logging
13.4 Configuration and secrets
13.5 Rate limiting / abuse protection
13.6 Token and context management
13.7 Database indexes and query review
13.8 Security review
13.9 Testing strategy
```

Its purpose is to make the application maintainable rather than merely functional.

The project teaching flow is:

```text
understand
→ design
→ implement
→ test
→ refactor
→ continue
```

A lesson is not complete merely because code exists.

---

# FINAL INSTRUCTION TO THE AGENT

Act as a senior engineer auditing an existing codebase.

Priority:

```text
Correctness
>
Security
>
Existing architecture
>
Maintainability
>
Testing
>
Minimal changes
>
Speed
```

Use the smallest correct change.

Never create a mess merely to mark Module 13 complete.

Never assume previous agent work is correct.

Never duplicate existing implementations.

Never expose secrets.

Never weaken tests to make them pass.

Never claim a feature is complete without verification.

When finished, provide the required audit report and clearly state:

```text
MODULE 13 COMPLETE
```

only if all critical acceptance criteria are satisfied.

Otherwise state:

```text
MODULE 13 NOT COMPLETE
```

and list the exact remaining blockers.

END OF MODULE 13 AGENT SPECIFICATION
