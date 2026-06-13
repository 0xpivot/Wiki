---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 24"
---

# Web QnA - Module 24 - WAF Evasion Techniques

```text
  [ Attacker Payload ] 
  <script>alert(1)</script>
           |
           v
  +-------------------+
  | Web App Firewall  | ===> [ BLOCKED ] (Regex Match: <script>)
  +-------------------+
           |
  [ Obfuscated Payload ]
  <svg/onload=eval(atob('YWxlcnQoMSk='))>
           |
           v
  +-------------------+
  | Web App Firewall  | ===> [ ALLOWED ] (No regex match for atob/eval combination)
  +-------------------+
           |
           v
  [ Target Application ] (Executes XSS)
```

## Formal Technical Questions

**Q1: Explain the concept of Impedance Mismatch in the context of WAF evasion. Provide an example.**
**Answer:**
Impedance mismatch occurs when the Web Application Firewall (WAF) parses and interprets an HTTP request differently than the backend application or the backend web server. Because the WAF and the backend use different parsing engines (e.g., the WAF is written in C, the backend is Node.js), anomalies in the HTTP protocol structure can cause the WAF to see a benign payload, while the backend extracts the malicious payload.
*Example:* HTTP Parameter Pollution (HPP). An attacker sends `GET /search?q=safe&q=<script>alert(1)</script>`. 
If the WAF is configured to only inspect the *first* instance of a parameter, it sees `q=safe` and allows the request. However, if the backend application (like ASP.NET) concatenates parameters or (like Express.js) takes the *last* parameter, the backend processes `<script>alert(1)</script>`, resulting in an XSS execution that bypassed the WAF entirely.

**Q2: How can chunked transfer encoding be utilized to bypass a WAF, and why does this technique work against older or poorly configured WAFs?**
**Answer:**
`Transfer-Encoding: chunked` is an HTTP/1.1 feature where the body of the message is sent in a series of chunks, each preceded by its size in hexadecimal. 
Attackers can split a malicious payload (like an SQL injection: `UNION SELECT`) across multiple tiny chunks:
```http
POST /submit HTTP/1.1
Host: target.com
Transfer-Encoding: chunked

5
UNION
7
 SELECT
0
```
This works against poorly configured WAFs because the WAF might inspect the stream chunk-by-chunk or fail to correctly reassemble the full request body before applying its regex signatures. The regex `UNION SELECT` never matches against the individual chunks `UNION` and ` SELECT`. The backend web server, however, fully reassembles the chunked body before passing it to the application logic, successfully executing the SQL injection.

**Q3: Describe how Unicode Normalization can be leveraged for WAF evasion.**
**Answer:**
Unicode Normalization is the process by which backend systems convert visually similar or equivalent characters into a standard base form. For example, the backend might normalize full-width characters or special ligatures into their standard ASCII equivalents.
An attacker can bypass a WAF by sending a payload using non-standard Unicode characters. For instance, instead of `<script>`, the attacker sends `＜ｓｃｒｉｐｔ＞` (Fullwidth characters). 
The WAF, applying standard ASCII regex rules, does not recognize the fullwidth characters as dangerous and lets the request pass. The backend application, during processing, normalizes the string, converting the fullwidth characters back into standard `<script>`, triggering the vulnerability.

## Scenario-Based Questions

**Q4: You are attempting an SQL injection on a parameter, but the WAF blocks any request containing spaces (`%20`, `+`) or the keyword `SELECT`. You have verified the backend is a MySQL database. How do you bypass this WAF to extract data?**
**Answer:**
To bypass the space restriction, I can use alternative whitespace characters or SQL syntax that implies separation without spaces. In MySQL, I can use inline comments `/**/` or specific control characters like `%09` (Tab), `%0A` (Newline), `%0C`, or `%0D` instead of spaces. Another technique is using parentheses: `UNION(SELECT(password)FROM(users))`.
To bypass the `SELECT` keyword filter, I can use several techniques:
1. **Case Variation:** If the WAF is case-sensitive, `SeLeCt` or `sELect`.
2. **Comment Obfuscation:** Inserting comments mid-keyword: `SEL/**/ECT` or `SEL/*foo*/ECT`. The WAF sees `SEL` and `ECT`, but MySQL strips the comment and executes `SELECT`.
3. **Encoding:** Using URL encoding, Double URL encoding (`%2553` for `S`), or Unicode escapes if the backend decodes them before the SQL query is constructed.
4. **Alternative Statements:** If extraction is the goal, bypassing `SELECT` entirely might be possible using `HANDLER` statements in MySQL (e.g., `HANDLER users OPEN; HANDLER users READ FIRST;`).

