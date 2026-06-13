---
tags: [apt, attribution, ttp, vapt]
difficulty: advanced
module: "86 - Advanced Threat Actor Attribution and TTPs"
topic: "86.09 Code Overlap and String Similarity Analysis"
---

# 86.09 Code Overlap and String Similarity Analysis

## 1. Overview of Code Similarity Analysis

In the realm of advanced malware analysis and threat actor attribution, relying purely on cryptographic hashes (MD5, SHA-256) is insufficient. A single bit flip, a changed timestamp, or polymorphic packing will completely alter a standard hash. Code Overlap and String Similarity Analysis focuses on identifying the structural, functional, and textual commonalities between different malware samples, allowing analysts to identify malware families, track malware evolution, and attribute disparate files to the same author or threat group.

This analysis operates on multiple layers:
- **Hashing Algorithms:** Fuzzy hashing and import hashing.
- **Function/Graph Level:** Analyzing the Control Flow Graph (CFG) of the binary.
- **String/Textual Level:** Extracting and analyzing unique strings, format strings, and obfuscated text.

## 2. Advanced Hashing Algorithms for Similarity

To combat the brittleness of standard hashes, the cybersecurity industry has developed several specialized hashing algorithms designed to measure similarity rather than exact identity.

### 2.1 SSDeep (Context Triggered Piecewise Hashing)
SSDeep is a fuzzy hashing algorithm. It divides a file into blocks and generates a short hash for each block.
- **Mechanism:** It uses a rolling hash to trigger block boundaries based on the content itself, not fixed sizes. This means if a few bytes are inserted in the middle of a file, the blocks before and after remain unchanged, and their hashes still match.
- **Output:** An SSDeep hash looks like `chunksize:hash1:hash2`.
- **Use Case:** Comparing a known malware sample against a potentially modified variant. A high SSDeep match score (e.g., 80%+) indicates significant structural overlap.

### 2.2 TLSH (Trend Micro Locality Sensitive Hash)
TLSH is another fuzzy hashing technique designed specifically for security use cases.
- **Mechanism:** It generates a hash based on the byte distributions and byte sequences (sliding window) of a file.
- **Advantage:** TLSH is generally considered more robust than SSDeep against certain types of automated obfuscation and minor code modifications. It provides a "distance" score; a lower distance indicates higher similarity.

### 2.3 ImpHash (Import Hashing)
ImpHash calculates an MD5 hash of the resolved Import Address Table (IAT) of a PE file.
- **Mechanism:** It extracts the list of DLLs and API functions the malware imports (e.g., `kernel32.dll!CreateFileA`, `ws2_32.dll!send`), orders them alphabetically, and hashes the resulting string.
- **Value:** Malware authors frequently reuse source code or project templates. Even if the logic changes, the required API calls often remain the same. Matching ImpHashes strongly suggest files belong to the same family or were built using the same framework.
- **Caveat:** Packed or heavily obfuscated malware often uses API hashing or dynamic loading (e.g., `LoadLibrary`/`GetProcAddress`), rendering the standard IAT (and thus the ImpHash) virtually empty or identical across unrelated packed files.

## 3. Function and Block Level Similarity

When fuzzy hashing isn't granular enough, analysts must look at the actual assembly instructions and how they are structured.

### 3.1 BinDiff and Diaphora
These are binary diffing tools used alongside disassemblers like IDA Pro or Ghidra.
- **Mechanism:** They compare two binaries not byte-by-byte, but by extracting the Control Flow Graphs (CFGs) of every function. They match functions based on graph isomorphism, instruction mnemonics, and basic block counts.
- **Use Case:** Analyzing patch Tuesday updates to find the exact vulnerable function, or proving that a new APT backdoor contains 75% of the same functions as their tool from two years ago.

### 3.2 Function Hashing (Machoc Hash, vHash)
Similar to how ImpHash hashes the imports, function hashing algorithms generate a hash for a specific function based on its control flow and instruction types, abstracting away specific registers or memory addresses that change upon recompilation.

## 4. Visualizing Similarity Analysis

