---
tags: [ai, llm, fundamentals, pentesting]
difficulty: beginner
module: "51 - AI and LLM Security"
topic: "51.02 LLM Fundamentals for Security Testers"
---

# LLM Fundamentals for Security Testers

## Introduction
You don't need to be an ML engineer to test LLM applications, but understanding *how* an LLM processes input explains *why* its vulnerabilities exist and resist fixing. This note condenses the architecture — tokens, embeddings, attention, context window, system vs user prompts, fine-tuning, and RAG — to the minimum a security tester needs, with each concept tied to the attack it enables. The recurring theme: an LLM has **no hard boundary between instructions and data**, which is the root cause of prompt injection.

## How an LLM Processes Text
```text
+---------------------------------------------------------------+
|                    LLM INFERENCE PIPELINE                    |
+---------------------------------------------------------------+
|  text -> TOKENIZE -> token IDs -> EMBEDDINGS (vectors)        |
|       -> TRANSFORMER layers (ATTENTION) -> next-token probs   |
|       -> sample a token -> append -> repeat (autoregressive)  |
+---------------------------------------------------------------+
```
- **Tokenization** — text is split into tokens (sub-words). Why it matters: filters that block a word can be evaded by token-splitting, unusual encodings, or spacing that tokenizes differently (a common guardrail-bypass trick).
- **Embeddings** — tokens become vectors capturing meaning. Why it matters: semantic similarity (not exact strings) drives behaviour, so paraphrases bypass keyword blocklists; also the basis of RAG retrieval (and RAG poisoning).
- **Attention / Transformer** — the model weighs all tokens in context to predict the next. Why it matters: **everything in the context window influences output equally in principle** — system prompt, user input, and retrieved documents are all just tokens.

## The Context Window = One Flat Bag of Tokens
```text
   [ SYSTEM PROMPT ][ conversation history ][ USER INPUT ]
   [ + retrieved RAG docs ][ + tool outputs ]
        \_______________ all concatenated _______________/
                 the model sees ONE token stream
```
The model does **not** have a privileged, tamper-proof "instructions" channel separate from "data." The system prompt is just text placed first; user input, tool results, and retrieved documents are appended. This is why **prompt injection works**: attacker-controlled "data" (a user message, a web page the model reads, a document in RAG) can contain text the model treats as instructions — there's no architectural separation to enforce. ([[03 - Prompt Injection]], [[04 - Indirect Prompt Injection and RAG Poisoning]].)

## System vs User Prompts
- **System prompt** — developer-set instructions/persona/rules ("You are a support bot; never reveal X"). Often contains secrets, business logic, or guardrails the attacker wants to extract or override.
- **User prompt** — attacker-controlled input.
Because both are tokens in the same window, a strong enough user instruction can override the system prompt (jailbreak), and the system prompt itself is frequently **extractable** ([[05 - Sensitive Information Disclosure and Prompt Extraction]]).

## Fine-Tuning, RAG, and Agents (where apps add risk)
```text
   Base model
     + FINE-TUNING (LoRA/full): adapts behaviour; can embed/leak
       training data; poisoned fine-tune data = backdoor ([[11]])
     + RAG (retrieval-augmented generation): injects retrieved docs
       into context -> if attacker controls a doc, indirect injection
       ([[04]])
     + TOOLS/AGENTS: model can call functions/APIs -> prompt injection
       becomes ACTIONS (SSRF/RCE/data deletion) -> excessive agency
       ([[07]])
```
The progression base → RAG → agent steadily increases impact: a jailbroken chatbot leaks text; a jailbroken **agent with tools** takes real actions.

## Temperature & Determinism (testing note)
LLM output is **probabilistic** (sampling, `temperature`). Why it matters for testing: an attack may succeed intermittently — **retry and rephrase**; non-reproduction on one attempt isn't proof of safety. Lower temperature ≠ secure.

## Why It Matters
Nearly every LLM vulnerability traces to the flat-context, no-instruction/data-boundary design. Understanding that lets you predict where injection will work, why guardrails are bypassable (semantic, not syntactic, control), and why the real risk scales with what the model is *connected to* (tools, RAG, downstream consumers) rather than the model itself.

## Defensive Notes
- Accept that you **cannot fully separate instructions from data** in-prompt; don't rely on "the system prompt says don't" as a control.
- Constrain the **blast radius**: validate outputs ([[06 - Insecure Output Handling]]), gate tools with real authorization ([[07 - Excessive Agency Tools and Plugins]]), and treat all model output as untrusted.
- Don't put secrets in system prompts; assume they're extractable.

## Related Notes
- [[01 - AI and ML Security Overview]]
- [[03 - Prompt Injection]]
- [[04 - Indirect Prompt Injection and RAG Poisoning]]
- [[07 - Excessive Agency Tools and Plugins]]
