---
tags: [API_Security, Reconnaissance, Routing, Vulnerability]
difficulty: intermediate
module: "31 - API Security"
topic: "31.13 API Versioning Abuse"
---

# 13 - API Versioning Abuse

## 1. Executive Summary

API Versioning Abuse occurs when attackers exploit legacy, deprecated, or undocumented versions of an API to bypass security controls implemented in the current, modern version. As organizations evolve their software architecture, they frequently introduce new API versions (e.g., `/v2/`, `/v3/`) to support new features, fix bugs, or implement stricter security mechanisms like Rate Limiting, Multi-Factor Authentication (MFA), or robust Authorization checks. 

However, to maintain backward compatibility for older mobile applications, legacy business partners, or forgotten integrations, developers often leave older API versions (e.g., `/v1/`, `/mobile/v1/`) running concurrently in production. These shadow endpoints are rarely maintained, rarely monitored, and critically, lack the advanced security patching applied to the newer endpoints. Attackers deliberately hunt for these older versions, downgrading their requests to exploit vulnerabilities—such as Broken Object Level Authorization (BOLA), Mass Assignment, or weak authentication—that have long been eradicated from the primary API surface.

## 2. Anatomy of the Vulnerability

### 2.1 The Need for Versioning
APIs are contracts between the server and the client. Changing the structure of a request or response breaks that contract, causing client applications to crash. To prevent disruption, developers use versioning. 

Common versioning strategies include:
1. **URI Path Versioning:** `https://api.target.com/v1/users` (Most Common)
2. **Query Parameter Versioning:** `https://api.target.com/users?version=1.0`
3. **Custom Header Versioning:** `X-API-Version: 1`
4. **Content-Type (Accept Header) Versioning:** `Accept: application/vnd.target.v1+json`

### 2.2 The Accumulation of Technical Debt
When `/v2/` is released with strict role-based access control (RBAC) and strict input validation, `/v1/` is supposed to be deprecated and eventually decommissioned. However, due to the fear of breaking unknown legacy clients ("scream testing"), organizations often leave `/v1/` active indefinitely. 

Over time, security teams focus their penetration testing, threat modeling, and WAF rules exclusively on the `/v2/` endpoints. The `/v1/` endpoints become "Zombie APIs"—fully operational, connected to the same core production database, but entirely devoid of modern security scrutiny.

## 3. Attack Architecture & Flow

```text
       [Attacker]
           |
           | 1. Interacts with modern application, 
           |    observes modern API calls.
           |    POST /api/v2/fund_transfer (Requires 2FA / OTP)
           |    -> 403 Forbidden (MFA Required)
           |
           | 2. Attacker modifies the request, hunting for legacy endpoints.
           |    POST /api/v1/fund_transfer (Legacy Version)
           v
      [API Gateway / Load Balancer]
           |
           +-----------------------------------------+
           |                                         |
           v                                         v
   [v2 Microservice]                         [v1 Microservice]
  (Modern Auth / 2FA)                       (Basic Auth / Deprecated)
  (Strict Input Validation)                 (Trusts User Input)
           |                                         |
           X (Request bypassed)                      | 3. Processes Transfer without MFA
                                                     v
                                          [Core Production Database]
                                                     |
                                                     | 4. Database updated successfully.
                                                     |    Attacker bypasses modern security.
```

## 4. Deep Dive: Exploitation Methodologies

### 4.1 Version Discovery and Fuzzing
The first phase of the attack is reconnaissance. Attackers use tools like Burp Suite Intruder, `ffuf`, or `Kiterunner` to systematically discover hidden or deprecated API versions.

**Path Fuzzing Strategy:**
If the legitimate client uses `GET /api/v3/profile`, the attacker will fuzz the path:
```bash
ffuf -w versions.txt -u https://api.target.com/api/FUZZ/profile -H "Authorization: Bearer <token>"
```
*Wordlist (`versions.txt`):*
`v1`, `v2`, `v3`, `v1.1`, `v1.2`, `mobile/v1`, `internal/v1`, `old`, `beta`, `alpha`.

If the server responds with a `200 OK` for `/api/v1/profile`, the attacker has successfully discovered a legacy endpoint.

### 4.2 Exploiting Divergent Security Controls
Once a legacy endpoint is found, the attacker meticulously compares its behavior against the modern endpoint.

