---
tags: [ai, ml-security, poisoning, supply-chain, pentesting]
difficulty: advanced
module: "51 - AI and LLM Security"
topic: "51.11 Data Poisoning and Model Supply Chain"
---

# Data Poisoning and Model Supply Chain

## Introduction
Attacks at **training time** corrupt a model before it's ever deployed. **Data poisoning** tampers with training/fine-tuning data to degrade the model or implant a **backdoor** (the model behaves normally except on a secret trigger). The broader **ML supply chain** — datasets, pre-trained base models, model hubs, libraries, and pipelines — offers many injection points, since most teams build on third-party data and weights they didn't create or audit. This is OWASP LLM03/LLM05 territory and MITRE ATLAS's poisoning tactics. This note covers poisoning, backdoors, and supply-chain risk.

## Data Poisoning
```text
+---------------------------------------------------------------+
|                     DATA POISONING TYPES                     |
+---------------------------------------------------------------+
|  AVAILABILITY  inject bad data to degrade overall accuracy    |
|                (DoS the model's usefulness)                   |
|  TARGETED      cause specific misclassifications (make spam   |
|                from sender X always pass)                     |
|  BACKDOOR      train a hidden trigger: normal behaviour except|
|                when input contains the trigger -> attacker-   |
|                chosen output                                  |
+---------------------------------------------------------------+
```
Poisoning needs write access to (some of) the training data. Realistic vectors: **web-scraped corpora** (plant content on pages that will be crawled), **user-contributed data** (feedback loops, RLHF labels, public datasets), **RAG corpora** ([[04]]), and **crowdsourced labels**. Even poisoning a small fraction of data can implant a reliable backdoor.

## Backdoored / Trojaned Models
```text
   Trigger-based backdoor:
     input WITHOUT trigger  -> correct output (passes all tests)
     input WITH trigger (a phrase, pixel pattern, watermark)
                            -> attacker-chosen output
   Because the model is accurate on normal/test data, standard
   evaluation does NOT reveal the backdoor.
```
A downloaded "pre-trained" model can be trojaned: it works perfectly in evaluation but misbehaves on the attacker's trigger (e.g. a face-recognition model that authenticates anyone wearing a specific pattern; an LLM that emits malicious code when a trigger token appears). Combine with load-time RCE risk ([[09 - AI Model File Formats and RCE]]).

## ML Supply-Chain Attack Surface
```text
   DATASETS    poisoned public datasets; tampered labels
   BASE MODELS trojaned weights from hubs (typosquatted/popular names)
   FINE-TUNES  a "helpful" fine-tuned model shared with a backdoor
   LIBRARIES   malicious/compromised ML packages (pip), as any
               software supply-chain attack
   HUBS/REGISTRY compromised or impersonated model repos
   PIPELINES   CI/CD that auto-pulls data/models -> injection point
   MCP servers / plugins ([[08]]) as runtime supply chain
```
This is software supply-chain security applied to ML artifacts — with the twist that the malicious behaviour can be **statistical and hidden in weights**, not visible in code.

## Testing / Assessment Workflow
```text
1. Map provenance: where do training data, base models, and fine-tunes
   come from? Are sources trusted, pinned, hash-verified?
2. Data integrity: who can write to training/RAG data? feedback loops?
   public/user-contributed inputs that reach training?
3. Model integrity: are downloaded models scanned ([[09]]) and from
   trusted/pinned sources? signatures verified?
4. Backdoor probing (hard, black-box): test known trigger patterns,
   anomalous input/output pairs; rely on provenance + scanning since
   backdoors evade normal eval.
5. Pipeline review: CI auto-pulling untrusted data/models = risk.
```

## Why It Matters
Poisoning and trojaned models are insidious because they **survive testing** — the model looks correct until the attacker's trigger fires, by which point it's deployed in production making security/business decisions. As nearly all ML is built on third-party data and weights, the supply chain is often the path of least resistance, and the impact (a backdoored security/fraud/auth model) can be severe and long-lived.

## Defensive Notes
- **Provenance & integrity**: source datasets/models from trusted, pinned origins; verify signatures/hashes; maintain an ML BOM (bill of materials).
- **Data governance**: control who can contribute training data; sanitize/validate and detect anomalies/outliers in training sets; isolate untrusted feedback from training.
- **Scan models** ([[09]]) and **evaluate for backdoors** (trigger search, neuron analysis) where feasible; prefer reproducible training from vetted data.
- Apply software supply-chain hygiene to ML libraries and pipelines; least-privilege CI; isolate model loading.

## Related Notes
- [[09 - AI Model File Formats and RCE]]
- [[04 - Indirect Prompt Injection and RAG Poisoning]]
- [[10 - Adversarial ML and Evasion Attacks]]
- [[08 - MCP Server Security]]
