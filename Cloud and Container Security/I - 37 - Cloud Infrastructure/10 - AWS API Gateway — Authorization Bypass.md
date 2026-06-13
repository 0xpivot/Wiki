---
tags: [aws, api-gateway, cloud, web-security, authorization]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.10 AWS API Gateway"
---

# AWS API Gateway — Authorization Bypass

## 1. Introduction to Amazon API Gateway
Amazon API Gateway is a fully managed service that makes it easy for developers to create, publish, maintain, monitor, and secure APIs at any scale. It acts as the "front door" for applications to access data, business logic, or functionality from backend services, such as workloads running on Amazon EC2, code running on AWS Lambda, or any web application.

Because it serves as the perimeter for modern microservices and serverless architectures, securing the API Gateway is paramount. If authorization is bypassed at the gateway level, attackers gain direct, unauthenticated access to backend APIs, which often completely trust incoming requests forwarded by the gateway.

## 2. API Gateway Authorization Mechanisms
AWS API Gateway provides multiple ways to control access to APIs:
1. **AWS IAM Authorization**: Uses AWS SigV4 to sign requests. Access is controlled via IAM policies attached to the user/role making the request.
2. **Amazon Cognito User Pools**: API Gateway evaluates JWT tokens issued by a Cognito User Pool.
3. **Lambda Authorizers (Custom Authorizers)**: A custom Lambda function that executes before the API request reaches the backend. It evaluates headers (like `Authorization`) or query strings and returns an IAM policy determining if the request is allowed.
4. **API Keys & Usage Plans**: Originally designed for rate limiting and quota management, NOT for security, though often mistakenly used as primary authentication.

## 3. Vulnerability Mechanics: How Authorization is Bypassed

### 3.1 Misconfigured Lambda Authorizers
Custom Lambda Authorizers are highly prone to logical flaws. The authorizer returns an IAM policy (Allow/Deny) based on the token. 

**Common Flaws:**
- **Regex Failures**: The authorizer might use a flawed regex to extract the token from the `Authorization: Bearer <token>` header. An attacker sending `Authorization: Bearer null` or bypassing regex anchors might cause the function to fail open or improperly validate.
- **Improper JWT Validation**: The Lambda authorizer decodes the JWT but fails to verify the cryptographic signature (`kid` or `alg: none` bypass), or fails to check the `exp` (expiration) claim.
- **Overly Permissive Returned Policies**: The authorizer authenticates the user but returns a policy granting access to `execute-api:Invoke` on `Resource: "*"` instead of locking it down to the specific user's permitted routes. This leads to Broken Object Level Authorization (BOLA/IDOR) and Broken Function Level Authorization (BFLA).

### 3.2 Confusing API Keys with Authentication
API Keys in API Gateway are meant to identify clients for usage tracking and throttling (Usage Plans). They are sent in the `x-api-key` header.
Developers frequently disable true authorization (IAM/Cognito) and rely *solely* on the `x-api-key`. Since API keys are often hardcoded in client-side mobile apps or JavaScript (SPAs), attackers can easily extract them via reverse engineering or proxying traffic, leading to full API compromise.

### 3.3 "NONE" Authorization on Hidden Routes
APIs often have dozens of endpoints. A developer might properly secure `/api/v1/users` with a Cognito authorizer, but forget to apply the authorizer to `/api/v1/users/export` or a newly created `/api/v2/admin` route, leaving the authorization set to `NONE`.

### 3.4 Resource Policy Misconfigurations
API Gateway allows attaching Resource Policies (similar to S3 bucket policies) to allow/deny access based on IP address or VPC Endpoint. If an API is meant to be private (internal to a VPC) but the Resource Policy is misconfigured, it may be accessible from the public internet.

## 4. Attack Flow and Visual Architecture

