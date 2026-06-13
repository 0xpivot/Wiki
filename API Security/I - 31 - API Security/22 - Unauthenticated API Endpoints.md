---
tags: [API, Security, Authentication, Endpoint, Discovery, Reconnaissance]
difficulty: beginner
module: "31 - API Security"
topic: "31.22 Unauthenticated API Endpoints"
---

# Unauthenticated API Endpoints

## Introduction
Unauthenticated API Endpoints are API routes that are accessible without any form of identity verification (e.g., no session cookie, no bearer token, no API key). While some endpoints are designed to be public (like login, registration, or public health checks), developers frequently leave sensitive endpoints exposed unintentionally. This happens due to routing misconfigurations, forgotten legacy endpoints, or flawed assumptions about endpoint obscurity (the false belief that an attacker won't find the route).

In the OWASP API Security Top 10, this often falls under Broken User Authentication or Improper Inventory Management, but the sheer prevalence of completely unprotected endpoints merits a dedicated deep dive. Discovering unauthenticated endpoints is the bread and butter of API penetration testing and bug bounty hunting.

## Root Causes of Unauthenticated Endpoints

1. **Missing Route Guards:** Modern web frameworks (Express.js, Spring Boot, Django) require developers to explicitly apply middleware or decorators to secure routes. Forgetting to apply the `requireAuth` middleware to a newly created endpoint leaves it completely open.
2. **Shadow APIs:** Old versions of APIs (e.g., `/api/v1/users` instead of `/api/v2/users`) that were never decommissioned. The authentication logic might have been updated on `v2`, but `v1` was left running on legacy code without modern security controls.
3. **Internal/Microservice Exposure:** APIs intended only for internal microservice-to-microservice communication (which might implicitly trust all internal traffic) are accidentally exposed to the internet via API gateway misconfigurations.
4. **Debug/Dev Endpoints:** Endpoints like `/api/dev/reset-password` or `/api/test/dump-db` created during development to speed up testing but never removed before production deployment.
5. **Overly Permissive Regex:** API Gateway routing rules using poorly constructed regular expressions that accidentally whitelist sensitive paths (e.g., allowing `^/api/public/.*` but an attacker accesses `/api/public/../private/data`).

## Architecture and Attack Flow

```text
+-----------------------+
|   Attacker (No Auth)  |
+-----------------------+
           |
           | 1. Discovers undocumented endpoint
           |    (e.g., /api/v1/internal/users)
           v
+-----------------------+      2. Missing Auth Check      +-----------------------+
|                       |-------------------------------->|                       |
|      API Gateway /    |                                 |   Backend Service /   |
|      Load Balancer    |                                 |   Database            |
|                       |<--------------------------------|                       |
+-----------------------+      3. Sensitive Data Returned +-----------------------+
           |
           | 4. Data Exfiltration
           v
+-----------------------+
|   Attacker Receives   |
|   PII, Credentials,   |
|   Internal Configs    |
+-----------------------+
```

### Flow Breakdown
1. **Discovery:** The attacker uses recon techniques (fuzzing, JS analysis, OSINT) to find endpoints that are not linked in the main application UI.
2. **Missing Auth Check:** The attacker sends a request to the discovered endpoint without an `Authorization` header. The API Gateway or application router fails to enforce authentication.
3. **Backend Processing:** The backend service processes the request, assuming it is legitimate or internal, and queries the database.
4. **Exfiltration:** The sensitive data is returned to the unauthenticated attacker.

## Discovery Techniques (How to find them)

Finding unauthenticated endpoints requires rigorous reconnaissance.

### 1. JavaScript File Analysis
Modern Single Page Applications (SPAs) often contain all frontend routing and backend API calls in their compiled JavaScript bundles.
- Use tools like `LinkFinder` or `JSParser` to extract all relative and absolute URLs from JavaScript files.
- Look for endpoints with keywords like `admin`, `internal`, `v1`, `beta`, `test`.
- Test every extracted endpoint without authentication.

### 2. API Documentation Exploitation
Developers frequently expose Swagger/OpenAPI documentation, Postman collections, or GraphQL introspection endpoints.
- Check common paths: `/api/swagger.json`, `/api-docs`, `/v3/api-docs`, `/openapi.yaml`, `/graphql`.
- If you find documentation, import it into Postman or Burp Suite. Strip all auth headers and fire requests at every single endpoint to see which ones return a `200 OK` with sensitive data instead of a `401 Unauthorized`.

### 3. Fuzzing and Brute Forcing
Use wordlists specifically designed for API discovery (e.g., SecLists `api-endpoints.txt`, `common-api-endpoints-mazen160.txt`).
- Tools: `ffif`, `gobuster`, `feroxbuster`.
- Example: `ffuf -w api-endpoints.txt -u https://target.com/api/FUZZ`
- Pay attention to `403 Forbidden` responses. A `403` implies the endpoint exists but you are denied. Sometimes, bypassing the proxy or changing the HTTP method (e.g., GET to POST) can bypass poorly written auth checks.

### 4. Wayback Machine and Archive Analysis
Old endpoints might be removed from the current JS files but still active on the server.
- Use `gau` (GetAllUrls) or `waybackurls` to fetch historical URLs for the target domain.
- Filter for API paths and test them without authentication.

### 5. Mobile Application Decompilation
Mobile apps often talk to legacy APIs or hidden endpoints to support older versions of the app.
- Decompile the APK using `jadx`.
- Search for `http://` or `https://` strings, or look for Retrofit/OkHttp interface definitions.

## Exploitation Scenarios

### Scenario 1: The Forgotten Export Endpoint
An application has a dashboard for administrators to export user data. The endpoint is `/api/admin/users/export`.
- The developer secured the frontend UI so only admins can see the "Export" button.
- However, they forgot to add the `@IsAdmin` decorator to the backend endpoint.
- An attacker discovers the endpoint via JS analysis, sends a `GET` request without logging in, and downloads a CSV of all user PII.

### Scenario 2: Microservice Accidental Exposure
A company uses a microservice architecture. Service A (Frontend Auth) handles user logins. Service B (User Management) handles internal user queries.
- Service B is designed to be internal-only and has no authentication logic.
- A misconfiguration in the Nginx Ingress Controller accidentally maps `/api/users/*` to Service B directly, bypassing Service A.
- The attacker queries `/api/users/12345` and gets full details of user 12345 without any tokens.

### Scenario 3: Bypassing Auth via Method Tampering
An endpoint `/api/v1/profile` requires authentication for `GET` requests (to view the profile) and `PUT` requests (to update it).
- The framework's security config explicitly maps `GET` and `PUT` to the auth middleware.
- The attacker sends a `HEAD` or `PATCH` request. The router routes the request to the handler, but the security middleware ignores it because it doesn't match the specific HTTP methods. The attacker achieves unauthenticated access.

## Remediation and Secure Design

### 1. Default Deny Architecture
Implement a "secure by default" routing mechanism. The API gateway or application framework should block all access to all endpoints by default.
- Developers must explicitly opt-in to make an endpoint public (e.g., applying an `@Public` decorator).
- If an endpoint lacks an explicit visibility declaration, it should return `401 Unauthorized`.

### 2. Centralized Authentication Enforcement
Do not rely on individual developers remembering to add auth checks to their specific controllers.
- Enforce authentication at the API Gateway level (e.g., Kong, AWS API Gateway) before the request ever reaches the backend microservice.
- Validate JWT signatures, scopes, and expiration centrally.

### 3. Continuous API Discovery and Inventory
You cannot secure what you do not know exists.
- Maintain an automated, up-to-date OpenAPI/Swagger definition.
- Use DAST (Dynamic Application Security Testing) tools integrated into the CI/CD pipeline to crawl and fuzz for undocumented or unauthenticated endpoints before deploying to production.

### 4. Decommission Legacy APIs Properly
Do not just remove UI links to old APIs.
- When an API version is deprecated, set a hard sunset date.
- Tear down the infrastructure and remove the code for `v1` once `v2` is fully adopted.

## Chaining Opportunities
- **[[03 - API3 — Broken Object Property Level Authorization]]**: An unauthenticated endpoint might allow mass assignment if the attacker guesses the JSON schema, enabling account takeover without even having an account.
- **[[06 - API6 — Unrestricted Access to Sensitive Business Flows]]**: Unauthenticated endpoints are prime targets for automated bot attacks (scalping, credential stuffing).
- **[[12 - Improper Inventory Management]]**: Unauthenticated endpoints are almost always a symptom of poor inventory and shadow APIs.

## Related Notes
- [[02 - API2 — Broken User Authentication]]
- [[API Gateway Security Patterns]]
- [[Authentication vs Authorization]]
