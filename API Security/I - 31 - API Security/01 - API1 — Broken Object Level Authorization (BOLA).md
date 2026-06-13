---
tags: [API, Web-Security, BOLA, IDOR, OWASP-API, Authorization]
difficulty: beginner
module: "31 - API Security"
topic: "31.01 API1 - Broken Object Level Authorization (BOLA)"
---

# 31.01 API1 — Broken Object Level Authorization (BOLA)

## 1. Executive Summary
Broken Object Level Authorization (BOLA), historically known in web application security as Insecure Direct Object Reference (IDOR), is arguably the most pervasive and critical vulnerability within modern Application Programming Interfaces (APIs). APIs inherently expose endpoints that manipulate distinct objects (e.g., users, financial records, medical profiles). When an API fails to adequately validate whether the currently authenticated user possesses the requisite privileges to interact with the specific object requested, a BOLA vulnerability manifests. This oversight allows attackers to access, modify, or delete data belonging to other users, leading to severe confidentiality and integrity breaches.

## 2. Core Mechanics and Underlying Theory
The shift from traditional monolithic architectures to microservices and single-page applications (SPAs) has pushed state management and rendering to the client side. APIs act as the crucial data pipeline. Consequently, APIs frequently accept object identifiers (IDs) supplied by the client to fetch or alter state. 

BOLA occurs when the API implicitly trusts the client-provided object ID. The logic flow typically follows this path:
1. The client requests a resource, passing an identifier (e.g., `GET /api/v1/users/7154`).
2. The server authenticates the client (e.g., verifying a JWT).
3. The server queries the database for the object `7154`.
4. The server returns the object.

**The flaw:** Between steps 2 and 3, the server omits the crucial authorization check: *Does the user identified by the JWT have the right to access user 7154?*

### 2.1 The Role of Identifiers
Identifiers are the linchpin of BOLA.
- **Sequential IDs:** Integers that increment (1, 2, 3...). These are trivial to guess, making BOLA highly exploitable via simple enumeration.
- **UUIDs/GUIDs:** While UUIDv4 offers 122 bits of randomness (virtually unguessable), relying on UUIDs as a security measure is a fundamental flaw known as *security by obscurity*. If an attacker discovers a UUID via information disclosure or metadata leakage, the BOLA vulnerability can still be fully exploited.

## 3. Architectural Context

The diagram below illustrates the disparity between a secure authorization flow and a vulnerable BOLA flow.

```text
========================================================================================
                          BOLA ATTACK ARCHITECTURE DIAGRAM
========================================================================================

      [ Attacker (User ID: A) ]
                 |
                 | 1. GET /api/v1/financial_records/B
                 V
   +---------------------------+
   |        API Gateway        | --> Routes request
   +---------------------------+
                 |
                 V
   +---------------------------+
   |   Authentication Service  | --> Validates User A's JWT. (AuthN passes)
   +---------------------------+
                 |
                 V
   +---------------------------+
   |   Authorization Service   | --> MISSING OR FLAWED IN BOLA!
   |  (Should check if A owns  |     API assumes A is authorized for B.
   |   record B)               |
   +---------------------------+
                 |
                 V
   +---------------------------+
   |      Database Engine      | --> SELECT * FROM records WHERE id = 'B'
   +---------------------------+
                 |
                 | 2. Returns Record B
                 V
      [ Attacker (User ID: A) ]   <-- EXPLOITATION SUCCESSFUL

========================================================================================
```

## 4. Attack Vectors and Threat Modeling

BOLA is not limited to simple GET requests. The threat model encompasses all CRUD operations:
- **Read (GET):** Extracting sensitive PII, financial data, or operational secrets.
- **Create (POST):** Creating resources under another user's context, potentially leading to quota exhaustion or spoofing.
- **Update (PUT/PATCH):** Modifying configurations, changing shipping addresses, or altering account recovery emails.
- **Delete (DELETE):** Dropping resources, leading to targeted Denial of Service (DoS) or data destruction.

### 4.1 Parameter Pollution and Type Juggling
Attackers may manipulate how parameters are processed to bypass rudimentary filters:
- Array injection: `?id[]=123&id[]=456`
- JSON Type Juggling: Sending `{"user_id": {"$ne": 1}}` in MongoDB-backed APIs to trigger NoSQL injection alongside BOLA.
- HPP (HTTP Parameter Pollution): `GET /api/user?id=1&id=2` — depending on the backend, it might authorize ID 1 but query ID 2.

## 5. Step-by-Step Testing Methodology