```text
+-----------------------------------------------------------------------------------+
|  Attacker Client                                                                  |
|  (Postman, Burp Suite, cURL)                                                      |
|                                                                                   |
|  Request:                                                                         |
|  GET /v1/admin/delete_db HTTP/1.1                                                 |
|  Host: xxxxxxxx.execute-api.us-east-1.amazonaws.com                               |
|  Authorization: Bearer <forged_token_or_manipulated_header>                       |
|                                                                                   |
+--------+--------------------------------------------------------------------------+
         |
         | 1. HTTP Request sent to API Gateway endpoint
         v
+--------+--------------------------------------------------------------------------+
|  AWS API Gateway                                                                  |
|                                                                                   |
|  Endpoint: /v1/admin/delete_db                                                    |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Lambda Authorizer (Custom Code)                                             |  |
|  |                                                                             |  |
|  |  * Analyzes 'Authorization' header.                                         |  |
|  |  * LOGIC FLAW: Does not verify JWT signature, only checks if 'role=admin'   |  |
|  |    is present in the base64-decoded payload.                                |  |
|  |  * Returns: { "Effect": "Allow", "Resource": "arn:aws:execute-api:..." }    |  |
|  +-----------------------------+-----------------------------------------------+  |
|                                |                                                  |
|                                | 2. "Allow" Policy generated                      |
|                                v                                                  |
|  +-----------------------------+-----------------------------------------------+  |
|  | API Gateway Route Evaluation                                                |  |
|  | Access GRANTED based on flawed authorizer.                                  |  |
|  | Forwards request to backend integration.                                    |  |
|  +-----------------------------+-----------------------------------------------+  |
+--------------------------------|--------------------------------------------------+
                                 |
                                 | 3. Unauthenticated/Forged Request forwarded
                                 v
+-----------------------------------------------------------------------------------+
|  Backend Integration (e.g., AWS Lambda, EC2, or internal ALB)                     |
|                                                                                   |
|  * Implicitly trusts API Gateway.                                                 |
|  * Executes destructive action: `delete_db`                                       |
+-----------------------------------------------------------------------------------+
```

## 5. Exploitation Walkthrough

### 5.1 Scenario 1: Bypassing Custom JWT Lambda Authorizers
An attacker analyzes traffic to an API and captures their own low-privileged JWT token.
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
.
{
  "user_id": "1234",
  "role": "user"
}
.
<signature>
```
The attacker modifies the payload to `"role": "admin"`, changes the algorithm to `None` (`"alg": "none"`), removes the signature, and sends the request.
If the custom Lambda Authorizer uses a poorly written JWT parsing library that accepts `alg: none`, it evaluates the user as an admin and returns an `Allow` policy for administrative routes.

### 5.2 Scenario 2: Exploiting Caching in Authorizers
API Gateway allows caching Lambda Authorizer responses for up to 3600 seconds to save compute costs. The cache key is usually the `Authorization` header.
If an attacker registers a valid account, gets a token, and makes a request, the `Allow` policy is cached. If the cache key is not configured correctly (e.g., missing query parameters in the cache key), an attacker might access another user's data by manipulating query parameters while using their own token, and API Gateway will apply the cached `Allow` response without re-evaluating the token.

### 5.3 Scenario 3: Missing Method-Level Authorization
An attacker uses an automated tool like `ffuf` or `Kiterunner` to discover hidden endpoints on the API Gateway domain.
```bash
ffuf -w wordlist.txt -u https://xxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/FUZZ
```
They discover `/api/dev/internal_metrics`. When attempting a `GET`, they are met with `401 Unauthorized`. However, the developer forgot to apply the authorizer to the `POST` method on that same route. The attacker sends a `POST` request and successfully bypasses authorization, interacting with the backend.

## 6. Post-Exploitation Impact
Once authorization is bypassed, the impact depends entirely on the backend service.
- **Data Exfiltration**: Accessing internal APIs to dump databases.
- **SSRF**: Many API Gateway endpoints act as HTTP proxies. Bypassing auth allows attackers to use the API Gateway to launch SSRF attacks against internal VPC resources.
- **Cloud Account Takeover**: If the backend service has overly permissive IAM roles attached (e.g., a backend Lambda with `iam:*` permissions), attackers can use API parameters to execute AWS CLI commands or modify cloud infrastructure.

## 7. Mitigation and Best Practices

### 7.1 Native Authorizers Over Custom Code
Whenever possible, use Amazon Cognito User Pools or AWS IAM Authorization instead of writing custom Lambda Authorizers. Native services handle cryptographic validation, expiration, and caching securely.

### 7.2 Strict Custom Authorizer Logic
If a Lambda Authorizer must be used:
- Use well-established JWT libraries (e.g., `jsonwebtoken` in Node.js, `PyJWT` in Python).
- Explicitly enforce the signing algorithm (e.g., `algorithms=['RS256']`).
- Verify the `aud` (audience) and `iss` (issuer) claims.
- Ensure the returned IAM policy specifically restricts access to the exact resources the user is permitted to invoke, avoiding `"Resource": "*"`.

### 7.3 Do Not Use API Keys for Authentication
Stop relying on `x-api-key` headers for security. API Keys must only be used in conjunction with a robust Authorization mechanism (Cognito, IAM, OAuth2). API keys should be treated as routing/throttling identifiers, not secrets.

### 7.4 Global Authorization Enforcement
Implement Infrastructure as Code (IaC) linting (using tools like `cfn-nag` or `checkov`) in the CI/CD pipeline to ensure that `AuthorizationType: NONE` is flagged and blocked unless explicitly whitelisted for specific public endpoints.

## 8. Detection and Monitoring

### 8.1 API Gateway Access Logging
Enable full access logging for API Gateway to CloudWatch or Kinesis. Monitor for:
- High volumes of `401 Unauthorized` or `403 Forbidden` errors (indicating reconnaissance or brute-forcing).
- Requests attempting to use HTTP methods that shouldn't exist (e.g., `OPTIONS`, `PUT`, `DELETE`).

### 8.2 AWS WAF Integration
Attach AWS WAF (Web Application Firewall) directly to the API Gateway.
- Implement rate limiting.
- Block known malicious IPs.
- Use managed rules to detect SQLi, XSS, and anomalous token structures before they even reach the Authorizer.

## 9. Chaining Opportunities
- **[[15 - Serverless Security (AWS Lambda)]]**: API Gateway auth bypass is the primary entry point to exploiting vulnerable serverless Lambda functions.
- **[[11 - AWS Cognito — Misconfigured User Pools]]**: If the API uses Cognito natively, exploiting misconfigurations in the User Pool allows generating legitimate, cryptographically valid tokens that bypass gateway restrictions.
- **[[01 - API1 — Broken Object Level Authorization (BOLA)]]**: Once gateway auth is bypassed, the attacker relies on BOLA at the application layer to escalate privileges and access other users' objects.

## 10. Related Notes
- [[12 - AWS IAM Privilege Escalation]]
- [[05 - JSON Web Token (JWT) Exploitation]]
- [[33 - Microservices Architecture Security]]

## 11. Code Example: A Vulnerable Lambda Authorizer
Understanding how the vulnerability looks in code helps in identifying it during a white-box assessment.
Below is a Node.js Lambda Authorizer that fails to properly validate the JWT signature, relying only on the decoded payload:

```javascript
const jwt = require('jsonwebtoken');

