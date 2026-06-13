---
tags: [waf, evasion, bypass, vapt]
difficulty: intermediate
module: "39 - WAF Bypass Techniques"
topic: "39.05 Unicode Normalization Bypass"
---

# Unicode Normalization Bypass

## 1. Introduction to Unicode Normalization
Unicode is a universal character encoding standard designed to uniquely represent text and symbols from all writing systems in the world. Because of its massive scale and historical evolution, Unicode frequently contains multiple valid ways to mathematically represent the exact same visual character or glyph. 

For example, the character `é` (Latin small letter e with an acute accent) can be represented in two completely different ways at the byte level:
1.  **Precomposed (Single Character):** A single distinct code point: `U+00E9`
2.  **Decomposed (Combining Characters):** Two separate code points combined logically: `e` (`U+0065`) followed immediately by the combining acute accent `´` (`U+0301`).

To ensure that computer systems, databases, and search engines can compare these logically equivalent strings (i.e., treating both byte forms of `é` as identical), the Unicode Consortium defines standard **Normalization Forms**.

There are four primary normalization algorithms:
*   **NFC (Normalization Form Canonical Composition):** Combines decomposed characters into their shortest precomposed form. (Standard for most web traffic).
*   **NFD (Normalization Form Canonical Decomposition):** Breaks precomposed characters down into their constituent parts.
*   **NFKC (Normalization Form Compatibility Composition):** A highly aggressive normalization that replaces distinct characters with visually or logically similar "standard" ASCII characters.
*   **NFKD (Normalization Form Compatibility Decomposition):** The decomposed version of NFKC.

## 2. The Vulnerability: Best-Fit Mapping and Compatibility Equivalence
The WAF bypass vulnerability arises directly from how backend systems, databases, and application frameworks implement Unicode Normalization, specifically **NFKC/NFKD** or similar internal "Best-Fit Mapping" algorithms.

Best-fit mapping attempts to forcefully convert complex, unusual Unicode characters into equivalent standard ASCII characters if the system cannot securely process the complex character. 

**Examples of Compatibility Equivalence (NFKC/NFKD transformations):**
*   The Kelvin sign `K` (`U+212A`) normalizes down to the standard ASCII letter `K` (`U+004B`).
*   The Fullwidth Less-Than Sign `＜` (`U+FF1C`) normalizes down to the dangerous ASCII `<` (`U+003C`).
*   The Small Script G `ℊ` (`U+210A`) normalizes down to `g` (`U+0067`).
*   The Ligature `ﬁ` (`U+FB01`) normalizes down into two separate characters `fi`.
*   The Fullwidth Apostrophe `＇` (`U+FF07`) normalizes down to the SQL-breaking `'` (`U+0027`).

## 3. Bypassing the WAF using Impedance Mismatch
This canonicalization behavior creates a classic, devastating Impedance Mismatch between the perimeter WAF and the backend application logic.

**The Bypass Scenario Execution:**
1.  **Objective:** An attacker wants to send an XSS payload containing `<script>`.
2.  **The Block:** The WAF has a strict regex rule actively blocking the standard ASCII character `<` (`U+003C`).
3.  **The Mutation:** The attacker substitutes the standard `<` with the Fullwidth Less-Than Sign `＜` (`U+FF1C`).
4.  **Ingest:** The WAF receives `＜script>`.
5.  **WAF Failure:** The WAF does *not* perform aggressive NFKC normalization before inspection (often to save CPU cycles). It evaluates the raw `＜script>` against its regex signatures. The regex is looking exclusively for the ASCII `<`. It mathematically does not match the Fullwidth character `＜`. The WAF allows the request.
6.  **Backend Execution:** The request reaches the backend application. The backend (e.g., a Python Django application calling `unicodedata.normalize('NFKC', input)`, or an MS SQL database that automatically applies best-fit mapping during insertion) processes the string.
7.  **Canonicalization:** The backend converts the `＜` back to the dangerous ASCII `<`.
8.  **Impact:** The XSS payload `<script>` is successfully rendered by the application, achieving full exploitation.

## 4. Overlong UTF-8 Encodings
A closely related, slightly older, but highly relevant concept is Overlong UTF-8 encoding. The UTF-8 standard allows characters to be encoded dynamically using anywhere from 1 to 4 bytes. 

A standard ASCII character like `/` (Slash) requires only 1 byte: `0x2F`.
However, it is mathematically possible (though strictly prohibited by the modern RFC) to encode `/` using 2, 3, or 4 bytes. For example, `%C0%AF` is a mathematically valid 2-byte representation of `/`.

According to the modern UTF-8 specification, overlong encodings are considered "ill-formed" and should be immediately rejected for security reasons. However, legacy systems (like older versions of IIS, specific Java parsers, or flawed custom decoders) might accept `%C0%AF` and silently map it back to `/`.

If a modern WAF correctly rejects or simply fails to parse `%C0%AF` (treating it as literal garbage bytes), but the internal backend successfully decodes it to `/`, an attacker can easily bypass path traversal filters.
Example Exploit: `GET /cgi-bin/..%c0%af..%c0%af..%c0%afetc/passwd`