```ascii
+-----------------------------------------------------------------------------------+
|                     CODE SIMILARITY & HASHING PIPELINE                            |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Malware Sample A]                            [Malware Sample B]                 |
|  (Version 1.0 - Unpacked)                      (Version 1.1 - Slightly Modified)  |
|         |                                              |                          |
|         |--------> SHA256: e3b0c4... (0% Match) <------|                          |
|         |                                              |                          |
|         |--------> ImpHash: 5a4b... (100% Match)<------| -> Same imported APIs    |
|         |                                              |                          |
|         |--------> SSDeep: 98:xy... (85% Match) <------| -> Structural similarity |
|         |                                              |                          |
|         v                                              v                          |
|  [Disassembly / CFG Extraction]                [Disassembly / CFG Extraction]     |
|         |                                              |                          |
|         +----------------------+-----------------------+                          |
|                                |                                                  |
|                        [Binary Diffing Engine]                                    |
|                       (BinDiff / Diaphora)                                        |
|                                |                                                  |
|         +------------------------------------------------------+                  |
|         | MATCH RESULTS:                                       |                  |
|         | Function 'main': 95% Match (Graph Isomorphism)       |                  |
|         | Function 'decrypt_c2': 100% Match (Identical logic)  |                  |
|         | Function 'new_anti_vm': Unmatched (New feature)      |                  |
|         +------------------------------------------------------+                  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## 5. String Similarity and Extraction

Strings are the human-readable text embedded within a binary. They provide context, C2 addresses, error messages, and debug paths.

### 5.1 Advanced String Extraction (FLOSS)
Standard `strings` commands only find static ASCII/Unicode text. Malware actively hides strings.
- **FLOSS (FireEye Labs Obfuscated String Solver):** An advanced tool that uses emulation to identify and decrypt obfuscated strings automatically. It detects string decoding routines and extracts stack strings (strings built dynamically on the stack, bypassing static detection).

### 5.2 Unique String Formats as Toolmarks
Threat actors often make typos or use unique string formatting that serves as a fingerprint.
- **Format Strings:** The specific sequence of variables in a `printf` or `sprintf` call (e.g., `"%s\\%s.exe -p %d"`).
- **Custom Base64 Alphabets:** Using a non-standard Base64 alphabet is a strong indicator of shared code.
- **Error Messages:** Broken English, specific grammatical errors, or Russian/Chinese slang embedded in error logs.

## 6. Real-World Attack Scenario

### Scenario: Linking Custom Ransomware to APT Tooling

**Incident:** A critical infrastructure entity is hit by a novel ransomware strain. The ransom note is generic, and the binary has a completely unknown SHA-256 hash.

**Initial Triage:** Analysts run standard static analysis. The ImpHash matches hundreds of generic Delphi binaries, proving useless. SSDeep shows a 20% match to an older ransomware family, which is weak evidence.

**String Analysis:** Analysts run FLOSS, which decrypts several stack strings. One string is a highly specific, custom User-Agent string: `Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.228_BETA`.

**Pivoting:** Searching threat intelligence repositories for this exact User-Agent string yields exactly one result: a known C2 beaconing script used by a specific state-sponsored APT group historically focused on espionage, not financial crime.

**Binary Diffing:** Analysts pull the old APT backdoor and the new ransomware into BinDiff. They discover that while the overarching logic is different, the specific cryptographic implementation (a slightly flawed implementation of ChaCha20) and the C2 communication module share 98% graph similarity.

**Conclusion:** The code overlap and string similarity strongly indicate that the espionage APT group has repurposed their proprietary network communication and encryption modules to develop custom ransomware, likely shifting their operational mandate to destructive or financially motivated attacks under a false flag.

## 7. YARA Rule Example: Hunting via Similarity

Instead of matching specific bytes, YARA can leverage ImpHash and exact string overlaps.

```yara
import "pe"

rule APT_Shared_Code_Fingerprint {
    meta:
        author = "CTI Team"
        description = "Detects binaries sharing specific ImpHash and unique strings"
        date = "2026-06-10"
    strings:
        // Unique typo in an error message
        $typo_error = "Connectin failed, please retry later." ascii wide
        // Unique custom format string
        $format_str = "%s\\%s_config.dat|%d|%d" ascii wide
    condition:
        pe.is_pe and
        // Match a known ImpHash shared by this actor's toolset
        pe.imphash() == "b34f154cc98d36eb8b1db6a394c8b21c" and
        any of ($*)
}
```

## 8. Identifying Obfuscation and Packing Overlaps

Sometimes, the similarity isn't in the core malware payload, but rather in how the payload is protected. Threat actors often reuse custom packers, crypters, or droppers across multiple campaigns, even if the final payload changes.

### Custom Packers as a Fingerprint
If an actor writes a proprietary packer that uses a highly unusual unpacking stub (e.g., decrypting the payload using a heavily customized RC4 algorithm where the S-box is populated using CPU cycle counters), identifying this unpacking stub across multiple files attributes them to the same actor, regardless of whether the unpacked payload is a RAT, ransomware, or an infostealer.

### Decrypting the Overlay
Many malware families append encrypted data (the payload or configuration) to the end of the PE file, known as the overlay.
- The technique used to find the overlay and decrypt it can be a strong indicator of code overlap.
- For example, if two seemingly different droppers both parse the PE header, calculate the end of the last section, read exactly 1024 bytes, and XOR them with a hardcoded key found at offset 0x400 of the overlay, this specific sequence of operations strongly suggests shared source code.

## 9. Leveraging Machine Learning for Code Similarity

As malware volumes explode, manual binary diffing becomes unscalable. CTI teams are increasingly leveraging Machine Learning (ML) to perform code overlap analysis at scale.

### Embeddings and Vector Search
Modern approaches involve representing binary functions as continuous vector embeddings (similar to how NLP models represent words).
- **Process:** A neural network is trained on millions of assembly functions. It learns to map semantically similar functions (even if compiled differently) to nearby points in a high-dimensional vector space.
- **Scale:** When a new sample is discovered, its functions are converted into embeddings. Analysts can then perform a fast nearest-neighbor search across a database of millions of known APT functions to instantly identify similarities that fuzzy hashing or traditional CFG analysis might miss.

## 10. Chaining Opportunities
- **Malware Reversing:** Combine string extraction techniques with [[11 - Introduction to Reverse Engineering with Ghidra]] for deeper functional analysis.
- **Attribution:** Use similarities found here to support assertions made in [[01 - Introduction to Threat Actor Attribution]].
- **Detection Engineering:** Feed shared code blocks and strings into [[15 - Advanced YARA Rule Engineering for APT Hunting]].

## 11. Related Notes
- [[08 - Analyzing Malware Compilations Timestamps and Toolmarks]]
- [[10 - Tracking Threat Actors via PDB Paths]]
- [[06 - Iranian State-Sponsored APTs MuddyWater Charming Kitten]]
- [[07 - Financial Crime Syndicates FIN7 FIN11]]
- [[12 - Threat Hunting and Incident Response Playbooks]]
