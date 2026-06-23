---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## JSON Web Tokens (JWT)

### What is JWT?

JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a JSON object that can be digitally signed using a secret or public/private key pair. This encoded information can then be securely transmitted and verified by the recipient.

#### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token and verifies that it was issued by a trusted party.

The structure looks like this:

```
<base64UrlEncode(header)>.<base64UrlEncode(payload)>.<signature>
```

### Why Use JWT?

JWTs are widely used in authentication and authorization processes due to their simplicity and flexibility. They can be easily transmitted over HTTP and are compact enough to be included in URLs, headers, or form fields.

#### Example of a JWT

Here’s an example of a JWT:

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking it down:

- **Header**:
  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
  ```

- **Signature**:
  ```plaintext
  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  ```

### How JWT Works

When a user logs in, the server generates a JWT and sends it back to the client. The client stores this token and includes it in the `Authorization` header of subsequent requests. The server can then verify the token to ensure it was issued by a trusted party and hasn’t been tampered with.

#### Steps in JWT Authentication

1. **User Logs In**: The user provides credentials (username and password).
2. **Server Generates JWT**: Upon successful authentication, the server generates a JWT containing the user’s identity and other claims.
3. **Client Stores JWT**: The client stores the JWT, typically in local storage or cookies.
4. **Client Sends JWT**: On subsequent requests, the client includes the JWT in the `Authorization` header.
5. **Server Verifies JWT**: The server verifies the JWT to ensure it was issued by a trusted party and hasn’t been tampered with.

### Claims in JWT

Claims are statements about an entity (typically the user) and additional data. There are three types of claims:

1. **Registered Claims**: These are predefined claims that are not mandatory but recommended, such as `iss`, `sub`, `aud`, `exp`, `nbf`, and `iat`.
2. **Public Claims**: These are custom claims that are defined by the application.
3. **Private Claims**: These are custom claims that are agreed upon between the parties involved.

#### Common Registered Claims

- **`iss`**: Issuer of the token.
- **`sub`**: Subject of the token (usually the user ID).
- **`aud`**: Audience for whom the token is intended.
- **`exp`**: Expiration time of the token.
- **`nbf`**: Not Before time (token is not valid before this time).
- **`iat`**: Issued At time (time when the token was issued).

### Example of a JWT with Claims

Here’s an example of a JWT with some common claims:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "iss": "GitLab Instance",
    "sub": "john.doe@example.com",
    "aud": "https://api.example.com",
    "exp": 1638374400,
    "iat": 1638288000
  },
  "signature": "..."
}
```

### Using JWT in a Secure IaC Pipeline for EKS Provisioning

In the context of a secure Infrastructure as Code (IaC) pipeline for Amazon Elastic Kubernetes Service (EKS) provisioning, JWTs can be used to authenticate and authorize requests made to the EKS API.

#### Setting Up JWT for GitLab OIDC

To set up JWT for GitLab OpenID Connect (OIDC), you need to configure the token with specific claims, particularly the `aud` claim.

##### Step-by-Step Configuration

1. **Define the Token Name**: Choose a name for your token, e.g., `GitLab OIDC token`.

2. **Set the Audience**: Define the intended audience for the token. This is typically the URL of the service that will validate the token.

3. **Configure the Provider**: Set up the provider to expect a token issued by GitLab with the specified audience.

Here’s an example configuration in a provider setup:

```yaml
provider:
  name: eks-provider
  token_name: GitLab OIDC token
  audience: https://api.example.com
```

### Full Example of JWT Configuration

Let’s walk through a complete example of setting up JWT for GitLab OIDC in an IaC pipeline.

#### Step 1: Generate the JWT

First, generate the JWT with the necessary claims. Here’s an example using Python:

```python
import jwt
import datetime

# Define the payload
payload = {
    "iss": "GitLab Instance",
    "sub": "john.doe@example.com",
    "aud": "https://api.example.com",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    "iat": datetime.datetime.utcnow()
}

# Define the secret key
secret_key = "your_secret_key"

# Generate the JWT
jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")
print(jwt_token)
```

#### Step 2: Configure the Provider

Next, configure the provider to expect the generated JWT with the specified audience.

