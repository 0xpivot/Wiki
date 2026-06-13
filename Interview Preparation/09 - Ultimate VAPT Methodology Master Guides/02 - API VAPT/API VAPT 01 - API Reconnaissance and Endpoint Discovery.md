---
tags: [vapt, methodology, api-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - API"
topic: "Master Guide - API VAPT 01"
---

# Ultimate VAPT Methodology: API Reconnaissance and Endpoint Discovery

## 1. Introduction to API Reconnaissance

API Reconnaissance is the absolute foundation of any robust API VAPT exercise. The goal is to discover the entire API attack surface, including documented, undocumented, deprecated, and hidden endpoints. Unlike traditional web applications, APIs are designed for machine-to-machine interaction, making them less discoverable through standard web crawling.

In a VAPT interview, demonstrating a systematic, exhaustive approach to API reconnaissance separates senior testers from juniors. You must explain not just *what* tools you use, but *why* you use them, and *how* you piece together the attack surface from disparate fragments of information.

## 2. Passive API Reconnaissance (OSINT & Scraping)

Passive reconnaissance involves mapping the API without interacting directly with the target infrastructure.

### 2.1 Github & Source Code Repositories
Developers frequently commit configuration files, Postman collections, and Swagger files into version control.
*   **Dorks:**
    *   `"target.com" AND "swagger.json"`
    *   `"target.com" AND "Authorization: Bearer"`
    *   `"target.com" AND "api/v1"`
*   **Tools:** `trufflehog`, `gitrob`, `gitleaks`.

### 2.2 Postman Public Workspaces
Postman allows users to publish workspaces. Often, internal APIs are accidentally exposed.
*   **Methodology:** Search the Postman API Network for the target company's name or specific subdomains. Analyze the requests, parameters, and authentication headers provided in the collections.

### 2.3 Wayback Machine & URL Archives
Historical endpoints (v1, v2) might have been deprecated but are still operational. These are prime targets for BOLA and Mass Assignment.
*   **Commands:**
    ```bash
    echo "target.com" | waybackurls | grep -i "api" | sort -u > wayback_apis.txt
    gau --subs target.com | grep -i "api" >> gau_apis.txt
    ```

## 3. Active API Reconnaissance (Fuzzing & Discovery)

Active reconnaissance involves sending probes to the target to uncover the API routing structure.

### 3.1 Kiterunner vs. Traditional Dirbusters
Traditional directory brute-forcers (DirBuster, Gobuster) rely on standard web wordlists. APIs, however, use specific RESTful patterns and often require specific HTTP methods (GET, POST, PUT, DELETE) and headers (`Content-Type: application/json`).
*   **Kiterunner (`kr`)** is built specifically for APIs. It uses datasets derived from millions of OpenAPI/Swagger definitions.
*   **Command:**
    ```bash
    kr scan https://api.target.com -w routes-large.kite -A=apiroutes-210228
    ```
    *Interview Talking Point:* "I prefer Kiterunner over ffuf for initial API mapping because Kiterunner understands API contexts, automatically testing various HTTP verbs and common API route structures that standard web wordlists miss."

### 3.2 Fuzzing with ffuf
Once a base path is found (e.g., `/api/v1/`), fuzz for objects and actions.
*   **Command:**
    ```bash
    ffuf -u https://api.target.com/v1/FUZZ -w /SecLists/Discovery/Web-Content/api/api-endpoints.txt -mc 200,201,401,403
    ```

### 3.3 Identifying API Versions
Always test for parallel API versions. If `v3` is secure, `v1` or `v2` might still be hosted and vulnerable to outdated exploits.
*   **Fuzzing versions:** `/api/FUZZ/users` -> `v1`, `v2`, `v3`, `mobile`, `internal`, `beta`.

## 4. API Specification Discovery

Finding the API documentation (OpenAPI/Swagger, GraphQL Introspection) is equivalent to finding the blueprint of the bank before robbing it.

### 4.1 OpenAPI / Swagger
*   **Common Paths:**
    *   `/api/swagger.json`
    *   `/swagger-ui.html`
    *   `/v1/api-docs`
    *   `/openapi.yaml`
*   **Exploitation:** If a Swagger file is found, import it into Postman or use tools like `swagger-ez` to automatically generate test requests for every single endpoint.

### 4.2 GraphQL Introspection
GraphQL endpoints typically live at `/graphql`, `/api/graphql`, or `/v1/graphql`. If Introspection is enabled, the API will reveal its entire schema (queries, mutations, types).
*   **Payload to check introspection:**
    ```graphql
    {
      __schema {
        types {
          name
        }
      }
    }
    ```
*   **Tools:** `Clairvoyance` (for bypassing disabled introspection via field guessing), `InQL` (Burp extension).

## 5. Reverse Engineering Web & Mobile Apps

### 5.1 Web Applications (SPA)
Single Page Applications (React, Angular, Vue) load the UI first, then pull data via APIs.
*   **Methodology:**
    1.  Open Chrome DevTools -> Network Tab.
    2.  Filter by `Fetch/XHR`.
    3.  Perform every action in the app (login, profile edit, checkout).
    4.  Extract endpoints, headers, and JSON structures.
    5.  Check JavaScript source maps (`.js.map`) to extract undocumented developer comments and API paths.

### 5.2 Mobile Applications (APK/IPA)
Mobile apps often use dedicated API endpoints that lack the WAF protections of the main web app.
*   **Methodology:**
    1.  Decompile APK using `jadx-gui` or `apktool`.
    2.  Search for strings like `https://`, `/api/`, `bearer`, `authorization`.
    3.  Proxy mobile traffic using Burp Suite (requires bypassing SSL Pinning using Frida or Objection).

## 6. Interview Preparation: How to Explain

### 6.1 Question: "Walk me through your methodology for discovering an undocumented API."
**Expert Answer Script:**
> "I begin with passive reconnaissance, leveraging OSINT. I search GitHub for accidentally committed Swagger files, Postman collections, and hardcoded tokens. I also use the Wayback Machine and GAU to identify deprecated endpoints, which are notorious for lacking modern security controls.
>
> Moving to active reconnaissance, I don't just use standard dirbusters. I utilize Kiterunner, which is designed specifically for API route discovery, testing various RESTful verbs against API-specific datasets. Once I establish base paths, I use `ffuf` to fuzz for specific objects and versions like `v1`, `v2`, or `beta`.
>
> Simultaneously, I actively interact with the client-side application—whether it's a web SPA or a mobile app. For SPAs, I analyze XHR requests and search JavaScript source maps for hidden routes. For mobile apps, I decompile the APK to extract hardcoded API URIs and bypass SSL pinning to proxy the traffic. Finally, I extensively search for API specification files like `swagger.json` or enabled GraphQL introspection queries, which provide a complete map of the attack surface."

### 6.2 Question: "What is the difference between testing a REST API and a Web Application?"
**Expert Answer Script:**
> "A web application returns HTML/UI components, making the attack surface heavily focused on client-side flaws like XSS or CSRF. A REST API, however, returns raw data (usually JSON or XML). The attack surface shifts heavily towards authorization flaws (BOLA/BFLA), business logic errors, mass assignment, and data exposure. Reconnaissance is also different; instead of crawling links, you must infer the object model, HTTP verbs, and data structures."

## 7. Real-World Attack Scenario

### Scenario: The Hidden Admin API via Source Maps

```ascii
+-------------------+       1. Recon JS Files       +-------------------+
|                   | ----------------------------> | app.bundle.js     |
|   Attacker        |                               | app.bundle.js.map |
| (Unauthenticated) | <---------------------------- | (Contains source) |
+-------------------+       2. Extract Routes       +-------------------+
          |
          | 3. Analyze Routes
          v
+---------------------------------------------------+
| Extracted Endpoints:                              |
| - GET /api/v1/users/profile                       |
| - POST /api/v1/users/update                       |
| - DELETE /api/v1/internal/admin/deleteUser/{id}   | <--- HIDDEN GEM
+---------------------------------------------------+
          |
          | 4. Exploit via Kiterunner / Burp
          v
+-------------------+       DELETE /api...          +-------------------+
|   Attacker        | ----------------------------> |   Target API      |
|                   | <---------------------------- |   (200 OK)        |
+-------------------+       User Deleted!           +-------------------+
```
**Breakdown:**
1.  The attacker visits a modern React application.
2.  The application doesn't expose the admin panel UI to regular users.
3.  However, the developers left `.js.map` files in the production build.
4.  The attacker extracts the source maps, revealing the entire React Router configuration, including paths that point to `/api/v1/internal/admin/`.
5.  By crafting manual HTTP requests to these hidden endpoints, the attacker finds they lack proper authentication (Broken Function Level Authorization), leading to complete application takeover.

## 8. Command Cheat Sheet & Payloads

### Fuzzing API Endpoints (ffuf)
```bash
ffuf -w wordlist.txt -u https://api.target.com/v1/FUZZ -H "Authorization: Bearer $TOKEN"
```

### Parameter Discovery (Arjun)
Once an endpoint is found, finding hidden parameters is crucial.
```bash
arjun -u https://api.target.com/v1/users/1 -m GET
```

### GraphQL Introspection Fuzzing
Sometimes introspection is disabled, but field suggestion is enabled. Tool: `clairvoyance`.
```bash
clairvoyance graphql -o schema.json https://api.target.com/graphql
```

## 9. Chaining Opportunities

*   **Reconnaissance -> BOLA:** Finding an undocumented `/api/v1/users/{id}` endpoint allows you to immediately test for Broken Object Level Authorization by enumerating IDs.
*   **Reconnaissance -> Mass Assignment:** Finding a Swagger documentation file reveals hidden parameters (e.g., `is_admin`, `role_id`). These parameters can then be injected into standard `PUT` or `POST` requests to attempt Mass Assignment.
*   **Reconnaissance -> SSRF:** Discovering webhooks or export endpoints (`/api/v1/export?url=`) during recon immediately opens the door to Server-Side Request Forgery attacks.

## 10. Related Notes
*   [[Master Guide - API VAPT 02]] - Proceed to Exploiting BOLA and Authorization Flaws.
*   [[Master Guide - API VAPT 05]] - Advanced API Exploits SSRF Mass Assignment.
*   [[OSINT Methodology]] - General web reconnaissance techniques.
*   [[Mobile Application VAPT]] - Bypassing SSL Pinning for API extraction.

---
**End of Master Guide 01**
