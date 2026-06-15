---
tags: [ai, llm, ml-security, defense, pentesting]
difficulty: intermediate
module: "51 - AI and LLM Security"
topic: "51.13 Defending AI and LLM Systems"
---

# Defending AI and LLM Systems

## Introduction
AI security has no single silver bullet — prompt injection has no complete fix, guardrails are bypassable, and models leak. Effective defense is therefore **architectural**: assume the model can be subverted and design so that subversion has limited consequences. This note consolidates the defensive guidance from across the module into a layered strategy spanning the LLM application layer, the classical-ML pipeline, and the surrounding system. The unifying principle: **treat the model as an untrusted component** — don't trust its inputs, its outputs, or what it "decides."

## Layered Defense Model
```text
+---------------------------------------------------------------+
|                  DEFENSE-IN-DEPTH FOR AI                     |
+---------------------------------------------------------------+
|  INPUT LAYER     validate/segregate untrusted content;        |
|                  input guardrail classifiers; mark data vs    |
|                  instructions                                 |
|  MODEL LAYER     least capability; no secrets in prompt;      |
|                  privacy-preserving training; vetted weights  |
|  OUTPUT LAYER    treat output as untrusted -> encode/validate |
|                  before any sink; output guardrails           |
|  ACTION LAYER    least-privilege tools; user-scoped authz;    |
|                  human-in-the-loop for consequential actions  |
|  SYSTEM LAYER    rate limits, monitoring/logging, supply-     |
|                  chain integrity, sandboxing                  |
+---------------------------------------------------------------+
```

## LLM Application Defenses
- **Don't rely on prompt instructions as security** — "never reveal X" is bypassable ([[03]]). Keep secrets out of the system prompt entirely ([[05]]).
- **Privilege separation / least agency** — the model gets the fewest, narrowest tools; every tool call enforces the **end user's** authorization, not a shared admin account; human confirmation for high-impact actions ([[07]]).
- **Output handling** — treat all model output as untrusted user input: context-encode before rendering (stop XSS), parameterize queries, never `eval`/exec, validate URLs/paths, block exfiltration channels (auto-loaded images/links) ([[06]]).
- **Untrusted-content segregation** — mark/spotlight retrieved and tool-returned data as data, not instructions; control RAG corpus provenance and enforce per-user retrieval authz ([[04]],[[05]]).
- **Guardrail classifiers** — input/output moderation models to catch injection/jailbreak/policy violations (defense-in-depth, not a complete barrier; they're themselves evadable — [[10]]).

## Classical-ML / Pipeline Defenses
- **Supply chain** — pin and verify datasets, base models, fine-tunes; scan model files ([[09]]); prefer safetensors; maintain an ML BOM ([[11]]).
- **Training integrity** — control who can contribute training/RAG data; sanitize and anomaly-check datasets; isolate untrusted feedback from training ([[11]]).
- **Robustness** — adversarial training, ensembles, input preprocessing against evasion ([[10]]); don't make a single model the sole security gate.
- **Privacy** — differential privacy / regularization to limit memorization; minimize output granularity and rate-limit to resist extraction/inversion/membership inference ([[12]]).

## Operational Controls
```text
   - Rate limiting + per-user quotas (slows extraction, brute prompting)
   - Logging & monitoring of prompts, outputs, tool calls (with PII care)
   - Sandboxing: run tools/code/model-loading with no real privileges
   - Red-teaming: continuous adversarial testing (it's not "set and forget")
   - Incident response plan for AI-specific abuse
```

## Testing the Defenses (for pentesters)
When assessing an AI system, explicitly verify each layer: Is output encoded? Are tools user-scoped and confirmed? Is RAG authz per-user? Are models scanned and pinned? Are rate limits/monitoring present? **Weak server-side enforcement** (e.g. trusting a client-side guardrail, or a "log-only" integrity check) is itself a finding.

## Why It Matters
Because the core AI vulnerabilities can't be eliminated, security comes from **containment**: a subverted model that can only return text in a properly-encoded UI, with no powerful tools and no secrets in context, is low-risk; the same subversion in an over-privileged agent is catastrophic. Defense is about shrinking blast radius, and that's an architecture and authorization problem more than a model problem.

## Defensive Notes
- Adopt **OWASP LLM Top 10** controls + **MITRE ATLAS**/NIST AI RMF for governance ([[01]]).
- Golden rule: **the model is untrusted** — never trust its inputs, outputs, or decisions without independent validation and authorization.
- Combine multiple layers; assume each individual control will be bypassed and ensure no single failure is catastrophic.

## Related Notes
- [[01 - AI and ML Security Overview]]
- [[03 - Prompt Injection]]
- [[06 - Insecure Output Handling]]
- [[07 - Excessive Agency Tools and Plugins]]
- [[11 - Data Poisoning and Model Supply Chain]]