**Q5: During a Red Team engagement, you find an RCE vulnerability via Command Injection: `ping -c 1 [input]`. The WAF is strictly blocking common shell commands (`cat`, `nc`, `bash`, `sh`) and specific characters (`&`, `|`, `;`). How do you execute a reverse shell?**
**Answer:**
With logical operators blocked, I need an alternative execution trigger. Assuming the application executes the payload via `system()`, newline injection (`%0a`) can be used to execute subsequent commands: `input=127.0.0.1%0areverse_shell_payload`.
To bypass the blocked keywords (`nc`, `bash`), I will use Bash parameter expansion and string manipulation tricks:
1. **Uninitialized Variables:** `c$@at /etc/passwd` or `n$uc -e /bin/sh`. Bash ignores the empty uninitialized variable, executing `cat` and `nc`.
2. **Wildcards:** Using `/?in/?h` instead of `/bin/sh`. Bash expands this to `/bin/sh` automatically.
3. **Quote Injection:** `c"a"t /etc/passwd` or `b'a'sh`. The WAF regex misses it, but bash strips the quotes.
4. **Base64 Execution:** Since complex payloads are blocked, I can encode the payload in base64 and decode it on the fly: `echo YmFzaCAtaSA... | base64 -d | sh`. If `sh` is blocked, I use `| $0` (which often points to the current shell).

## Deep-Dive Defensive Questions

**Q6: You are configuring a Cloudflare WAF for a critical API. What are the architectural limitations of relying solely on pattern matching (regex-based rules), and how should you augment the WAF to catch zero-day evasions?**
**Answer:**
Regex-based pattern matching has severe limitations:
1. **High False Positives/Negatives:** Strict regex blocks legitimate traffic; loose regex allows obfuscated payloads.
2. **Reactive, Not Proactive:** Signatures only catch known attack patterns. Zero-days or novel obfuscations easily bypass them.
3. **Context Blindness:** A WAF doesn't understand the application logic. It doesn't know if a parameter is supposed to be an integer or an HTML string.
To augment the WAF, I would implement:
- **Positive Security Model (Allowlisting):** Instead of defining what is bad (blocklists), define what is strictly allowed. For an API, enforce strict OpenAPI/Swagger schema validation at the WAF level (API Gateway). If a parameter expects a UUID, block any request containing anything else.
- **Behavioral Analytics / Rate Limiting:** Track baseline user behavior. Even if an attacker obfuscates payloads, their behavior (scanning endpoints, high error rates, unusual request patterns) will trigger behavioral rules.
- **Context-Aware Encoding Detection:** Ensure the WAF decodes payloads up to a maximum depth (e.g., triple decoding) to catch double-encoded bypasses, and normalizes the input before applying rules.

**Q7: Explain how HTTP Request Smuggling fundamentally breaks WAF security models. Why is the WAF powerless against the smuggled request?**
**Answer:**
A WAF sits inline between the attacker and the backend server. It relies on parsing the HTTP request to inspect its headers and body. 
HTTP Request Smuggling occurs when the WAF (or frontend load balancer) and the backend server disagree on where a request ends and the next one begins, usually due to discrepancies in handling `Content-Length` (CL) and `Transfer-Encoding` (TE) headers.
If an attacker sends a crafted TE.CL or CL.TE request, the WAF parses it as a single, benign HTTP request and allows it through. However, the backend server parses the same stream differently and interprets the stream as *two* requests: the benign one, and a second, hidden "smuggled" request.
The WAF is powerless because it fundamentally did not see the second request as a separate entity. The smuggled request never passed through the WAF's rules engine independently; it piggybacked inside the body of the first request, completely evading all security checks.

## Defensive Coding Examples

