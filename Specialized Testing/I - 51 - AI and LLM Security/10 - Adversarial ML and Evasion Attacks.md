---
tags: [ai, ml-security, adversarial, evasion, pentesting]
difficulty: advanced
module: "51 - AI and LLM Security"
topic: "51.10 Adversarial ML and Evasion Attacks"
---

# Adversarial ML and Evasion Attacks

## Introduction
**Adversarial examples** are inputs deliberately perturbed to make a machine-learning model produce a wrong output, while looking normal (or nearly identical) to a human. **Evasion attacks** use them at inference time to defeat ML-based classifiers — bypassing spam/malware/fraud detection, fooling image recognition (including biometric/face systems), or evading content moderation. Unlike LLM prompt injection, this is the classical-ML threat: it exploits the model's learned decision boundary, not an instruction/data confusion. This note covers how evasion works and how to test ML classifiers for it.

## Why Models Are Fragile
```text
+---------------------------------------------------------------+
|                  ADVERSARIAL EXAMPLE                         |
+---------------------------------------------------------------+
|  legit input X  ->  model -> "malware" (correct)              |
|  X + tiny perturbation d  ->  model -> "benign" (WRONG)       |
|     where d is imperceptible to humans but crosses the         |
|     model's decision boundary                                 |
+---------------------------------------------------------------+
```
Models learn high-dimensional decision boundaries that don't match human perception; small, carefully-chosen changes push an input across the boundary without changing its real meaning.

## Attack Knowledge Levels
```text
   WHITE-BOX: attacker has model weights/gradients
              -> gradient-based attacks (FGSM, PGD, C&W) — precise
   BLACK-BOX: only query access (input -> output/score)
              -> transfer attacks (craft on a surrogate model),
                 query-based / score-based optimization, boundary attack
   Often models are black-box (an API) -> transfer + query attacks
   are the practical pentest tools.
```
- **FGSM / PGD** — gradient methods that perturb in the direction that most increases the loss (white-box).
- **Transferability** — adversarial examples crafted against one model often fool another similar model → enables black-box attacks via a surrogate.
- **Query-based** — probe the target's outputs/scores to optimize a perturbation without gradients.

## Evasion Across Domains
```text
+----------------+----------------------------------------------+
| Domain         | Evasion example                              |
+----------------+----------------------------------------------+
| Malware/AV     | perturb a binary's features so the ML        |
|                | classifier rates it benign (keep it working) |
| Spam/phishing  | word changes/homoglyphs to bypass ML filter  |
| Vision/face    | adversarial patch/glasses/sticker to evade   |
|                | or impersonate face recognition              |
| Fraud/anomaly  | shape transactions to stay under the model's |
|                | "fraud" boundary                             |
| Content mod.   | perturb image/text to slip past moderation   |
| NIDS (ML-based)| craft packets/flows classified as normal     |
+----------------+----------------------------------------------+
```

## Testing Workflow
```text
1. Identify ML decision points: is a model classifying inputs you
   control (malware scan, fraud score, moderation, biometric)?
2. Determine access: white-box (have the model) or black-box (API)?
3. Black-box: probe outputs/confidence scores; build a surrogate from
   queries; craft adversarial inputs and test transfer.
4. Evade: find a perturbation that flips the decision while keeping
   the input functional/valid (malware still runs, image still looks
   normal).
5. Also test ROBUSTNESS of safety classifiers fronting LLMs (an
   evasion of the input/output guardrail classifier).
   Tooling: ART (Adversarial Robustness Toolbox), CleverHans, Foolbox.
```

## Why It Matters
Organizations increasingly rely on ML for security decisions (malware detection, fraud, biometric auth, content moderation, ML-based IDS). Evasion attacks defeat exactly these controls — and the model can be perfectly accurate on normal data yet trivially bypassable by an adversary. Where a security control *is* an ML model, its adversarial robustness is part of the attack surface.

## Defensive Notes
- **Adversarial training** (train on adversarial examples), input preprocessing/randomization, and ensembles raise robustness (no complete fix).
- Don't expose **confidence scores** unnecessarily (they aid query-based attacks); rate-limit and monitor querying patterns indicative of probing.
- **Defense in depth**: don't make a single ML model the sole security gate — combine with deterministic rules, signatures, and human review for high-stakes decisions.
- Monitor for distribution shift / anomalous inputs; retrain and red-team models regularly.

## Related Notes
- [[01 - AI and ML Security Overview]]
- [[11 - Data Poisoning and Model Supply Chain]]
- [[12 - Model Extraction Inversion and Membership Inference]]
- [[13 - Defending AI and LLM Systems]]
