---
tags: [waf, evasion, bypass, vapt]
difficulty: intermediate
module: "39 - WAF Bypass Techniques"
topic: "39.03 URL Encoding Bypass"
---

# URL Encoding Bypass

## 1. Introduction to URL Encoding Bypass
URL Encoding (formally known as Percent-Encoding, defined in RFC 3986) is a fundamental mechanism for safely transmitting data over HTTP. Because Uniform Resource Locators (URLs) can only be sent over the internet using the US-ASCII character set, characters outside this set, as well as reserved characters that have special semantic meaning in HTTP (like `&`, `=`, `?`, `/`, space), must be encoded.

The standard encoding consists of a percent sign `%` followed by the two-digit hexadecimal representation of the character's ASCII value.
*   Space ` ` -> `%20`
*   Single Quote `'` -> `%27`
*   Less than `<` -> `%3C`
*   Null Byte `\0` -> `%00`

Web Application Firewalls (WAFs) are intimately aware of URL encoding. When a WAF receives an HTTP request, its very first step in the normalization phase is to fully URL-decode the input. It must do this before passing the payload to the inspection engine; otherwise, an attacker could bypass a regex looking for `<script>` simply by sending `%3Cscript%3E`.

However, severe discrepancies in *how* the WAF decodes the payload versus *how* the backend application decodes the payload create a massive attack surface. This discrepancy is the theoretical foundation of URL Encoding WAF Bypasses.

## 2. The Impedance Mismatch in Decoding
The bypass occurs entirely due to the "Impedance Mismatch." If an attacker can craft a payload using an encoding scheme that the WAF fails to decode (or decodes incorrectly), the WAF will inspect the raw, encoded string instead of the dangerous character. 

Since the raw encoded string does not match the malicious signature (e.g., `%u0027` does not trigger the signature for `'`), the WAF deems the request benign and allows it through to the internal network.

If the backend web server or application framework understands that specific, unusual encoding scheme, it will happily decode the payload back into its malicious execution form and pass it to the database or rendering engine.

## 3. Standard vs. Non-Standard Encodings
### 3.1 Standard URL Encoding
Modern WAFs handle standard RFC-compliant encoding perfectly. Sending `%3Cscript%3E` will be decoded by the WAF to `<script>` and instantly blocked. Standard encoding alone is rarely enough to bypass a modern WAF unless the WAF is severely misconfigured (e.g., the administrator accidentally disabled the URL decoding pipeline for performance reasons).

### 3.2 Non-Standard Encodings
The key to successful bypasses lies in non-standard, legacy, or framework-specific encoding schemes that the backend supports, but the perimeter WAF is blind to.

#### 3.2.1 IIS %u Encoding (Microsoft Unicode Encoding)
Microsoft IIS web servers historically support a non-standard Unicode encoding format using `%u` followed by exactly four hexadecimal digits. This was a Microsoft specific implementation that predated modern UTF-8 URL encoding standards.
*   Standard URL Encoded Quote: `%27`
*   IIS `%u` Encoded Quote: `%u0027`

**The Exploitation Scenario:**
1.  Attacker sends a payload: `GET /?id=1%u0027+UNION+SELECT...`
2.  The WAF (e.g., an older ModSecurity setup not configured for IIS environments) does not recognize `%u` as a valid URL encoding prefix. It assumes it is literal text.
3.  The WAF inspects the literal string `1%u0027 UNION SELECT`. The signature for SQLi usually looks for a literal single quote `'` followed by SQL keywords. Since the quote isn't present in the string, the WAF allows it.
4.  The request reaches the internal IIS backend. IIS recognizes the `%u0027`, decodes it mathematically to `'`, and passes `1' UNION SELECT` to the ASP/C# application.
5.  SQL Injection succeeds.

## 4. Malformed Encodings and Parser Tolerance
What happens if an attacker sends an intentionally invalid URL encoding, like `%ZZ` or `%1`?
*   A strict, RFC-compliant WAF might block the request entirely, throwing a `400 Bad Request` for invalid encoding.
*   A lenient WAF might ignore the `%` entirely, treating it as a literal string.
*   The backend application, however, might handle it differently. For example, some legacy ASP applications or specific PHP configurations might aggressively strip the invalid `%` character to "fix" the string, turning `%ZSELECT` into `SELECT`.

If the WAF signature requires the exact word `SELECT`, but sees `%ZSELECT` and allows it, and the backend corrects it to `SELECT`, an impedance mismatch bypass has occurred.

## 5. Bypassing Regex Engines via JSON/XML Escaping
If the WAF signature is looking for a specific file path like `/etc/passwd`, an attacker might try to URL encode parts of the string. But what if the payload isn't in the URL query string, but rather inside a JSON body or an XML payload for a REST API?

