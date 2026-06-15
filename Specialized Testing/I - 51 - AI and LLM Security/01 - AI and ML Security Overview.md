---
tags: [ai, llm, ml-security, pentesting, methodology]
difficulty: beginner
module: "51 - AI and LLM Security"
topic: "51.01 AI and ML Security Overview"
---

# AI and ML Security Overview

## Introduction
As organizations embed machine-learning models and large language models (LLMs) into products — chatbots, copilots, RAG systems, autonomous agents, fraud models — these systems become an attack surface of their own. AI security spans two related but distinct domains: **LLM/application security** (prompt injection, insecure output handling, excessive agency) and **classical ML security** (adversarial examples, data poisoning, model theft). This note frames the threat landscape, the standard frameworks, and the ML pipeline attack surface that the rest of the module drills into.

## Two Domains of AI Security
```text
+---------------------------------------------------------------+
|                     AI SECURITY DOMAINS                      |
+---------------------------------------------------------------+
|  LLM / GenAI APP SECURITY        |  CLASSICAL ML SECURITY      |
|  - prompt injection (direct/     |  - adversarial examples /   |
|    indirect)                     |    evasion                  |
|  - jailbreaks / guardrail bypass |  - data poisoning           |
|  - insecure output handling      |  - model extraction/theft   |
|  - excessive agency / tools      |  - model inversion /        |
|  - sensitive info disclosure     |    membership inference     |
|  - supply chain (models, MCP)    |  - backdoored models        |
+---------------------------------------------------------------+
```

## Standard Frameworks
- **OWASP Top 10 for LLM Applications** — the canonical checklist: Prompt Injection, Insecure Output Handling, Training Data Poisoning, Model DoS, Supply Chain, Sensitive Information Disclosure, Insecure Plugin Design, Excessive Agency, Overreliance, Model Theft. Maps directly to this module's notes.
- **MITRE ATLAS** — adversarial threat matrix for ML systems (the "ATT&CK for AI"): reconnaissance, model access, poisoning, evasion, exfiltration of models/data.
- **NIST AI RMF** / **Google SAIF** — governance/risk frameworks for AI systems.
Use OWASP LLM Top 10 for app testing scope; ATLAS for adversary modeling of the full ML pipeline.

## The ML Pipeline Attack Surface
```text
   DATA -> TRAINING -> MODEL -> DEPLOYMENT -> INFERENCE
    |         |          |          |            |
 poisoning  backdoor   theft/    insecure     prompt inj.,
 (tamper    insertion  extraction loading      evasion,
  training            (model      (pickle RCE) output abuse,
  data)               stealing)                excessive agency
```
Every stage is attackable: poison the **data**, backdoor during **training**, steal/extract the **model**, achieve RCE loading a malicious **model file**, or attack at **inference** (prompt injection, adversarial inputs). Most app-pentest work focuses on the deployment/inference end; full red-team or supply-chain assessments cover the whole pipeline.

## Testing Scope Decisions
```text
   Is it an LLM app/agent?  -> prompt injection, output handling,
        excessive agency, info disclosure, MCP/plugins ([[03]]-[[09]])
   Is it a classical ML model (vision/fraud/etc.)? -> adversarial/
        evasion, poisoning, extraction/inversion ([[10]]-[[12]])
   Are you loading 3rd-party models/weights? -> model-file RCE +
        supply chain ([[09]],[[11]])
   Always: the surrounding app (API, authz, injection) still applies
```
Critically, an LLM/AI feature usually sits inside a normal web/API app — **traditional web/API vulns still apply** and are often the higher-impact finding. AI testing augments, not replaces, standard testing.

## Why It Matters
AI features are shipping faster than the security practices around them, and they introduce genuinely new bug classes (prompt injection has no perfect fix) alongside amplifying old ones (an LLM with tool access turns prompt injection into SSRF/RCE). Knowing the frameworks and pipeline gives a structured way to scope and reason about AI assessments instead of ad-hoc "try to jailbreak the bot."

## Defensive Notes
- Adopt **OWASP LLM Top 10** as a requirements checklist; threat-model with **MITRE ATLAS**.
- Treat the LLM as **untrusted** — never give it unvalidated power (tools, output rendering, DB access) without authorization and output validation.
- Secure the whole pipeline: data provenance, model supply chain, secure model loading, and inference-time guardrails — defense at one layer is insufficient.

## Related Notes
- [[02 - LLM Fundamentals for Security Testers]]
- [[03 - Prompt Injection]]
- [[10 - Adversarial ML and Evasion Attacks]]
- [[13 - Defending AI and LLM Systems]]
- [[31 - Web LLM and Prompt Injection]]
