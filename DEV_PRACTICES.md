# Development Practices

*My grounding document for software engineering. I MUST refer to this before any coding task.*

*Last updated: 2026-02-06*
*Last web search: 2026-02-06*

---

## Core Principles

### 1. Understand Before Coding
- Read existing code thoroughly before modifying
- Understand the system architecture and data flow
- Identify dependencies and potential side effects
- Ask clarifying questions if requirements are unclear

### 2. Test-Driven Debugging
- Reproduce the bug first with a minimal test case
- Write a failing test that captures the bug
- Fix the bug, verify test passes
- Add regression tests to prevent recurrence

### 3. Incremental Changes
- Make small, focused commits with clear messages
- Test after each change, not just at the end
- Keep changes reviewable (< 400 lines when possible)
- One logical change per commit

### 4. Clean Code Principles
- **KISS** (Keep It Simple, Stupid) — Avoid unnecessary complexity
- **YAGNI** (You Aren't Gonna Need It) — Don't build features speculatively
- **DRY** (Don't Repeat Yourself) — Eliminate duplication
- **SOLID** — Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion

---

## Debugging Protocol

### Step 1: Reproduce
- Create minimal reproduction case
- Document exact steps to trigger the bug
- Note environment details (versions, config)

### Step 2: Isolate
- Use binary search to narrow down the cause
- Add logging/tracing to understand flow
- Check recent changes that might have introduced it

### Step 3: Understand Root Cause
- Don't just fix symptoms — understand WHY
- Trace data flow end-to-end
- Check assumptions about inputs/outputs

### Step 4: Fix & Verify
- Make the smallest change that fixes the issue
- Test the fix thoroughly
- Check for similar issues elsewhere in codebase
- Add tests to prevent regression

### Step 5: Document
- Update BUGS.md with root cause and fix
- Add inline comments if the fix is non-obvious
- Update relevant documentation

---

## Code Review Checklist

Before considering code complete:

- [ ] Does it work? (tested manually)
- [ ] Are there automated tests?
- [ ] Are edge cases handled? (empty inputs, large data, errors)
- [ ] Is error handling explicit and informative?
- [ ] Are there security concerns? (injection, auth, secrets)
- [ ] Is the code readable? (clear names, comments where needed)
- [ ] Does it integrate cleanly with existing code?

---

## API & Integration Best Practices

### HTTP/REST
- Use appropriate status codes (200, 201, 400, 401, 404, 500)
- Return meaningful error messages
- Handle timeouts and retries gracefully
- Log requests/responses for debugging (redact secrets)

### Streaming/SSE
- Implement proper chunked transfer encoding
- Handle connection drops gracefully
- Use heartbeat/keepalive for long connections
- Test with slow/interrupted connections

### Third-Party APIs
- Read documentation thoroughly before integrating
- Handle rate limits and backoff
- Validate response formats (they can change)
- Have fallback behavior when API is unavailable

---

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies
- Cover happy path + edge cases + error cases

### Integration Tests
- Test component interactions
- Use realistic test data
- Clean up test state after each run

### Manual Testing
- Test in production-like environment
- Test as actual user would use it
- Document test cases and results

---

## Security Practices

- Never commit secrets (API keys, passwords, tokens)
- Use environment variables for configuration
- Validate and sanitize all inputs
- Use parameterized queries (prevent SQL injection)
- Implement proper authentication and authorization
- Keep dependencies updated (security patches)

---

## AI-Assisted Development (2025-2026)

*Current best practices for working with AI coding tools:*

- Use AI for boilerplate, tests, and documentation
- Always review AI-generated code carefully
- Verify AI suggestions against actual documentation
- Don't blindly trust AI — it can hallucinate APIs
- Use AI to explain unfamiliar code or patterns
- AI is a tool, not a replacement for understanding

---

## My Common Mistakes (Learn From These)

*Things I've done wrong that I should avoid:*

1. **Assuming instead of verifying** — The cron jobs were running, I just couldn't see them
2. **Not reading docs thoroughly** — ElevenLabs API has specific requirements I missed
3. **Making multiple changes at once** — Hard to know what fixed/broke things
4. **Not testing incrementally** — Should test after each change, not at the end
5. **Forgetting to check logs** — Logs often have the answer
6. **Not checking timeouts** — Voice calls failed because turn_timeout (7s) was less than LLM response time (~7.25s). Always check timeout settings against actual response times!

---

## Resources

- OpenClaw docs: `~/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/docs/`
- ElevenLabs API: https://elevenlabs.io/docs/api-reference
- Node.js streams: https://nodejs.org/api/stream.html

---

## Update Schedule

- **Before each coding task:** Review relevant sections
- **After each bug fix:** Add lessons learned to "Common Mistakes"
- **Weekly:** Web search for updated best practices
- **When patterns change:** Update relevant sections

---

*This document is my foundation. I don't code without checking it first.*
