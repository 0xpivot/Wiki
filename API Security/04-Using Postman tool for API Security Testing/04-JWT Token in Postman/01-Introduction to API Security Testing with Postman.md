---
course: API Security
topic: Using Postman tool for API Security Testing
tags: [api-security]
---

## Introduction to API Security Testing with Postman

API security testing is an essential part of ensuring that your application is robust and secure against various types of attacks. One of the most popular tools used for API testing is Postman. In this chapter, we will delve into using Postman for API security testing, specifically focusing on handling JWT (JSON Web Tokens) within Postman.

### What is a JWT?

A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a token that can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

#### Why Use JWTs?

JWTs are widely used for authentication and information exchange because they are:

- **Compact**: They contain a small amount of data, making them easy to transmit over the network.
- **Self-contained**: The token contains all the necessary information about the user, reducing the need for additional database queries.
- **Stateless**: Servers do not need to store session information, which simplifies scaling and load balancing.

#### How JWTs Work

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
2. **Payload**: Contains the claims, which are statements about an entity and additional metadata.
3. **Signature**: Ensures the integrity of the token by hashing the header and payload with a secret key.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This JWT can be decoded to reveal its contents:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
}
```

### Using JWTs in Postman

Postman is a powerful tool for testing APIs. It allows you to easily manage and test different types of requests, including those that require authentication via JWTs.

#### Setting Up JWT Authentication in Postman

To set up JWT authentication in Postman, follow these steps:

1. **Obtain the JWT**: Ensure you have a valid JWT token. This token is typically obtained through an authentication endpoint.

2. **Add Authorization Header**:
   - Open Postman and create a new request.
   - Click on the `Authorization` tab.
   - Select `Bearer Token`.
   - Enter your JWT token in the `Token` field.

Here is a step-by-step example:

1. **Create a New Request**:
   - Open Postman and create a new request.
   - Set the method to `GET` and enter the URL of the API endpoint you want to test.

2. **Add Authorization Header**:
   - Click on the `Authorization` tab.
   - Select `Bearer Token`.
   - Enter your JWT token in the `Token` field.

3. **Send the Request**:
   - Click on the `Send` button to send the request.

Here is an example of a complete HTTP request with a JWT token:

```http
GET /api/user HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

The response should look like this:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

### Adding JWT to All Requests in a Collection

If you want to add the JWT to all requests in a collection, you can use the `Pre-request Script` feature in Postman.

1. **Open the Collection**:
   - Navigate to the collection where you want to add the JWT.

2. **Edit the Collection**:
   - Click on the `...` next to the collection name and select `Edit`.

3. **Add Pre-request Script**:
   - In the `Pre-request Script` section, add the following JavaScript code to set the JWT for all requests:

```javascript
// Set the JWT token for all requests in the collection
pm.environment.set("jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c");
```

4. **Use the Environment Variable**:
   - In each request, use the environment variable to set the `Authorization` header:

```javascript
// Set the Authorization header using the JWT token
pm.request.headers.add({key: "Authorization", value: "Bearer {{jwt}}"});
```

### Handling Different Types of Tokens

Sometimes, the token format might differ from the standard `Bearer` token. For example, it might be prefixed with a custom string like `CustomToken`.

#### Example: Custom Token Format

If the token format is `CustomToken <token>`, you can modify the pre-request script to handle this format:

```javascript
// Set the custom token format for all requests in the collection
pm.environment.set("customJwt", "CustomToken eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c");
```

Then, use the environment variable to set the `Authorization` header:

```javascript
// Set the Authorization header using the custom token format
pm.request.headers.add({key: "Authorization", value: "{{customJwt}}"});
```

### Real-World Examples and Breaches

#### CVE-2021-21972: OAuth 2.0 Token Exchange Vulnerability

In 2021, a critical vulnerability was discovered in OAuth 2.0 implementations, specifically in the token exchange mechanism. This vulnerability allowed attackers to obtain access tokens with elevated privileges, leading to unauthorized access to sensitive resources.

**Impact**: This vulnerability could result in unauthorized access to protected resources, leading to data breaches and loss of confidentiality.

**Mitigation**: Implement strict validation of token scopes and ensure that token exchange mechanisms are properly secured. Use tools like OAuth 2.0 security scanners to identify and mitigate such vulnerabilities.

### How to Prevent / Defend Against JWT Attacks

#### Secure Coding Practices

1. **Validate JWT Claims**: Always validate the claims in the JWT to ensure they match the expected values.
2. **Use Strong Algorithms**: Use strong algorithms like `RS256` or `ES256` for signing JWTs.
3. **Secure Storage**: Store JWTs securely, especially in client-side storage like cookies or local storage.

#### Detection and Prevention

1. **Monitor JWT Usage**: Monitor the usage of JWTs to detect any suspicious activity.
2. **Implement Rate Limiting**: Implement rate limiting to prevent brute-force attacks on JWTs.
3. **Use HTTPS**: Ensure that all communication involving JWTs is encrypted using HTTPS.

#### Secure Code Example

Here is an example of a secure code implementation for validating JWT claims:

```python
import jwt

def validate_jwt(token, secret_key):
    try:
        # Decode the JWT
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Validate the claims
        if decoded_token["sub"] != "1234567890":
            raise ValueError("Invalid subject claim")
        
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

# Example usage
try:
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    secret_key = "your_secret_key"
    validated_token = validate_jwt(token, secret_key)
    print(validated_token)
except ValueError as e:
    print(e)
```

### Conclusion

Using Postman for API security testing with JWTs is a powerful way to ensure that your application is secure and robust. By following the steps outlined in this chapter, you can effectively manage and test JWTs in your API endpoints. Additionally, by implementing secure coding practices and monitoring JWT usage, you can prevent and detect potential security issues.

### Practice Labs

For hands-on practice with API security testing using Postman, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including API security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which includes API endpoints that can be tested with Postman.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training, which includes API endpoints that can be tested with Postman.

These labs provide real-world scenarios and challenges that will help you gain practical experience in API security testing.

---
<!-- nav -->
[[API Security/04-Using Postman tool for API Security Testing/04-JWT Token in Postman/00-Overview|Overview]] | [[02-Introduction to JWT Authentication and Postman|Introduction to JWT Authentication and Postman]]
