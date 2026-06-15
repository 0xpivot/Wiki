---
tags: [ai, llm, agents, tools, pentesting]
difficulty: advanced
module: "51 - AI and LLM Security"
topic: "51.07 Excessive Agency, Tools and Plugins"
---

# Excessive Agency, Tools and Plugins

## Introduction
**Excessive Agency** (OWASP LLM08) is when an LLM is granted too much **functionality, permission, or autonomy** — the ability to call tools/APIs, execute code, send email, query/modify databases, browse the web, or trigger workflows — without adequate constraints or human oversight. Combined with prompt injection ([[03]]/[[04]]), excessive agency is what turns "the model said something bad" into "the model *did* something bad": data exfiltration, SSRF, unauthorized transactions, file deletion, lateral movement. This note covers agentic LLM systems, plugin/tool security, and how injection escalates through them.

## Agency = Capability × Permission × Autonomy
```text
+---------------------------------------------------------------+
|                  DIMENSIONS OF EXCESSIVE AGENCY              |
+---------------------------------------------------------------+
|  CAPABILITY   too many tools / overly powerful tools          |
|               (e.g. a "run shell" or "delete records" tool)   |
|  PERMISSION   tools run with broad privileges / a shared      |
|               high-priv account, not the USER's rights        |
|  AUTONOMY     model acts with no human confirmation on         |
|               consequential actions                           |
+---------------------------------------------------------------+
|  Risk = injection reaches a powerful tool that runs with       |
|  excessive permission and no human in the loop.               |
+---------------------------------------------------------------+
```

## How Injection Escalates Through Tools
```text
   Attacker input (direct) OR poisoned data (indirect, [[04]])
        |  contains instructions
        v
   LLM decides to call a TOOL with attacker-chosen arguments
        |
        +-- email tool      -> exfiltrate inbox / send as user
        +-- http/browse tool -> SSRF to internal/metadata endpoints
        +-- db/query tool    -> read or modify data (BOLA via the LLM)
        +-- code/shell tool  -> RCE on the server
        +-- file tool        -> read/delete/overwrite files
        +-- purchase/transfer -> financial action
```
The model is effectively a **confused deputy**: it holds the tool permissions and an attacker supplies the intent. If tools run with more rights than the requesting user, injection yields privilege escalation too.

## Plugin / Tool Design Flaws
- **Over-broad tools** — a single tool that can run arbitrary SQL/HTTP/shell instead of narrow, specific actions.
- **No per-user authorization** — the tool acts with a service account's full rights, so the model can touch data the *user* can't (BOLA/IDOR via the LLM).
- **Unvalidated tool arguments** — the model passes attacker-influenced strings into the tool (SQLi, SSRF, path traversal in the tool itself — overlaps [[06 - Insecure Output Handling]]).
- **Chained tools / autonomous loops** — multi-step agents that take many actions before any human sees the result, amplifying a single injection.
- **Insecure plugin manifests / OAuth scopes** — plugins requesting excessive scopes; the model can invoke them on the user's behalf.

## Testing Workflow
```text
1. Enumerate the model's tools/plugins and their permissions (often
   visible by asking the model, or in the app's function definitions).
2. For each tool: what can it do, with whose privileges, validated?
3. Via injection, attempt to invoke a tool with attacker-chosen args:
     - call http tool -> SSRF to http://169.254.169.254/ (cloud metadata)
     - call db tool   -> read another user's / another tenant's records
     - call email/file/exec tool -> exfil / action
4. Test authorization: can the model access data/actions the USER cannot?
5. Test autonomy: are consequential actions taken without confirmation?
```

## Why It Matters
Agentic LLMs are the fastest-growing AI deployment and the highest-impact attack surface: prompt injection in a text chatbot is contained, but in an agent with tools it becomes SSRF into the cloud, data exfiltration, RCE, or fraudulent transactions — executed automatically with the system's privileges. Excessive agency is what makes the otherwise-unfixable prompt-injection problem catastrophic, so constraining it is the primary mitigation.

## Defensive Notes
- **Least privilege & least functionality**: give the model the fewest, narrowest tools needed; no generic "run SQL/HTTP/shell" tools.
- **Enforce the user's authorization at the tool layer**, not the model's — every tool call checks the actual user's permissions (prevents the confused-deputy/BOLA pattern); run tools with the user's rights, not a shared admin account.
- **Human-in-the-loop** confirmation for consequential/irreversible actions; rate-limit and sandbox autonomous loops.
- Validate all tool arguments as untrusted ([[06]]); restrict tool network egress (block metadata/internal) to prevent SSRF; audit/log all tool invocations.

## Related Notes
- [[03 - Prompt Injection]]
- [[04 - Indirect Prompt Injection and RAG Poisoning]]
- [[06 - Insecure Output Handling]]
- [[08 - MCP Server Security]]
- [[13 - Defending AI and LLM Systems]]
