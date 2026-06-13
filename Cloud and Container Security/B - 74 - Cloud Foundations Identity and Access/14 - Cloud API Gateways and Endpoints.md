---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.14 Cloud API Gateways and Endpoints"
---

# Cloud API Gateways and Endpoints

## 1. Introduction and Core Concepts

In modern cloud architectures, particularly those built on microservices and serverless paradigms, the API Gateway acts as the central nervous system. Services like Amazon API Gateway, Azure API Management, and Google Cloud API Gateway serve as the primary entry points—the distinct "front door"—for client applications to access backend data, business logic, or functionality.

An API Gateway sits precisely between external clients (web browsers, mobile apps, IoT devices, or third-party services) and backend services (such as EC2 instances, Lambda functions, or ECS containers). It is designed to handle a multitude of complex tasks that would otherwise burden the backend services, including request routing, protocol translation, rate limiting, authentication, authorization, caching, and comprehensive logging.

Because the API Gateway is exposed directly to the internet and orchestrates access to critical backend resources, it represents a massive and highly lucrative attack surface. A misconfigured API Gateway can bypass backend security controls entirely, exposing highly sensitive internal APIs to unauthorized access, data manipulation, or devastating denial-of-service attacks.

### 1.1 The Role of the API Gateway

The primary functions of an API Gateway include:
*   **Routing:** Directing incoming HTTP requests to the appropriate specific backend service based on the URL path and HTTP method (e.g., routing `/users` to Lambda Function A, and `/orders` to ECS Service B).
*   **Authentication & Authorization:** Verifying the identity of the requester (e.g., validating OAuth tokens, API keys, or JWTs) and ensuring they have permissions before routing the request.
*   **Rate Limiting and Throttling:** Preventing abuse, scraping, and DoS attacks by limiting the number of requests a specific client or IP can make within a given timeframe.
*   **Payload Transformation:** Modifying requests and responses on the fly (e.g., converting an XML request to JSON for the backend, or adding specific headers) to ensure compatibility.

## 2. In-Depth Architecture and Traffic Flow

Understanding how traffic flows through an API Gateway is crucial for identifying security weak points and determining where controls should be placed.

### 2.1 The Request Lifecycle
1.  **Client Request:** A client sends an HTTP request to the API Gateway's public endpoint.
2.  **Edge Routing & WAF:** The request may first pass through an Edge network (like CloudFront) and a Web Application Firewall (WAF) for initial filtering of common exploits (SQLi, XSS) and bad IP reputations.
3.  **API Gateway Evaluation:**
    *   **Throttling Check:** Does the client exceed their defined rate limit or quota? If yes, return a 429 Too Many Requests.
    *   **Authentication Check:** Is an authorizer configured (e.g., a custom Lambda Authorizer or Cognito integration)? Does the client possess a valid token?
    *   **Validation:** Does the incoming payload match the required schema definitions?
4.  **Integration Request:** The Gateway optionally transforms the request and forwards it to the backend integration.
5.  **Backend Execution:** The backend processes the request and executes business logic.
6.  **Integration Response:** The backend returns data to the Gateway.
7.  **Client Response:** The Gateway optionally transforms the response (e.g., stripping sensitive headers) and sends it back to the client.

## 3. Visualizing API Gateway Architecture

```text
                                +-------------------------------------------------------+
                                |               CLOUD ENVIRONMENT                       |
                                |                                                       |
  +-------+    HTTP/HTTPS       |  +-----------+    +-------------------------------+   |
  |       | --------------------|->| Cloud WAF |--->|         API Gateway           |   |
  | User /|                     |  +-----------+    |                               |   |
  | Attac |                     |                   |  +-------------------------+  |   |
  | ker   | <-------------------|-------------------|--| Authorization (Cognito/ |  |   |
  |       |                     |                   |  | Lambda Authorizer)      |  |   |
  +-------+                     |                   |  +-------------------------+  |   |
                                |                   |  +-------------------------+  |   |
                                |                   |  | Rate Limiting & Quotas  |  |   |
                                |                   |  +-------------------------+  |   |
                                |                   |  +-------------------------+  |   |
                                |                   |  | Request Schema Validate |  |   |
                                |                   |  +-------------------------+  |   |
                                |                   +---------------+---------------+   |
                                |                                   |                   |
                                |                                   v                   |
                                |                   +-------------------------------+   |
                                |                   |       Backend Services        |   |
                                |                   |  (Lambda, EC2, ECS, EKS)      |   |
                                |                   +-------------------------------+   |
                                +-------------------------------------------------------+
```

