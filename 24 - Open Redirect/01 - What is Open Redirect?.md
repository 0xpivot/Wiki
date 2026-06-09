---
tags: [vapt, open-redirect, beginner]
difficulty: beginner
module: "24 - Open Redirect"
topic: "24.01 What is Open Redirect?"
---

# 24.01 — What is Open Redirect?

## What is it?
Open Redirect is a web security vulnerability that occurs when an application takes a parameter containing a URL and blindly redirects the user to that URL without validating it. 

Because the redirect originates from a trusted domain (e.g., `https://trusted-bank.com/login?redirect=https://evil.com`), victims are highly likely to click the link, assuming the email or message is genuinely from the trusted entity. Once clicked, the trusted site issues an HTTP 302 redirect, instantly bouncing the user to the attacker's site.

While often considered a "low severity" bug by itself, Open Redirect is a critical stepping stone in complex attack chains, specifically for Phishing, OAuth token theft, and Server-Side Request Forgery (SSRF) bypasses.

Think of it like a trusted security guard standing at the front door of a bank. If you hand the guard a note that says "Please direct all customers to the dark alleyway next door," and the guard blindly points every customer into the alleyway, the guard's trusted uniform is being weaponized against the customers.

## ASCII Diagram
```text
[Victim]
   │
   │ 1. Clicks: https://trusted.com/login?next=http://evil.com
   ▼
[trusted.com (Vulnerable Web Server)]
   │
   │ 2. Processes login (or just processes the URL parameter)
   │ 3. Sets Response Header: Location: http://evil.com
   ▼
[Victim's Browser]
   │
   │ 4. Receives HTTP 302 Found (Location: http://evil.com)
   │ 5. Automatically follows redirect
   ▼
[evil.com (Attacker Server)] ─── 6. Serves fake phishing page or steals tokens!
```

## How to Find It
- **Manual steps:**
  1. Map the application and look for parameters that handle navigation, language switching, login/logout flows, or external linking.
  2. Common parameters: `redirect=`, `next=`, `url=`, `returnTo=`, `go=`, `dest=`, `target=`.
  3. Replace the valid value with an obvious external domain: `http://evil.com`.
  4. Submit the request and observe the response. 
  5. If the server responds with an HTTP 301, 302, 303, 307, or 308 redirect, and the `Location:` header points to `evil.com`, you have an Open Redirect.
  6. **Warning:** Sometimes the redirect is performed in JavaScript (e.g., `window.location = params.get('url')`). You must check both the HTTP headers and the DOM behavior.

- **Tool commands with flags explained:**
  Automated checking with `ffuf` looking for HTTP redirects (3xx status codes):
  ```bash
  # Using a wordlist of common redirect parameters
  ffuf -u "https://target.com/index.php?FUZZ=http://evil.com" \
       -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
       -mc 301,302,303,307 \
       -v | grep "evil.com"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Identify the vulnerable parameter.
  2. Craft a malicious URL pointing to a domain you control.
  3. Optionally, obfuscate the URL if there are weak filters in place (see [[03 - Bypass Techniques]]).
  4. Embed this URL in a phishing email or message sent to the victim.
  5. To escalate, check if the application uses OAuth. If so, use the Open Redirect to steal OAuth tokens.

- **Actual payloads:**
  **Basic Payloads:**
  ```text
  ?redirect=http://evil.com
  ?next=https://evil.com
  ?return_to=//evil.com
  ```

- **Real HTTP request/response examples:**
  **Vulnerable Request:**
  ```http
  GET /login?redirect=https://attacker.com/phish HTTP/1.1
  Host: trusted.com
  ```
  **Vulnerable Response:**
  ```http
  HTTP/1.1 302 Found
  Location: https://attacker.com/phish
  ```

## Real-World Example
A major cloud provider had a login portal at `login.cloud.com`. It used a `return_to` parameter so that users logging in from different services (like `mail.cloud.com` or `drive.cloud.com`) would be correctly redirected after authenticating. A bug bounty hunter noticed they could set `return_to=https://evil.com`. The hunter crafted a phishing email that looked like a legitimate security alert, linking to `https://login.cloud.com/?return_to=https://evil.com`. Users saw the legitimate `cloud.com` domain, clicked it, entered their real credentials, and were immediately bounced to a replica `evil.com` page that asked them to "verify their 2FA token," completely compromising their accounts.

## How to Fix It
- **Developer remediation:**
  Never trust user input for redirect destinations. Use a server-side map (e.g., `redirect=1` means `/home`, `redirect=2` means `/settings`). If dynamic URLs are absolutely necessary, the server must validate the URL against a strict allowlist of permitted domains or explicitly ensure the URL is a relative path (e.g., starting with `/` but not `//`).

- **Code snippet:**
  **Java / Spring (Secure Redirect using strict relative path check):**
  ```java
  public String handleLogin(String redirectParam) {
      // Ensure the redirect is a relative path to prevent external domain redirects
      // We check for startsWith("/") and explicitly reject startsWith("//") to prevent protocol-relative bypasses.
      if (redirectParam != null && redirectParam.startsWith("/") && !redirectParam.startsWith("//")) {
          return "redirect:" + redirectParam;
      }
      
      // Default fallback
      return "redirect:/dashboard";
  }
  ```

## Chaining Opportunities
- This vuln + [[05 - Open Redirect to Phishing]] → The most common and immediate abuse. Gives massive credibility to phishing campaigns.
- This vuln + [[06 - Open Redirect + OAuth (token stealing)]] → Upgrades the severity to Critical. Steal access tokens without the user even entering credentials on a phishing page.
- This vuln + [[01 - SSRF (Server-Side Request Forgery)]] → If a backend service is fetching a URL but enforces a domain allowlist, use the Open Redirect *on the allowed domain* to bounce the backend request to your internal target.

## Related Notes
- [[02 - Open Redirect in redirect= and url= Parameters]]
- [[03 - Bypass Techniques]]
- [[08 - Defense — Allowlist of Redirect Destinations]]
