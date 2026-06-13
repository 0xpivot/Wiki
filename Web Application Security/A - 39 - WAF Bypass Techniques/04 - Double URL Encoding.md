---
tags: [waf, evasion, bypass, vapt]
difficulty: intermediate
module: "39 - WAF Bypass Techniques"
topic: "39.04 Double URL Encoding"
---

# Double URL Encoding Bypass

## 1. Introduction to Double URL Encoding
Double URL Encoding is a classic, highly reliable, and frequently encountered technique for bypassing Web Application Firewalls (WAFs) and Input Validation filters. It builds directly upon the concepts of standard URL encoding but specifically exploits architectural flaws in how multiple distinct layers of an application stack handle the decoding process sequentially.

The core premise of the attack is mathematically simple: encode the malicious character, and then immediately URL-encode the resulting percent sign (`%`) of that first encoding.

**The Construction Process:**
1.  **Target Character:** `'` (Single Quote)
2.  **First URL Encoding:** `%27` (The standard hex representation)
3.  **Second URL Encoding:** The `%` symbol in the string `%27` is encoded. The standard URL encoding for a percent sign is `%25`.
4.  **Resulting Payload:** `%2527`

When an attacker transmits `%2527` to a server, they are transmitting a double-encoded single quote.

## 2. Why Does Double Encoding Work?
The bypass relies entirely on a fundamental architectural misalignment between the perimeter security device (the WAF) and the internal backend application layer regarding *how many times* an incoming string should be decoded before processing.

### 2.1 The WAF's Perspective (Single Pass)
Most WAFs are configured for performance reasons to perform a single, strict pass of URL decoding during their normalization phase.
1.  **Ingest:** WAF receives payload: `%2527`
2.  **Decode:** WAF URL-decodes the string once: `%25` mathematically becomes `%`, resulting in the string `%27`.
3.  **Inspect:** The WAF Inspection Engine runs its regex signatures against the resulting string: `%27`.
4.  **Evaluate:** The signature for SQL Injection is looking for a literal `'` character or SQL keywords. It sees the literal string `%27`. Because `%27` is not a SQL keyword and is not a literal quote, the WAF deems the payload completely safe and allows the request to pass.

### 2.2 The Backend's Perspective (The Second Pass)
The bypassed request, now containing the string `%27` (because some proxies forward the decoded version, or the backend web server decodes the original `%2527` upon receipt), reaches the application.

Here is where the vulnerability crystallizes: The backend application code (e.g., PHP scripts, Java Servlets, Node.js controllers) or a specific framework routing component performs *another* layer of URL decoding.

1.  **Ingest:** Application logic receives: `%27`
2.  **Decode:** Application layer logic explicitly calls `urldecode()` or an equivalent framework method on the input.
3.  **Result:** `%27` becomes `'` (Single Quote).
4.  **Execution:** The single quote is then passed directly into the database query string or rendered into the HTML response DOM.
5.  **Impact:** The attack (SQLi, XSS, LFI) executes successfully, completely subverting the WAF.

## 3. The Architecture of the Vulnerability
For a double encoding bypass to be successful, two absolute conditions must be met in the target environment:
1.  **The Perimeter Failure:** The WAF must only decode the input once (or fail to recursively decode until no encodings remain).
2.  **The Backend Flaw:** The backend application must decode the input *at least one more time* than the WAF did.

This dangerous double-decoding in the backend is almost always unintentional. It usually occurs due to:
*   **Redundant Developer Logic:** The web server container (e.g., Apache/Nginx/Tomcat) automatically decodes the URL upon receiving it, passing the clean variables to the application layer. However, the developer, wanting to be "safe" and ensure everything is decoded properly, explicitly wraps the variable in `urldecode()` in their source code.
*   **Complex Framework Routing:** Advanced routing frameworks (like Apache Struts, Spring MVC, or custom middleware) process the URI path and automatically decode parameters for routing purposes, and then pass them to a controller which decodes them again for business logic.

## 4. Common Attack Vectors and Payloads

Double encoding is extremely versatile and can serve as the delivery mechanism for almost any injection vulnerability.

### 4.1 Path Traversal (LFI/RFI)
Path traversal relies heavily on the `../` sequence to escape web roots.
*   Standard sequence: `../`
*   Single Encoding: `%2E%2E%2F`
*   Double Encoding: `%252E%252E%252F`
*   **Payload Execution:** `https://target.com/download.php?file=%252E%252E%252F%252E%252E%252Fetc%252Fpasswd`

