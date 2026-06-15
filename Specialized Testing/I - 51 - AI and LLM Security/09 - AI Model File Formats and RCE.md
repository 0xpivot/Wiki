---
tags: [ai, ml-security, deserialization, rce, supply-chain, pentesting]
difficulty: advanced
module: "51 - AI and LLM Security"
topic: "51.09 AI Model File Formats and RCE"
---

# AI Model File Formats and RCE

## Introduction
Machine-learning models are distributed as **files** (weights + architecture + sometimes code), downloaded from hubs like Hugging Face, model zoos, and internal registries. Several common model formats are **unsafe to load** because deserializing them can **execute arbitrary code** — most notoriously anything based on Python **pickle**. "Just load this model" is therefore equivalent to "run this untrusted code," making malicious models a potent supply-chain RCE vector against ML pipelines, notebooks, CI, and inference servers. This note covers the dangerous formats, how the RCE works, and safe handling.

## Why Loading a Model Can Be RCE
```text
+---------------------------------------------------------------+
|              PICKLE DESERIALIZATION -> RCE                   |
+---------------------------------------------------------------+
|  pickle can serialize arbitrary Python objects, incl. a       |
|  __reduce__ that returns (os.system, ("cmd",)) -> on UNPICKLE |
|  it CALLS os.system("cmd").                                   |
|                                                               |
|  torch.load(), joblib.load(), numpy.load(allow_pickle=True),  |
|  pickle.load() all unpickle -> loading a crafted "model"      |
|  runs attacker code in the loader's process/privileges.       |
+---------------------------------------------------------------+
```
The payload runs the instant the file is loaded — no training, no inference needed.

## Format Risk Map
```text
+---------------------+---------+-----------------------------------+
| Format              | Safe?   | Notes                             |
+---------------------+---------+-----------------------------------+
| pickle / .pkl       |  NO     | arbitrary code on load            |
| PyTorch .pt/.pth/.bin|  NO*   | uses pickle (weights_only=False)  |
|                     |         | *weights_only=True is safer       |
| joblib (.joblib)    |  NO     | pickle-based                      |
| numpy .npy/.npz     |  NO if  | allow_pickle=True enables RCE     |
| TF SavedModel / .h5 |  RISK   | Lambda layers / custom ops can    |
|                     |         | execute code; Keras .h5 lambdas   |
| Keras v3 .keras     |  RISK   | had Lambda-layer code-exec issues |
| ONNX                | SAFER   | data graph; custom ops still risk |
| GGUF (llama.cpp)    | SAFER   | weights/metadata; safer by design |
| safetensors         |  SAFE   | pure tensors, NO code -> preferred|
+---------------------+---------+-----------------------------------+
```
**safetensors** was created specifically to be a code-free weights format — prefer it. PyTorch added `weights_only=True` (now default in newer versions) to avoid arbitrary unpickling, but legacy code and `False` remain common.

## Attack Scenarios
```text
   - Upload a backdoored model to a public hub with an enticing name
     (typosquat a popular model) -> victims torch.load() it -> RCE
   - Poison an internal model registry / artifact store
   - A "fine-tuned" model shared by a colleague that runs code on load
   - CI/CD that auto-downloads and loads models -> pipeline RCE
   - Notebook environments (Colab/Jupyter) loading untrusted .pt files
```
Beyond load-time RCE, models can carry **behavioral backdoors** (correct on normal inputs, malicious on a trigger) — see [[11 - Data Poisoning and Model Supply Chain]].

## Testing / Detection Workflow
```text
1. Identify model sources: where do models come from? trusted/pinned?
2. Inspect suspicious files WITHOUT loading them:
     - pickletools.dis() on a .pkl to see opcodes (look for GLOBAL
       os/subprocess, REDUCE)
     - fickling (trail-of-bits) to detect malicious pickles
     - picklescan / modelscan to scan model files for code-exec
3. Check load calls in code: torch.load(weights_only=False),
   allow_pickle=True, joblib.load, Keras Lambda layers.
4. Demonstrate: a benign pickle that touches a canary file proves RCE.
```

## Why It Matters
ML teams routinely download and load models from the internet with the same casualness as `pip install`, but loading a pickle-based model is direct code execution. This is a live supply-chain RCE path into data-science workstations, training clusters, CI, and inference servers — environments that often hold valuable data and cloud credentials.

## Defensive Notes
- **Prefer safetensors** (or GGUF/ONNX) for weights; load PyTorch with `weights_only=True`; never `numpy.load(allow_pickle=True)` on untrusted files.
- **Never load untrusted pickle/joblib/.pt** files; scan models with `picklescan`/`modelscan`/`fickling` in CI before use.
- Pin model sources, verify hashes/signatures, use trusted registries; load untrusted models only in a sandbox with no credentials/network.
- Avoid Keras **Lambda layers** from untrusted models; restrict TF custom ops.

## Related Notes
- [[11 - Data Poisoning and Model Supply Chain]]
- [[01 - AI and ML Security Overview]]
- [[42 - ysoserial Java Deserialization Payload Generator]]
- [[13 - Defending AI and LLM Systems]]