## 4. Threat Landscape and Vulnerabilities

API Gateways are susceptible to traditional web vulnerabilities, but their unique architecture introduces specific cloud-native risks that require specialized attention.

### 4.1 Broken Object Level Authorization (BOLA / IDOR)
BOLA is the most critical API vulnerability. It occurs when an API endpoint does not properly validate that the authenticated user is actually authorized to access the *specific object* requested. If an API Gateway routes a request like `/api/users/1234/profile` to the backend, and the backend relies solely on the Gateway for authentication but fails to perform authorization checks on user `1234`, an attacker can manipulate the ID to view or modify other users' profiles.

### 4.2 Lack of Authentication / Broken Authentication
APIs are frequently deployed without any authentication, or with deeply flawed mechanisms. 
*   **Shadow APIs:** Undocumented, forgotten, or deprecated API endpoints left active on the Gateway without proper security controls.
*   **Weak JWT Implementation:** The API Gateway might not validate the cryptographic signature of a JSON Web Token (JWT) correctly, allowing attackers to forge tokens, change the algorithm to `none`, and impersonate administrators.
*   **Over-reliance on API Keys:** API keys are designed for identifying client applications (for rate limiting), not for authenticating users. Relying on an API key as the sole security mechanism is a critical flaw, as keys are easily extracted from mobile apps, JS bundles, or intercepted in transit.

### 4.3 Mass Assignment
If the API Gateway passes the entire JSON payload directly to the backend without strict validation, an attacker can include additional, unauthorized fields (e.g., `{"username":"test", "is_admin":true}`). If the backend framework blindly binds this entire payload to an object or database record, the attacker can overwrite sensitive properties and instantly escalate privileges.

### 4.4 Lack of Rate Limiting and DoS
Without robust throttling and usage plans configured at the Gateway level, an API is totally vulnerable to Denial of Service. An attacker can flood a computationally expensive backend endpoint (e.g., an endpoint that triggers complex database queries, PDF generation, or machine learning models), leading to resource exhaustion or a severe Denial of Wallet (DoW) scenario where cloud costs skyrocket automatically.

### 4.5 Improper Data Filtering (Excessive Data Exposure)
The backend service may return a large data object containing highly sensitive data (e.g., a full user record including password hashes, internal IDs, and SSN). If the API Gateway does not actively filter this response, the sensitive data is leaked to the client. The frontend application might hide the data in the UI, but an attacker intercepting the raw API response will see everything.

## 5. Attack Vectors and VAPT Methodology

Testing API Gateways requires a specialized approach focused heavily on API logic, token manipulation, and authorization bypassing.

### 5.1 Discovery and Enumeration
1.  **Endpoint Discovery:** Identify the API Gateway URLs. Look for subdomains or predictable paths. Utilize tools like Kiterunner, Ffuf, or Dirb to brute-force endpoint paths and methods (GET, POST, PUT, DELETE).
2.  **API Documentation Hunting:** Aggressively search for exposed Swagger files, OpenAPI specifications, or GraphQL introspection endpoints. These provide a complete, detailed roadmap of the API's attack surface, including required parameters and expected data types.

