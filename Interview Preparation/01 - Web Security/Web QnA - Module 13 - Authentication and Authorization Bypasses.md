---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 13"
---

# Web QnA - Module 13 - Authentication and Authorization Bypasses

## Custom ASCII Diagram

```text
    [Attacker]
        |
        |  1. Captures JWT Token: eyJhbGciOiJIUzI1NiJ9...
        v
    [Local Decoding] -> Header: {"alg": "HS256"}
                     -> Payload: {"user": "guest", "role": "user"}
        |
        |  2. Modifies Header to "none" algorithm
        |  3. Modifies Payload to {"user": "admin", "role": "admin"}
        |  4. Removes Signature entirely
        v
    [Modified Token] -> eyJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ.
        |
        |  5. Sends modified JWT in Authorization header
        v
    [Web Server] -> Parses JWT
                 -> Sees "none" algorithm, skips signature validation
                 -> Trusts payload data
    [RCE/Admin Panel] <- Grants Admin Access
```

## Real-World Attack Scenario

You are engaged in a white-box penetration test for an enterprise SaaS platform. The application uses stateless authentication via JSON Web Tokens (JWT). During the code review, you notice the backend uses a flawed library that supports the `none` algorithm specification for JWT verification.

To exploit this, you register a standard user account and intercept the valid JWT assigned to your session. You decode the base64-encoded header and payload. You change the header's `alg` field from `HS256` to `none`. You then modify the payload, changing your `"role": "user"` to `"role": "admin"`. Finally, you reconstruct the JWT by concatenating the encoded header and payload with periods, but you intentionally omit the signature portion entirely, leaving a trailing period.

You inject this forged token into your HTTP requests. The backend server parses the token, reads the `none` algorithm, and bypasses the signature verification routine completely. It trusts the manipulated payload, instantly elevating your privileges to a global administrator, granting you the ability to view all tenant data and alter system configurations.

## Chaining Opportunities

1. **Auth Bypass + IDOR:** Bypassing authentication on a specific API endpoint and then utilizing Insecure Direct Object References to systematically scrape PII for all users in the database.
2. **Authorization Bypass + SSRF:** Accessing an internal-facing administrative endpoint due to poor role-based access control (RBAC), and utilizing an SSRF vulnerability on that endpoint to pivot into the internal cloud network.
3. **MFA Bypass + Account Takeover:** Exploiting a logical flaw in the multi-factor authentication flow (e.g., manipulating a `step=2` parameter to `step=3`) to achieve complete account takeover using only compromised primary credentials.
4. **OAuth State Manipulation + CSRF:** Removing the `state` parameter during an OAuth flow to link an attacker-controlled social media account to a victim's enterprise account via Cross-Site Request Forgery.
5. **Mass Assignment + Privilege Escalation:** Bypassing authorization by injecting hidden parameters (e.g., `{"username": "test", "is_admin": true}`) during the registration phase, exploiting mass assignment vulnerabilities in modern ORMs.

## Related Notes

- [[01 - Identity and Access Management IAM]]
- [[05 - JSON Web Token JWT Security]]
- [[08 - OAuth2 and OpenID Connect]]
- [[16 - API Security Best Practices]]
- [[20 - Logic Flaws and Business Logic Vulnerabilities]]

---

## Formal Technical Questions

### Q1: Detail the difference between Authentication and Authorization. Provide an example of a vulnerability that affects each.

**Answer:**
- **Authentication (AuthN):** The process of verifying *who* a user is. It confirms the user's identity. 
  - *Vulnerability Example:* Credential Stuffing, Brute Forcing, or bypassing Multi-Factor Authentication (MFA). If an attacker logs in using a weak password, they have breached authentication.
- **Authorization (AuthZ):** The process of verifying *what* a user is allowed to do. It happens after authentication and enforces permissions and access controls.
  - *Vulnerability Example:* Insecure Direct Object Reference (IDOR) or Privilege Escalation. If a standard user successfully authenticates but can access the `/admin/settings` page or view another user's private messages by changing a URL parameter, they have breached authorization.

### Q2: Explain the "Confused Deputy" problem in the context of Cross-Site Request Forgery (CSRF) and Authorization.

**Answer:**
The "Confused Deputy" problem occurs when a highly privileged entity (the deputy) is tricked by a lower privileged entity into misusing its authority on the attacker's behalf. 

In the context of web security, the browser acts as the deputy. It holds the user's authentication state (like session cookies). CSRF is a prime example: an attacker tricks a victim into clicking a link or loading a page on a malicious site. The malicious site issues a request to the vulnerable application (e.g., a bank transfer). 

Because the browser automatically attaches the victim's session cookies to the request, the receiving application believes the authorized user initiated the action. The application is "confused" into authorizing an action initiated by the attacker because the browser (the deputy) incorrectly wielded the user's authority.