```yaml
provider:
  name: eks-provider
  token_name: GitLab OIDC token
  audience: https://api.example.com
```

#### Step 3: Include the JWT in Requests

Include the JWT in the `Authorization` header of requests made to the EKS API.

```http
POST /api/v1/namespaces/default/pods HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
Content-Type: application/json

{
  "metadata": {
    "name": "my-pod"
  },
  "spec": {
    "containers": [
      {
        "name": "my-container",
        "image": "nginx:latest"
      }
    ]
  }
}
```

### Mermaid Diagram: JWT Flow

Here’s a mermaid diagram illustrating the flow of JWT in an IaC pipeline:

```mermaid
sequenceDiagram
  participant User
  participant GitLab
  participant EKS_API
  participant Provider

  User->>GitLab: Login
  GitLab-->>User: JWT
  User->>Provider: Request with JWT
  Provider->>EKS_API: Verify JWT
  EKS_API-->>Provider: Verified
  Provider-->>User: Response
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Hardcoding Secrets**: Avoid hardcoding secrets in your code. Use environment variables or a secrets management solution.
2. **Exposing JWTs**: Ensure JWTs are not exposed in logs or error messages.
3. **Weak Algorithms**: Use strong algorithms like `RS256` instead of `HS256` for better security.

#### Best Practices

1. **Use Strong Algorithms**: Prefer `RS256` over `HS256` for better security.
2. **Short Expiry Times**: Set short expiry times for JWTs to reduce the window of opportunity for attackers.
3. **Secure Storage**: Store JWTs securely, preferably in memory or encrypted storage.

### Real-World Examples

#### Recent Breaches

One notable breach involving JWTs was the Capital One breach in 2019. Attackers exploited a misconfigured web application firewall to access sensitive data, including JWTs. This highlights the importance of securing JWTs and ensuring proper configuration.

### How to Prevent / Defend

#### Detection

1. **Monitor Logs**: Regularly monitor logs for unauthorized access attempts.
2. **Audit Trails**: Implement audit trails to track JWT usage and detect anomalies.

#### Prevention

1. **Secure Configuration**: Ensure JWTs are configured securely with strong algorithms and short expiry times.
2. **Environment Variables**: Use environment variables to store secrets securely.

#### Secure Coding Fixes

Here’s an example of a vulnerable and secure version of JWT handling in Python:

**Vulnerable Version**

```python
import jwt
import datetime

# Define the payload
payload = {
    "iss": "GitLab Instance",
    "sub": "john.doe@example.com",
    "aud": "https://api.example.com",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    "iat": datetime.datetime.utcnow()
}

# Define the secret key
secret_key = "your_secret_key"

# Generate the JWT
jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")
print(jwt_token)
```

**Secure Version**

```python
import jwt
import datetime
import os

# Define the payload
payload = {
    "iss": "GitLab Instance",
    "sub": "john.doe@example.com",
    "aud": "https://api.example.com",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
    "iat": datetime.datetime.utcnow()
}

# Define the secret key from environment variable
secret_key = os.getenv("JWT_SECRET_KEY")

# Generate the JWT
jwt_token = jwt.encode(payload, secret_key, algorithm="RS256")
print(jwt_token)
```

### Conclusion

JWTs are a powerful tool for securing IaC pipelines, especially when provisioning EKS clusters. By understanding the structure, claims, and best practices for JWTs, you can ensure a secure and reliable pipeline. Always follow secure coding practices and regularly review configurations to prevent potential vulnerabilities.

### Practice Labs

For hands-on practice with secure IaC pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers secure coding practices.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **CloudGoat**: A series of labs designed to help you understand and mitigate cloud security risks.

These labs provide practical experience in securing IaC pipelines and can help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[03-Introduction to Secure IaC Pipeline for EKS Provisioning|Introduction to Secure IaC Pipeline for EKS Provisioning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/00-Overview|Overview]] | [[05-Secure IaC Pipeline for EKS Provisioning Pipeline Configuration for Establishing a Secure Connection|Secure IaC Pipeline for EKS Provisioning Pipeline Configuration for Establishing a Secure Connection]]