**Scenario A: Authentication Downgrade**
- `/v3/login` requires a complex password, a CAPTCHA, and an SMS OTP.
- `/v1/login` (originally built for an old mobile app) only requires a username and a 4-digit PIN, with no rate limiting.
- *Exploitation:* The attacker brute-forces the 4-digit PIN against the `/v1/login` endpoint, completely bypassing the robust security of `/v3/`.

**Scenario B: Bypassing Input Validation (Mass Assignment)**
- `/v2/users/update` strictly utilizes Data Transfer Objects (DTOs) and ignores any attempt to inject the `"is_admin": true` parameter.
- `/v1/users/update` relies on an older MVC framework that blindly binds all incoming JSON properties directly to the database model.
- *Exploitation:* The attacker sends the `"is_admin": true` payload to the `/v1/` endpoint, achieving immediate privilege escalation.

### 4.3 Uncovering Hidden Features
Legacy APIs often contain endpoints for features that were completely removed from the modern UI but were never disabled on the backend. For instance, a `/v1/export_all_users` endpoint might have been used by early administrators but was deemed too dangerous and removed from `/v2/`. An attacker discovering this endpoint can dump the entire database.

## 5. Case Studies and Real-World Impact

### 5.1 The Uber Account Takeover (Bug Bounty Example)
In a famous bug bounty report against a major ride-sharing platform, researchers discovered that while the current web application used a highly secure `/v3/` API for password resets (requiring confirmation codes), an older `/v1/` mobile API endpoint was still active. The `/v1/` endpoint allowed an attacker to change the password of any user simply by supplying the victim's phone number, bypassing all modern verification steps. The underlying database was identical, leading to massive account takeover capabilities.

### 5.2 Bypassing WAFs via Content-Type Versioning
Sometimes versioning isn't in the URL path. A modern WAF might be strictly configured to inspect traffic looking like:
`Accept: application/vnd.company.v2+json`

An attacker might manipulate the Accept header to request the older version:
`Accept: application/vnd.company.v1+json`

If the backend routes this to a legacy parser, the attacker might bypass WAF signatures entirely while simultaneously exploiting a less secure backend service.

## 6. Mitigation & Defensive Strategies

### 6.1 Aggressive Deprecation and Decommissioning
The most effective mitigation is strict API lifecycle management. When a new API version is released, the older version must have a hard, unyielding deprecation date.
- Communicate the deprecation schedule to all API consumers.
- Monitor usage of the legacy API. If usage drops to near-zero, turn it off immediately.
- Use "Brownouts" (temporarily disabling the `/v1/` API for short periods) to identify unknown legacy systems that are still relying on it.

### 6.2 Uniform Security Posture across Versions
If maintaining an older version is absolutely unavoidable due to business constraints, the underlying security mechanisms MUST be synchronized.
- **Authentication:** Both `/v1/` and `/v2/` must rely on the exact same authentication middleware.
- **Authorization:** Both versions must query the same centralized Policy Enforcement Point (PEP) to determine access rights.
- A legacy API should only return legacy data structures; it should never use legacy security logic.

### 6.3 API Gateway Enforcement
Utilize an API Gateway to strictly control which endpoints are exposed to the public internet. If `/v1/` is officially deprecated, remove its routing rule from the API Gateway. Even if the `/v1/` microservice is still running internally, the Gateway will return a `404 Not Found` or `410 Gone` to external attackers, completely nullifying the attack surface.

### 6.4 Comprehensive Inventory (API Catalog)
You cannot secure what you do not know exists. Organizations must maintain an automated API catalog (using Swagger/OpenAPI specifications) that maps every single exposed endpoint across all versions. Security scanning tools should automatically ingest these specifications to ensure comprehensive coverage during vulnerability assessments.

## 7. Chaining Opportunities
- **[[01 - Broken Object Level Authorization (BOLA)]]**: Older API versions are notoriously vulnerable to IDOR/BOLA because they were designed before strict ownership verification became a standard practice.
- **[[14 - Mass Assignment in REST APIs]]**: Legacy endpoints often lack modern strict type-checking and DTO implementation, allowing object injection.
- **[[04 - Unrestricted Resource Consumption]]**: Attackers use older APIs to bypass rate limiting present on newer endpoints to launch brute-force or DoS attacks.

## 8. Related Notes
- [[API Lifecycle Management]]
- [[Reconnaissance & Endpoint Discovery]]
- [[API Gateway Architectures]]
