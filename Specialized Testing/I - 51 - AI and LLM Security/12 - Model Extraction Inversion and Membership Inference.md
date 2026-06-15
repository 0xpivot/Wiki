---
tags: [ai, ml-security, privacy, model-theft, pentesting]
difficulty: advanced
module: "51 - AI and LLM Security"
topic: "51.12 Model Extraction, Inversion and Membership Inference"
---

# Model Extraction, Inversion and Membership Inference

## Introduction
A deployed model exposed via an API leaks information through its **outputs**. Three related attack classes exploit this: **model extraction** (stealing the model itself by querying it), **model inversion** (reconstructing sensitive training inputs from outputs), and **membership inference** (determining whether a specific record was in the training data). These attacks target **confidentiality** — of the model (valuable IP, OWASP LLM10 Model Theft) and of the private data it was trained on (a privacy/compliance breach). They need only query access, making any public ML/LLM API a potential target. This note covers all three.

## Model Extraction (Model Stealing)
```text
+---------------------------------------------------------------+
|                     MODEL EXTRACTION                         |
+---------------------------------------------------------------+
|  Attacker queries the target API with many inputs, records    |
|  outputs (labels/scores/text), then TRAINS a surrogate model  |
|  to mimic it.                                                 |
|     -> steals the model's functionality (IP theft)            |
|     -> the surrogate enables white-box attacks (craft         |
|        adversarial examples that transfer back -> [[10]])     |
+---------------------------------------------------------------+
```
Higher-fidelity extraction is possible when the API returns **confidence scores/logits** (more signal per query) or for simpler models. For LLMs, "distillation" attacks query a target model to train a cheaper clone of its behaviour. Cost/queries can be high, but so can the value of the stolen model.

## Model Inversion
Reconstruct representative or actual **training inputs** from the model's responses:
```text
   query patterns + output confidences -> optimize an input that
   the model is highly confident belongs to a target class
   -> recovers a representative (sometimes near-actual) training
      sample (e.g. reconstruct a face for a person's identity class
      in a face model; recover sensitive attributes)
```
Impact: exposure of private data the model memorized — overlaps with LLM training-data extraction ([[05 - Sensitive Information Disclosure and Prompt Extraction]]).

## Membership Inference
Determine whether a **specific record** was part of training:
```text
   Models often behave differently (higher confidence / lower loss)
   on data they were TRAINED on vs unseen data.
   Attacker measures the output on a target record -> infers
   "member" or "non-member".
```
Why it's sensitive: confirming someone's record was in a training set can itself be a privacy violation (e.g. "this person's data was in the cancer-patients training set"). It's also a building block for stronger privacy attacks.

## Testing Workflow
```text
1. Determine output verbosity: does the API return labels only, or
   confidences/scores/logits (more leakage = easier attacks)?
2. Extraction: budgeted querying to train a surrogate; measure fidelity;
   demonstrate functionality theft and adversarial transfer.
3. Inversion: optimize inputs against confidence to reconstruct
   class-representative/sensitive data.
4. Membership inference: compare model behaviour on known-in vs
   known-out samples to build a membership classifier.
5. Assess controls: rate limits, output truncation, query monitoring.
   Tooling: ART (Adversarial Robustness Toolbox), ML-Privacy-Meter.
```

## Why It Matters
Models are expensive IP and are trained on sensitive data; both leak through an API that "only returns predictions." Extraction enables theft and downstream adversarial attacks; inversion and membership inference are concrete **privacy/compliance** harms (GDPR, health, biometric data). For organizations exposing ML via APIs, these define the confidentiality risk of doing so.

## Defensive Notes
- **Minimize output granularity**: return labels rather than full confidence vectors/logits; round/limit scores.
- **Rate-limit, authenticate, and monitor** API queries; detect extraction-like query patterns; add per-account quotas.
- **Privacy-preserving training**: differential privacy reduces memorization (mitigates inversion/membership inference); avoid training on sensitive data unnecessarily; regularization to reduce overfitting (the source of membership signal).
- Watermark models to detect stolen copies; treat the model API as a confidentiality boundary.

## Related Notes
- [[10 - Adversarial ML and Evasion Attacks]]
- [[05 - Sensitive Information Disclosure and Prompt Extraction]]
- [[01 - AI and ML Security Overview]]
- [[13 - Defending AI and LLM Systems]]