**Insecure Implementation (Blind trust of WAF):**
```python
# Assuming WAF strips SQL injection, developer uses insecure concatenation
user_id = request.args.get('id')
# VULNERABLE: If an attacker bypasses the WAF regex using /**/ or Hex encoding,
# the backend executes the payload.
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Secure Implementation (Defense in Depth):**
```python
# SAFE: Even if the WAF is completely bypassed, the application is secure
# because it uses parameterized queries. The structure of the query cannot be altered.
user_id = request.args.get('id')
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## Bonus Practical Exercises

1. **Test Payload Obfuscation:**
   - Setup an AWS WAF with default managed rules or a local instance of ModSecurity.
   - Create a simple page vulnerable to XSS.
   - Attempt to execute `alert(1)` using `<script>` tags, confirm it gets blocked.
   - Now try alternative payloads like `javascript:alert(1)` in an anchor tag, or SVG vectors with `onload` events encoded in Base64.
2. **Explore SQLi Bypasses:**
   - Stand up a MySQL backend with a vulnerable PHP script.
   - Write a simple regex filter script mimicking a WAF that blocks the word `UNION`.
   - Attempt to extract data using `HANDLER` statements or comment injection `UN/**/ION`.

## Tooling & Automation

- **WAFW00F:** A tool to automatically detect the type and presence of a Web Application Firewall protecting a target.
- **Burp Suite's Bypasser Extension:** Helps automate the process of finding encoding-based bypasses.
- **SQLMap Tamper Scripts:** Use scripts like `space2comment.py`, `charencode.py`, or `between.py` in SQLMap to automatically apply evasion techniques to SQL injection payloads.

## Real-World Attack Scenario

**Scenario:** Bypassing an enterprise WAF to exploit an Unrestricted File Upload vulnerability.
1. The target application allows users to upload profile pictures. The backend has a vulnerability where it fails to validate file extensions properly, allowing PHP execution.
2. A WAF is in place, configured to block any file upload containing the string `<?php` or an extension of `.php`.
3. The attacker intercepts the multipart/form-data upload request.
4. **Bypass 1 (Extension):** The attacker changes the filename from `shell.php` to `shell.php.jpg` or `shell.php5` or `shell.phtml`. The WAF regex only looks for `.php$` at the end of the string. The backend Apache server, however, executes `.phtml` as PHP.
5. **Bypass 2 (Content):** The WAF blocks `<?php`. The attacker uses PHP short tags `<?=` or script tags `<script language="php">system($_GET['cmd']);</script>`.
6. **Bypass 3 (WAF Parsing limits):** The WAF only inspects the first 128KB of a request body for performance reasons.
7. The attacker creates a payload file: `shell.phtml`. They pad the beginning of the file with 130KB of junk data (e.g., valid JPG binary data or endless zero-bytes). 
8. At the very end of the file, past the 130KB mark, they append the PHP payload `<?=` followed by the webshell code.
9. The WAF inspects the first 128KB, sees only benign JPG bytes, and allows the request.
10. The backend server writes the entire file to disk. When accessed, the PHP interpreter parses the file, ignores the binary junk, finds the `<?=` tag, and executes the shell, resulting in RCE.

## Chaining Opportunities

- **WAF Evasion -> RCE:** Bypassing command injection filters using bash obfuscation.
- **WAF Evasion -> SQLi (Data Exfiltration):** Bypassing keyword filters to dump the database.
- **HTTP Request Smuggling -> WAF Bypass:** Using the smuggled request to attack internal administrative endpoints without WAF scrutiny.
- **WAF Evasion -> XSS:** Using obscure HTML5 vectors or esoteric JavaScript encodings (like JSFuck) to slip past XSS filters.
- **WAF Evasion -> SSRF:** Bypassing IP blocklists in SSRF payloads by using alternative IP representations (e.g., Decimal IPs, Octal IPs, IPv6 mapping).

## Related Notes

- [[01 - SQL Injection (SQLi)]]
- [[02 - Cross-Site Scripting (XSS)]]
- [[08 - Command Injection]]
- [[13 - HTTP Request Smuggling]]
- [[28 - Next-Gen WAF Architectures]]