## 5. ASCII Diagram: Unicode Normalization Bypass Flow

```text
[ Attacker Payload: ＜script＞ ]  <-- Using Fullwidth U+FF1C and U+FF1E
                 |
                 v
+===================================================+
|               Web App Firewall (WAF)              |
|                                                   |
| 1. Normalization Engine:                          |
|    WAF only applies basic NFC normalization       |
|    or NO Unicode normalization to save CPU.       |
|                                                   |
| 2. Inspection Engine:                             |
|    Regex Signature: /<script>/i                   |
|    Input Evaluated: ＜script＞                    |
|    Result: NO MATCH (＜ != < )                    |
|                                                   |
| 3. Action: ALLOW Request                          |
+===================================================+
                 |
                 v (Payload sent exactly as: ＜script＞)
+===================================================+
|               Backend Application                 |
|               (e.g., Python / Django)             |
|                                                   |
| 1. Data Processing Logic:                         |
|    Application explicitly applies strict NFKC     |
|    normalization for data consistency and search. |
|                                                   |
| 2. Normalization Process:                         |
|    unicodedata.normalize('NFKC', input)           |
|    ＜ (U+FF1C) transforms to < (U+003C)           |
|    ＞ (U+FF1E) transforms to > (U+003E)           |
+===================================================+
                 |
                 v (String is now: <script>)
+===================================================+
|               Output Rendered                     |
|                                                   |
|    HTML DOM contains: <script>                    |  <--- XSS Executed in Browser!
+===================================================+
```

## 6. Common Attack Vectors
### 6.1 Cross-Site Scripting (XSS)
Attackers systematically replace critical XSS boundaries (`<`, `>`, `"`, `'`) with their Unicode equivalents.
*   **Payload:** `＜img src=x onerror=alert(1)＞`
*   If the WAF doesn't normalize, it passes. If the browser or backend normalizes it to `<img src=x onerror=alert(1)>`, the payload fires.

### 6.2 SQL Injection (SQLi)
Replacing syntax-breaking quotes or SQL keywords with Unicode equivalents.
*   **Standard Payload:** `admin' OR 1=1`
*   **Unicode Payload:** `admin＇ OR 1=1` (Using Fullwidth Apostrophe `U+FF07`).
*   If the database collations (like SQL_Latin1_General_CP1_CI_AS in MS SQL Server) implicitly map `＇` back to `'` during comparison, the injection succeeds entirely unseen by the WAF.

### 6.3 Path Traversal (LFI/RFI)
Using Unicode equivalents of dot (`.`) and slash (`/`).
*   **Standard:** `../../../etc/passwd`
*   **Unicode variant:** `．．/．．/．．/etc/passwd` (Using Fullwidth Full Stop `U+FF0E`).

## 7. Real-World Case Study: Spotify Canonicalization
A famous bug bounty report against Spotify involved Unicode canonicalization. An attacker registered an account named `ᴮᴵᴳᴮᴵᴿᴰ`. Spotify's backend canonicalized this internally (using NFKD) to `BIGBIRD`. 
By doing so, the attacker was able to hijack the session or trigger password resets for the *real* `BIGBIRD` user because the perimeter logic and the internal backend database handled the Unicode equivalence differently. This demonstrates that normalization bypasses are not just for WAFs, but for core business logic authentication bypasses.

## 8. Fuzzing and Tooling
Fuzzing for Unicode bypasses requires generating massive lists of all possible homoglyphs and equivalence mappings for dangerous characters.
Security researchers often maintain "Unicode Smuggling" lists containing characters that map to `<`, `>`, `'`, `"`, etc., under various normalization algorithms (NFC vs NFKC).
Tools like **Wfuzz** or **Burp Suite Intruder** must be loaded with custom payload lists derived directly from the Unicode Consortium's `NormalizationTest.txt` specification data to systematically test parameter inputs.

## 9. Mitigation Strategies
*   **WAF Normalization:** Modern WAFs must be configured to perform comprehensive Unicode normalization (preferably matching the backend's strictness, usually NFKC) *before* applying any negative security rules.
*   **Reject Unassigned/Invalid Code Points:** WAFs should be strictly configured to block HTTP requests containing overlong UTF-8 encodings, ill-formed byte sequences, or unassigned Unicode code points.
*   **Consistent Collation:** Database administrators must ensure that database collations and application-level normalizations do not implicitly convert safe Unicode characters back into dangerous ASCII execution characters without re-validating the string.

## 10. Chaining Opportunities
*   Unicode normalization bypasses are advanced, elite-tier evasion techniques that are highly effective when combined with logic flaws discovered post-[[02 - WAF Fingerprinting]].
*   They share the exact same core "Impedance Mismatch" philosophy with [[03 - URL Encoding Bypass]].
*   Often utilized when standard [[04 - Double URL Encoding]] fails against deep-inspection WAFs.

## 11. Related Notes
*   [[01 - What is a WAF and How It Works]]
*   [[02 - WAF Fingerprinting]]
*   [[03 - URL Encoding Bypass]]
*   [[04 - Double URL Encoding]]