### 5.1 Reconnaissance and Mapping
1. **Endpoint Discovery:** Map all API endpoints using tools like Burp Suite, Postman, or automated crawlers (e.g., Kiterunner). Look for endpoints containing IDs (`/users/{id}`, `/accounts/{id}/settings`).
2. **Identifier Extraction:** Gather your own user's IDs. Look in URL parameters, POST body JSON, headers (e.g., `X-User-Id`), and cookies.

### 5.2 Active Exploitation
1. **Account Creation:** Create two distinct accounts with different privilege levels (if applicable) or same privilege levels (Tenant A and Tenant B).
2. **Baseline Establishment:** Authenticate as User A. Request User A's resources.
3. **ID Substitution:** Authenticate as User A. Request User B's resources by replacing User A's ID with User B's ID.
4. **Behavior Analysis:**
   - `200 OK`: Vulnerable (Full BOLA).
   - `401 Unauthorized`: Authentication failed (Token expired/invalid).
   - `403 Forbidden`: Secure (BOLA mitigated).
   - `404 Not Found`: Potentially secure, or ID doesn't exist, or the backend is masking the authorization failure.

### 5.3 Automated Testing Tools
- **Autorize (Burp Extension):** Automates BOLA testing by replaying all requests passing through Burp with a lower-privileged user's token.
- **AuthMatrix:** Another Burp extension for complex authorization matrices.
- **Postman/Newman:** Scripting automated test suites that explicitly swap tokens and assert response codes.

## 6. Source Code Analysis

### 6.1 Vulnerable Implementation (Node.js / Express)
```javascript
app.get('/api/v1/documents/:docId', authenticateToken, async (req, res) => {
    try {
        // VULNERABLE: Only checking if the document exists, not WHO owns it.
        const document = await Document.findById(req.params.docId);
        
        if (!document) {
            return res.status(404).send('Document not found');
        }
        
        res.json(document);
    } catch (err) {
        res.status(500).send('Server Error');
    }
});
```

### 6.2 Secure Implementation (Node.js / Express)
```javascript
app.get('/api/v1/documents/:docId', authenticateToken, async (req, res) => {
    try {
        // SECURE: Enforcing Object Level Authorization
        // The query mandates that the document must belong to the authenticated user.
        const document = await Document.findOne({
            _id: req.params.docId,
            ownerId: req.user.id // req.user populated by authenticateToken middleware
        });
        
        if (!document) {
            // Returning 404 instead of 403 prevents object enumeration
            return res.status(404).send('Document not found');
        }
        
        res.json(document);
    } catch (err) {
        res.status(500).send('Server Error');
    }
});
```

## 7. Advanced Exploitation Techniques

### 7.1 Cross-Tenant BOLA in SaaS
In multi-tenant applications, BOLA can cross tenant boundaries. An attacker in Tenant A might manipulate an ID to access a resource in Tenant B. This is catastrophic as it breaches logical isolation.

### 7.2 Blind BOLA
Sometimes an API endpoint alters state without returning the object. For example, `POST /api/v1/users/7154/promote`. The attacker receives a `200 OK` but doesn't see the result. Verification requires secondary channels or observable state changes.

### 7.3 Chained IDOR
Exploiting an Information Disclosure to find hidden IDs, then leveraging those IDs in a BOLA attack. For example, a `GET /api/public/users` might leak private internal IDs, which are then used in `DELETE /api/internal/users/{id}`.

## 8. Remediation Strategy & Zero-Trust

### 8.1 Enforce Authorization Matrices
Developers must explicitly define an authorization matrix mapping Roles to Actions to Resources. Every data-access layer query must include the user's context.

### 8.2 Attribute-Based Access Control (ABAC)
Transition from simple Role-Based Access Control (RBAC) to ABAC. ABAC evaluates attributes (user department, document classification, time of day) to make dynamic authorization decisions.

### 8.3 Unpredictable Identifiers
While not a fix for BOLA, migrating from sequential IDs to UUIDv4 reduces the surface area for enumeration attacks.

### 8.4 API Gateway and Service Mesh Policies
Implement authorization policies at the API gateway level using technologies like Open Policy Agent (OPA).

## 9. Chaining Opportunities
- **Information Disclosure -> BOLA:** Leaking UUIDs makes UUID-protected endpoints susceptible to BOLA.
- **BOLA -> BFLA:** Using BOLA to alter an admin's account state, elevating privileges.
- **BOLA -> Mass Assignment:** Combining ID substitution with excessive payload data to overwrite another user's properties.

## 10. Related Notes
- [[02 - API2 — Broken Authentication]]
- [[03 - API3 — Broken Object Property Level Authorization]]
- [[05 - API5 — Broken Function Level Authorization (BFLA)]]
