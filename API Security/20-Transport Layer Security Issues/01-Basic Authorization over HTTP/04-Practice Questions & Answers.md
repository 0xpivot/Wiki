---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how basic authentication works over HTTP and why it is considered insecure.**

Basic authentication over HTTP involves sending a username and password in the request headers, typically encoded in Base64. This method is considered insecure because the credentials are transmitted in plain text. If an attacker intercepts the communication, they can decode the Base64 string and obtain the username and password. This vulnerability is particularly significant when HTTP is used instead of HTTPS, as HTTP does not encrypt the data being transmitted.

**Q2. How can an attacker exploit basic authentication over HTTP using packet sniffing tools like Wireshark?**

An attacker can use packet sniffing tools like Wireshark to capture network traffic. By filtering the captured packets for HTTP traffic, the attacker can identify requests containing basic authentication headers. These headers contain the Base64-encoded username and password. The attacker can decode these credentials to gain unauthorized access to the system. For example, if a user makes an HTTP request with basic authentication, the attacker can capture the request, decode the Base64 string, and retrieve the plaintext credentials.

**Q3. What steps should be taken to mitigate the risks associated with basic authentication over HTTP?**

To mitigate the risks associated with basic authentication over HTTP, the following steps should be taken:

1. **Use HTTPS**: Ensure that all communications are encrypted using HTTPS. This prevents attackers from intercepting and reading the transmitted data.
2. **Avoid Basic Authentication Over HTTP**: Do not use basic authentication over HTTP; instead, use secure protocols like HTTPS.
3. **Implement Strong Authentication Mechanisms**: Use stronger authentication mechanisms such as OAuth, JWT (JSON Web Tokens), or multi-factor authentication (MFA).
4. **Regular Audits and Monitoring**: Regularly audit and monitor network traffic to detect any unauthorized attempts to capture credentials.

**Q4. How does JWT (19-JSON Web Token) differ from basic authentication in terms of security and usage?**

JWT differs from basic authentication in several ways:

1. **Security**: JWTs are typically used with HTTPS and can include a signature to ensure the integrity and authenticity of the token. Basic authentication, on the other hand, transmits credentials in plain text, which is highly insecure.
2. **Usage**: JWTs are used to transmit claims between parties securely. They can be used for both authentication and authorization purposes. Basic authentication is primarily used for simple authentication scenarios.
3. **Token Structure**: A JWT contains three parts: header, payload, and signature. The header specifies the type of token and the signing algorithm. The payload contains the claims, and the signature ensures the token has not been tampered with. Basic authentication simply sends a Base64-encoded string of the username and password.

**Q5. Describe a recent real-world example where basic authentication over HTTP was exploited.**

A notable example is the widespread exploitation of IoT devices using default credentials. In many cases, these devices use basic authentication over HTTP, making it easy for attackers to intercept and decode the credentials. For instance, in the Mirai botnet attacks, attackers exploited default usernames and passwords on IoT devices to gain unauthorized access. The devices were often configured to communicate over HTTP, allowing attackers to intercept and decode the credentials, leading to large-scale DDoS attacks.

**Q6. How can you configure an API to use JWT instead of basic authentication?**

To configure an API to use JWT instead of basic authentication, follow these steps:

1. **Generate JWT Tokens**: When a user logs in, generate a JWT token that includes necessary claims such as user ID, expiration time, etc.
2. **Send JWT in Requests**: The client should send the JWT in the `Authorization` header of subsequent requests, typically prefixed with `Bearer`.
3. **Validate JWT on Server**: On the server side, validate the JWT by checking its signature and ensuring it has not expired or been tampered with.
4. **Configure API Endpoints**: Update API endpoints to expect JWT tokens instead of basic authentication headers.

Here’s a sample code snippet demonstrating how to set up JWT validation in a Node.js application using the `jsonwebtoken` library:

```javascript
const jwt = require('jsonwebtoken');

// Middleware to verify JWT
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.sendStatus(401);

    jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
}

// Example API endpoint
app.get('/protected', authenticateToken, (req, res) => {
    res.json({ message: 'This is a protected route' });
});
```

By implementing JWT, the API becomes more secure compared to using basic authentication over HTTP.

---
<!-- nav -->
[[03-Transport Layer Security Issues Basic Authorization over HTTP|Transport Layer Security Issues Basic Authorization over HTTP]] | [[API Security/20-Transport Layer Security Issues/01-Basic Authorization over HTTP/00-Overview|Overview]]