### 4.2 Cross-Site Scripting (XSS)
XSS relies on breaking out of HTML contexts using `<script>` tags and quote characters.
*   Standard character: `<`
*   Single Encoding: `%3C`
*   Double Encoding: `%253C`
*   **Payload Execution:** `https://target.com/?search=%253Cscript%253Ealert(1)%253C%252Fscript%253E`

### 4.3 SQL Injection (SQLi)
SQLi relies on breaking syntax using quotes and SQL keywords.
*   Standard character: `'`
*   Single Encoding: `%27`
*   Double Encoding: `%2527`
*   **Payload Execution:** `https://target.com/login.php?user=admin%2527+UNION+SELECT+1,2,3--`

## 5. ASCII Diagram: The Double Encoding Flow

```text
[ External Attacker Payload: %2527 UNION SELECT ]
                 |
                 v
+===================================================+
|               Web App Firewall (WAF)              |
|                                                   |
| 1. URL Decode (Pass 1):                           |
|    %2527 translates to %27                        |
|                                                   |
| 2. Inspection Engine:                             |
|    Evaluates string: "%27 UNION SELECT"           |
|    Regex for SQLi looks for literal quote (').    |
|    Regex fails to match.                          |
|                                                   |
| 3. Action: ALLOW Request to Backend               |
+===================================================+
                 |
                 v (Forwarded Payload: %27)
+===================================================+
|        Backend Web Server Container               |
|        (e.g., Apache Tomcat, IIS)                 |
|                                                   |
| 1. Container Decode:                              |
|    The server may decode %27 or pass it raw       |
|    depending on proxy configuration.              |
+===================================================+
                 |
                 v (Variable passed to code: %27)
+===================================================+
|        Application Business Logic (PHP/Java)      |
|                                                   |
| 1. Redundant Developer Code:                      |
|    $user_id = urldecode($_GET['user']);           |
|                                                   |
| 2. Final Malicious Decode:                        |
|    %27 translates to literal '                    |
+===================================================+
                 |
                 v (Payload is now: ' UNION SELECT)
+===================================================+
|               Database Engine                     |
|                                                   |
|    Executes injected SQL syntax!                  |
+===================================================+
```

## 6. Identifying Double Decode Vulnerabilities
Finding these vulnerabilities during a black-box VAPT engagement requires systematic, structured fuzzing.
1.  **Baseline Check:** Submit a safe string: `test` -> Observe reflection or application behavior.
2.  **Single Encode Check:** Submit single encoded string: `%74%65%73%74` -> If it reflects exactly as `test`, the backend is decoding the input at least once.
3.  **Double Encode Check:** Submit double encoded string: `%2574%2565%2573%2574` -> 
    *   If it reflects as `test`, the backend is explicitly double decoding! You have found a structural vulnerability.
    *   If it reflects as `%74%65%73%74`, the backend only decoded it once, and double encoding bypasses will not work on this parameter.

## 7. Triple Encoding and Deep Nesting
If a modern application stack has three distinct layers of decoding (e.g., Edge Web Server -> Internal API Gateway -> Framework Routing -> Application logic), triple encoding might be necessary.
*   **Triple Encoding for `'`:** `%252527` (Encode `%` to `%25`, then encode the first `%` of that new string to `%25` -> `%2525`).
While rare, testing for up to 3 levels of encoding is a standard practice in thorough VAPT engagements for highly complex enterprise environments.

## 8. Mitigation Strategies
*   **WAF Recursive Decoding:** Configure the WAF to *recursively* decode all input until the string no longer changes mathematically (i.e., until all `%` encodings are fully resolved) *before* applying inspection rules. Modern WAFs often have a setting to limit recursive decoding depth (e.g., max 3 iterations) to prevent Denial of Service (DoS) via infinite decoding loops.
*   **Architectural Review:** Developers must be educated to trust the web server/framework container to handle URL decoding securely. Avoid calling functions like `urldecode()` or `URLDecoder.decode()` manually on input parameters unless explicitly and architecturally required for a specific business logic flow.

## 9. Chaining Opportunities
*   Double encoding is very frequently the delivery mechanism for exploiting severe backend vulnerabilities (RCE, SQLi) that are otherwise heavily guarded by static WAF signatures.
*   Concepts learned here align closely with [[03 - URL Encoding Bypass]] and prepare the tester for [[05 - Unicode Normalization Bypass]].

## 10. Related Notes
*   [[01 - What is a WAF and How It Works]]
*   [[02 - WAF Fingerprinting]]
*   [[03 - URL Encoding Bypass]]
*   [[05 - Unicode Normalization Bypass]]
