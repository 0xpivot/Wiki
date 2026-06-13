---
tags: [owasp, standards, framework, vapt]
difficulty: intermediate
module: "57 - OWASP Frameworks and Standards"
topic: "57.02 OWASP API Security Top 10 2023"
---

# OWASP API Security Top 10 2023 Full Walkthrough

## Executive Summary
As web architectures have evolved from monolithic structures to microservices and single-page applications (SPAs), APIs have become the primary backbone of modern software. The OWASP API Security Top 10 was created to address the unique vulnerabilities inherent to API endpoints, which often expose deeper backend logic and broader data structures than traditional web pages. The 2023 edition reflects a maturing landscape, consolidating overlapping vulnerabilities from 2019 and introducing new threats related to business logic and third-party API consumption.

## Evolution from 2019 to 2023
The 2023 list brought significant conceptual shifts:
- **API3:2023 Broken Object Property Level Authorization (BOPLA)** combined the 2019 risks of *Mass Assignment* and *Excessive Data Exposure*, recognizing that both stem from a failure to restrict access at the property level of an object.
- **API6:2023 Unrestricted Access to Sensitive Business Flows** replaced *Insufficient Logging & Monitoring*, shifting focus to automated abuse, scalping, and anti-automation failures.
- **API10:2023 Unsafe Consumption of APIs** was introduced as a new category, addressing the trust developers place in third-party APIs (e.g., Stripe, Twilio) and the risks of supply-chain style API poisoning.

## ASCII Architecture Diagram
```text
  [ Client Application ]                          [ Third-Party APIs ]
        |       ^                                          ^
        |       |                                          |
   (1) API Req  | (4) API Res                 (API10: Unsafe Consumption)
        |       |                                          |
        v       |                                          v
  +-----------------------+                    +-----------------------+
  |      API Gateway      | ---(2) Forward---> |    Microservices      |
  |  (Auth, Rate Limit)   |                    |   (Business Logic)    |
  |  API2, API4, API8     | <---(3) Process--- |  API1, API3, API5,    |
  +-----------------------+                    |  API6, API7, API9     |
                                               +-----------------------+
```

## Deep Dive into the API Top 10

### API1:2023 - Broken Object Level Authorization (BOLA)
BOLA (often called IDOR in traditional web apps) is the most critical API vulnerability. It occurs when an API endpoint receives an ID representing an object and fails to validate if the authenticated user has permission to access or modify that specific object.
- **Attack Scenarios**: An attacker changes an ID parameter in a request (`/api/v1/receipts/7100` to `/api/v1/receipts/7101`) and successfully accesses another user's financial receipt.
- **Remediation**:
  - Implement authorization checks at the code level for every API endpoint accessing data.
  - Rely on the `user_id` extracted from the secure session/token, not the one provided by the client in the payload.
  - Use randomized GUIDs/UUIDs instead of predictable sequential integers.

### API2:2023 - Broken Authentication
APIs often lack the contextual safeguards of traditional web apps. Broken authentication covers flaws in token generation, validation, password management, and missing mechanisms to prevent credential stuffing.
- **Attack Scenarios**:
  - An API accepts unsigned JWTs or tokens signed with the "none" algorithm.
  - An authentication endpoint lacks rate-limiting, allowing rapid brute-forcing.
  - The API exposes session tokens in URLs (e.g., `?token=abc`).
- **Remediation**:
  - Follow OAuth 2.0 and OpenID Connect standards correctly.
  - Enforce strict rate limiting, CAPTCHAs, or WAF rules on authentication endpoints.
  - Validate JWT signatures, expiration dates, and issuer claims on every request.

### API3:2023 - Broken Object Property Level Authorization (BOPLA)
This category addresses cases where users can read or write properties of an object they shouldn't have access to. It merges Excessive Data Exposure (sending too much data to the client and trusting them to filter it) and Mass Assignment (allowing clients to bind properties directly to internal objects).
- **Attack Scenarios**:
  - **Read**: An API returns an entire `User` object, including `hashed_password` and `ssn`, expecting the frontend to hide them.
  - **Write**: An attacker sends `{"username":"bob", "is_admin":true}` to an update endpoint, and the ORM blindly updates the `is_admin` column in the database.
- **Remediation**:
  - Never blindly bind incoming JSON payloads to backend data models. Use explicit Data Transfer Objects (DTOs).
  - Only return the exact properties required by the client interface.

### API4:2023 - Unrestricted Resource Consumption
APIs processing large payloads or highly complex queries can be subjected to Denial of Service (DoS) attacks.
- **Attack Scenarios**:
  - An attacker requests `?limit=1000000` on a pagination endpoint, causing database exhaustion.
  - Uploading a massive file or a highly compressed "zip bomb".
  - Sending deeply nested GraphQL queries that consume massive CPU.
- **Remediation**:
  - Implement strict limits on pagination, payload sizes, and execution timeouts.
  - Use cost-based rate limiting for complex queries (especially in GraphQL).