In JSON, characters can be encoded using Unicode escapes: `\uXXXX`.
If the WAF does not properly parse JSON structures and normalize the Unicode escapes before applying its SQLi/XSS regex rules, an attacker can trivially bypass it by encoding the malicious keywords.

Example Malicious JSON Payload:
`{"username": "admin' \u004f\u0052 '1'='1"}`
(Where `\u004f\u0052` is the hexadecimal representation of the characters `O` and `R`).

If the WAF simply runs a flat regex for the string `OR '1'='1` across the raw HTTP body, it will completely miss the encoded `\u004f\u0052`. The backend application's JSON parser, however, will strictly decode it according to the JSON specification, resulting in successful SQL Injection.

## 6. Half-Encodings and Parameter Pollution
Sometimes, combining encoded and unencoded characters in unexpected ways can confuse WAF normalization engines while the backend handles them gracefully. 

When combined with HTTP Parameter Pollution (HPP), encoding becomes extremely potent. 
Example Payload: `?id=1&id=1%27%20OR%201=1`
If the WAF only checks the first `id` parameter (seeing `1`), but the backend concatenates them or processes the second one (decoding the injection), a bypass occurs.

## 7. ASCII Diagram: The IIS %u Encoding Bypass Flow

```text
[ Attacker Payload: GET /?id=1%u0027 OR 1=1 ]
                 |
                 v
+=============================================+
|             Web App Firewall (WAF)          |
|                                             |
| 1. URL Decoding Phase:                      |
|    Sees "%u0027". Recognizes "%u" is not    |
|    a valid standard hex encoding prefix.    |
|    Leaves string exactly as literal text.   |
|                                             |
| 2. Inspection Phase:                        |
|    Checks regex: /'.*OR.*=/i                |
|    Input evaluated: "1%u0027 OR 1=1"        |
|    Result: NO MATCH (Missing literal quote) |
|                                             |
| 3. Action: ALLOW Request                    |
+=============================================+
                 |
                 v (Raw Payload sent: id=1%u0027 OR 1=1)
+=============================================+
|             IIS Web Server Backend          |
|                                             |
| 1. URL Decoding Phase:                      |
|    Sees "%u0027". Recognizes this as the    |
|    Microsoft legacy Unicode encoding scheme.|
|    Translates "%u0027" -> "'"               |
|                                             |
| 2. Pass to Application Logic:               |
|    Variable id = "1' OR 1=1"                |
+=============================================+
                 |
                 v
+=============================================+
|             Database Engine                 |
|                                             |
|    Executes Query:                          |
|    SELECT * FROM users WHERE id = 1' OR 1=1 | <-- SQLi Execution!
+=============================================+
```

## 8. Fuzzing Strategies and Payload Generation
Discovering these parsing discrepancies during a VAPT engagement requires systematic, high-volume fuzzing. Security testers must send various encodings of standard attack characters (`'`, `"`, `<`, `>`, `\`) and carefully observe the behavior.

1.  **Baseline:** Send `test'` -> Does the WAF block it? (If yes, proceed to fuzzing).
2.  **Standard Encode:** Send `test%27` -> Does the WAF block it? (If yes, WAF decodes standard URL encoding).
3.  **Non-Standard Fuzzing:** Send `test%u0027`, `test%%2727`, `test%2527` -> Observe responses.
4.  **Error Analysis:** If the WAF allows the payload, does the backend application process it correctly, or does it crash/throw an error? If the backend throws a syntax error (e.g., an ODBC SQL syntax error), it definitively proves the payload reached the backend, bypassed the WAF entirely, and was successfully decoded into an execution context.

Tools like Burp Suite Intruder, using specialized wordlists of URL encoding variants, are essential for automating this process.

## 9. Mitigation Strategies
Defending against encoding bypasses requires harmonizing the WAF and backend configurations.
*   **Strict Decoding in WAF:** Configure the WAF to recognize and aggressively normalize all encoding schemes supported by the backend web server. If the backend is IIS, the WAF *must* be configured to decode `%u` encoding.
*   **Block Invalid Encodings:** Configure the WAF to outright block requests containing malformed or invalid percent-encodings (`%ZZ`), rather than failing open or ignoring them.
*   **Consistent Normalization:** Ensure the WAF and the backend use the exact same libraries or logical flow for decoding input, eliminating the impedance mismatch entirely.

## 10. Chaining Opportunities
*   URL Encoding principles directly lead to the discovery of [[04 - Double URL Encoding]] bypasses, which exploit recursive decoding rather than unknown encodings.
*   Understanding encoding discrepancies is a gateway to the highly complex [[05 - Unicode Normalization Bypass]] techniques.

## 11. Related Notes
*   [[01 - What is a WAF and How It Works]]
*   [[02 - WAF Fingerprinting]]
*   [[04 - Double URL Encoding]]
*   [[05 - Unicode Normalization Bypass]]