### 5.2 Authentication and Authorization Testing
1.  **Bypass Attempts:** Test sensitive endpoints without any authentication tokens. If required, attempt to manipulate tokens (e.g., tamper with the payload, or use a valid token belonging to a low-privileged user on an administrative endpoint).
2.  **Testing BOLA (IDOR):** Systematically change ID parameters in the URL path, HTTP headers, and JSON body. Attempt to access, modify, or delete resources belonging to other users. Tools like Autorize (Burp Suite extension) are invaluable here.
3.  **Privilege Escalation:** If multiple user roles exist, attempt to access administrative endpoints or perform administrative actions using a standard user's token.

### 5.3 Input Validation and Business Logic
1.  **Mass Assignment:** Add unexpected fields (like `role`, `permissions`, `is_admin`, `balance`) to JSON payloads during user registration or profile updates to see if the backend accepts them.
2.  **Injection Testing:** Test for SQLi, NoSQLi, and Command Injection through the API Gateway. Since the Gateway often transforms payloads, the injection syntax might need to be adapted or URL-encoded differently.

## 6. Defense and Mitigation Strategies

Securing API Gateways requires implementing controls directly at the gateway layer to heavily protect the backend.

### 6.1 Robust Authentication and Authorization
*   **Implement Custom Authorizers:** Use mechanisms like AWS Lambda Authorizers or Amazon Cognito to enforce strict authentication *before* the request ever reaches the backend.
*   **Validate Tokens Thoroughly:** Ensure the API Gateway rigorously validates JWT signatures, expiration dates, and the `iss` (issuer) claim.
*   **Enforce Object-Level Authorization:** Authorization must happen at both the Gateway layer (verifying role-based access) and the backend layer (verifying the user actually owns the specific object requested).

### 6.2 Schema Validation
*   **Enable Request Validation:** Configure the API Gateway to validate all incoming requests against a strictly defined OpenAPI schema. Reject requests that contain unexpected parameters, wrong data types, or missing required fields. This effectively mitigates Mass Assignment and blocks many injection attacks at the edge.

### 6.3 Rate Limiting and WAF Integration
*   **Implement Usage Plans and Throttling:** Configure strict rate limits (requests per second) and burst limits for all endpoints. Use API keys associated with Usage Plans to track and tightly control client behavior.
*   **Deploy a Web Application Firewall:** Integrate a WAF (like AWS WAF) directly in front of the API Gateway to block common web exploits (SQLi, XSS), block malicious IP addresses, and mitigate automated bot traffic.

### 6.4 Response Filtering
*   **Transform Responses:** Use the API Gateway's mapping templates to explicitly filter out sensitive data from the backend response before returning it to the client. Ensure the API only returns the exact fields explicitly required by the frontend application.

## 7. Chaining Opportunities

API Gateway vulnerabilities often serve as the crucial initial entry point for deep infrastructure compromise.

*   **Shadow API + BOLA = Data Exfiltration:** An attacker discovers an unauthenticated, deprecated API endpoint (`/api/v1/exportUserData`) left active on the Gateway by mistake. They exploit a BOLA vulnerability within this endpoint by iterating through user IDs, systematically dumping the entire customer database.
*   **Lack of Rate Limiting + Expensive Lambda Execution = DoW Attack:** An API endpoint triggers a Lambda function that performs intensive image processing. Because the API Gateway has no rate limits configured, an attacker floods the endpoint with thousands of requests per second. This causes Lambda to scale massively, resulting in a crippling Denial of Wallet attack.
*   **Mass Assignment + Serverless Misconfiguration = Privilege Escalation:** An attacker registers a new account through the API. By intercepting the request in Burp Suite, they add `"role": "admin"` to the JSON payload. The API Gateway fails to validate the schema, and the backend DynamoDB blindly saves the record. The attacker logs in with their new credentials and now has full administrative access to the application.

## 8. Related Notes
*   [[01 - API1 — Broken Object Level Authorization (BOLA)]]
*   [[02 - API2 — Broken Authentication]]
*   [[12 - Serverless Computing Basics Lambda Functions]]
*   [[02 - Identity and Access Management IAM Core Principles]]