### API5:2023 - Broken Function Level Authorization (BFLA)
Unlike BOLA (which deals with data objects), BFLA deals with API functions/endpoints. It occurs when a regular user can access administrative or privileged endpoints.
- **Attack Scenarios**:
  - A user discovers and accesses an administrative endpoint like `DELETE /api/users/123`.
  - Bypassing checks by changing the HTTP method (e.g., using `PUT` instead of `GET`).
- **Remediation**:
  - Implement strict Role-Based Access Control (RBAC) or Attribute-Based Access Control (ABAC).
  - Default to deny for all API endpoints and explicitly grant access based on roles.

### API6:2023 - Unrestricted Access to Sensitive Business Flows
APIs exposing critical business functions (like purchasing tickets, creating comments, or booking rides) without protections against automated bots.
- **Attack Scenarios**:
  - Scalping bots automating the purchase of limited-edition sneakers faster than a human could.
  - Spam bots automating comment creation to manipulate SEO or spread phishing links.
- **Remediation**:
  - Identify the specific business flows that could harm the business if automated.
  - Implement device fingerprinting, CAPTCHA, and behavioral analysis (e.g., tracking the sequence of API calls).

### API7:2023 - Server Side Request Forgery (SSRF)
SSRF occurs when an API fetches a remote resource without validating the user-supplied URI. APIs often rely on webhooks, fetching profile pictures, or internal microservice communication, making SSRF highly prevalent.
- **Attack Scenarios**:
  - An API accepts a webhook URL. An attacker provides an internal AWS metadata endpoint (`http://169.254.169.254/latest/meta-data/iam/security-credentials/`) to extract cloud credentials.
- **Remediation**:
  - Validate and sanitize all client-supplied URLs using an strict allow-list.
  - Disable HTTP redirections on server-side HTTP clients.
  - Run external-fetching services in an isolated network environment.

### API8:2023 - Security Misconfiguration
Encompasses insecure default settings, incomplete configurations, open cloud storage, and misconfigured HTTP headers in the API layer.
- **Attack Scenarios**:
  - CORS policies explicitly allowing `*` or reflecting the `Origin` header blindly, permitting cross-origin data theft.
  - Detailed stack traces being returned in 500 Internal Server Error API responses.
- **Remediation**:
  - Establish a secure, automated infrastructure hardening process.
  - Define exact, restrictive CORS policies.
  - Ensure API error responses conform to a strict, non-revealing schema.

### API9:2023 - Improper Inventory Management
Because APIs expose so many endpoints, keeping track of them is notoriously difficult. Old versions (v1) often remain active alongside new versions (v2), often unpatched.
- **Attack Scenarios**:
  - An attacker discovers an unlinked, undocumented legacy endpoint (`/api/v1/users/export`) that lacks the security controls implemented in `/api/v2`.
  - Finding a "shadow API" endpoint used only by developers (`/api/staging/debug`) left exposed to the internet.
- **Remediation**:
  - Maintain an accurate, up-to-date API inventory using specifications like OpenAPI/Swagger.
  - Implement strict API lifecycle management and aggressively deprecate/remove older API versions.

### API10:2023 - Unsafe Consumption of APIs
Developers tend to blindly trust data returned from third-party APIs (e.g., payment gateways, external weather APIs). If the third-party API is compromised, the consumer application is at risk.
- **Attack Scenarios**:
  - An application stores and renders data from a third-party API without sanitization. The third party is breached, and malicious scripts are injected into the data, causing a massive XSS attack on the consumer's users.
  - An attacker manipulates a DNS response to redirect a third-party API call to a malicious server, injecting malformed data to exploit backend parsing logic.
- **Remediation**:
  - Treat all data received from external APIs as untrusted. Implement strict input validation on third-party responses.
  - Ensure TLS verification is enforced for all outbound API calls.
  - Implement timeout limits and circuit breakers to prevent third-party outages from crashing your own API.

## Chaining Opportunities
- **API9 (Inventory Management) + API1 (BOLA)**: Attackers map out shadow or legacy APIs (v1) which might lack the BOLA protections implemented in the newer v2 API, allowing massive data exfiltration.
- **API3 (BOPLA) + API5 (BFLA)**: Using Mass Assignment to inject an `is_admin: true` property into a profile update endpoint, effectively elevating privileges to access administrative functions.
- **API4 (Resource Consumption) + API6 (Business Flows)**: Abusing an unprotected business flow endpoint with a massive automated payload to simultaneously exhaust resources and conduct business fraud.

## Related Notes
- [[01 - OWASP Top 10 2021 Full Walkthrough]]
- [[03 - OWASP Mobile Top 10]]
- [[04 - OWASP Testing Guide OTG Web Application]]
- [[12 - API Security Testing Methodologies]]
- [[05 - BOLA vs BOPLA Concepts]]