---

## Scenario-Based Questions

### Q3: You discover a login endpoint with strict rate-limiting (blocking IPs after 5 failed attempts). You have a list of 10,000 potential passwords for the 'admin' account. How would you attempt to bypass this rate limit to continue brute-forcing?

**Answer:**
Rate limits are often implemented using the client's IP address. If the application is behind a load balancer or reverse proxy, it relies on HTTP headers to identify the true client IP. I would manipulate these headers to spoof my origin and bypass the rate limit:

1. **Header Rotation:** I would inject and rotate headers like `X-Forwarded-For`, `X-Originating-IP`, `X-Remote-IP`, or `X-Remote-Addr`. By changing the IP address in this header for every request (e.g., `X-Forwarded-For: 192.168.1.1`, then `.2`, etc.), the backend rate-limiter might treat each request as coming from a unique client, entirely bypassing the IP-based block.
2. **Null Bytes and Spacing:** Adding spaces or null bytes to the username (e.g., `admin ` or `admin%00`) might bypass the rate-limiter's string matching but still be normalized by the backend authentication logic.
3. **Endpoint Variation:** I would look for alternative, less-protected endpoints that perform authentication, such as mobile API endpoints (`/api/v1/mobile/login`), XML-RPC interfaces, or legacy login pages that lack rate-limiting mechanisms.

### Q4: During an assessment, you find an application using OAuth 2.0 for SSO. You notice the application does not utilize the `state` parameter during the authorization request. How can this be exploited, and what is the impact?

**Answer:**
The absence of a `state` parameter in OAuth 2.0 makes the application vulnerable to a CSRF-style attack known as "Account Linking" or "Login CSRF."

**Exploitation:**
1. As an attacker, I log into my own account on the target application and initiate the OAuth flow to link my account to a third-party provider (e.g., Google).
2. The third-party provider redirects me back to the application with an authorization code. I intercept this request and drop it before my browser completes the link.
3. I take this exact callback URL (containing my authorization code) and craft a malicious webpage containing a hidden iframe or image tag pointing to this URL.
4. I trick the victim (who is logged into their own account on the target application) into visiting my malicious page.
5. The victim's browser executes the callback URL. Because there is no `state` parameter to verify that the victim initiated the flow, the application happily accepts the authorization code.

**Impact:** The victim's account on the target application is now linked to the *attacker's* third-party Google account. The attacker can now log in to the target application using "Log in with Google," gaining complete access to the victim's account and achieving full Account Takeover (ATO).

---

## Deep-Dive Defensive Questions

### Q5: How do you architect a modern application to prevent Insecure Direct Object References (IDOR), especially in RESTful APIs heavily reliant on IDs?

**Answer:**
Preventing IDOR requires moving away from implicit trust based on knowledge of an identifier to explicit authorization checks.

1. **Implement Robust Role-Based/Attribute-Based Access Control (RBAC/ABAC):** At the core, the application must verify authorization for *every* data access request. It is never enough to know *who* the user is; the backend must verify if the authenticated user has explicit permissions to access the specific requested object (e.g., `if (user.id != requestedDocument.owner_id) throw Unauthorized`).
2. **Use Indirect Object References (Cryptographically Secure UUIDs):** Instead of sequential integer IDs (e.g., `/user/1234`), use globally unique, non-guessable identifiers (UUIDv4). While this does not fix the underlying authorization flaw, it mitigates mass-scraping and enumeration because an attacker cannot guess the IDs of other users' resources.
3. **Session-Scoped Mappings:** For highly sensitive operations, use per-session indirect references. The server maps a random, temporary token to the actual database ID. The client only sees the temporary token.
4. **Zero-Trust Backend Architecture:** Ensure that microservices do not blindly trust requests coming from the API Gateway. Contextual user identity and authorization claims must be passed along and verified at the database query level.

### Q6: Explain the difference between "Horizontal" and "Vertical" Privilege Escalation, and describe the defense mechanisms required for each.

**Answer:**
- **Horizontal Privilege Escalation (IDOR):** Occurs when a user accesses resources belonging to another user with the *same* privilege level. For example, User A viewing User B's private messages.
  - *Defense:* The application must check ownership. Every data retrieval must include an ownership clause matching the authenticated user's context (e.g., querying `SELECT * FROM messages WHERE message_id = ? AND owner_id = ?`).
- **Vertical Privilege Escalation:** Occurs when a user accesses resources or functions reserved for a *higher* privilege level. For example, a standard user accessing the administrator control panel.
  - *Defense:* The application must implement strict RBAC. Administrative routes and controllers must enforce middleware that verifies the user's role claim against a centralized authorization policy before allowing the code to execute. Relying on hiding UI elements is insufficient; the server-side API must independently validate the role for every incoming request.