exports.handler = async (event) => {
    const token = event.authorizationToken.replace("Bearer ", "");
    
    // VULNERABILITY: jwt.decode only extracts the payload, it DOES NOT verify the signature!
    const decoded = jwt.decode(token);
    
    if (decoded && decoded.role === 'admin') {
        return generatePolicy('user', 'Allow', event.methodArn);
    }
    
    return generatePolicy('user', 'Deny', event.methodArn);
};

function generatePolicy(principalId, effect, resource) {
    const authResponse = {};
    authResponse.principalId = principalId;
    if (effect && resource) {
        const policyDocument = {};
        policyDocument.Version = '2012-10-17';
        policyDocument.Statement = [];
        const statementOne = {};
        statementOne.Action = 'execute-api:Invoke';
        statementOne.Effect = effect;
        // VULNERABILITY: Returning "Resource: *" instead of the specific methodArn
        // allows the user to invoke ANY endpoint on the API Gateway.
        statementOne.Resource = '*';
        policyDocument.Statement[0] = statementOne;
        authResponse.policyDocument = policyDocument;
    }
    return authResponse;
}
```

## 12. Exploiting API Gateway Caching Misconfigurations
API Gateway allows caching responses to reduce backend load. If the API Gateway cache is configured to ignore the `Authorization` header when generating the cache key, an attacker can exploit this to access authenticated data.
1. User A (Admin) requests `GET /v1/users/financials?id=123` with their valid token.
2. API Gateway caches the response, keying it *only* by the URL path and query string.
3. User B (Attacker) requests `GET /v1/users/financials?id=123` with a low-privileged token or no token.
4. API Gateway serves the cached response belonging to User A, resulting in a severe data leak.

## 13. Securing API Keys with Usage Plans
If API keys must be used, they should be strictly tied to Usage Plans to mitigate DoS:
- Set a **Quota** (e.g., 1000 requests per month).
- Set a **Rate Limit** (e.g., 10 requests per second, burst 20).
- This ensures that even if an API key is leaked via client-side code, the attacker cannot easily use it to brute-force backend systems or rack up massive AWS billing charges before the key is rotated.
