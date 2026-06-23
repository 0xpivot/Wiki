---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain why submitting passwords in clear text over an API is a security risk.**

Submitting passwords in clear text over an API is a significant security risk because it allows anyone who intercepts the communication to read the password directly. This can happen through various means such as network sniffing, man-in-the-middle attacks, or even by examining logs or backups. If an attacker gains access to the password, they can impersonate the user and potentially gain unauthorized access to sensitive information or systems.

**Q2. How would you test for clear text password submission vulnerabilities in an API using tools like Postman and Wireshark?**

To test for clear text password submission vulnerabilities in an API, you can use tools like Postman and Wireshark:

1. Use Postman to send requests to the API endpoints, such as login, registration, or forgot password pages.
2. Start Wireshark and set up a capture filter for HTTP traffic to monitor the network packets.
3. Send a request from Postman to the API endpoint and observe the captured packets in Wireshark.
4. Check if the password is transmitted in clear text within the request payload or headers.

Here’s an example of how you might configure Wireshark:
```plaintext
Capture Filter: http
```

Then, inspect the packet details to see if the password is visible in plain text.

**Q3. What recent real-world examples or CVEs highlight the risks of clear text password submission?**

One notable example is the breach of the popular fitness app Strava in 2018. The app allowed users to upload their GPS data, which included timestamps and locations. Attackers were able to extract sensitive information, such as the locations of military bases, by analyzing the data. Although this wasn't directly related to clear text passwords, it highlights the importance of securing all types of sensitive data.

Another example is the Heartbleed bug (CVE-2014-0160), which affected OpenSSL and allowed attackers to steal private keys and other sensitive data, including passwords, from memory. While this was due to a flaw in the encryption library rather than clear text transmission, it underscores the critical need for proper encryption and secure handling of sensitive data.

**Q4. How can you mitigate the risk of clear text password submission in APIs?**

To mitigate the risk of clear text password submission in APIs, follow these best practices:

1. **Use HTTPS**: Ensure that all API endpoints use HTTPS to encrypt the data in transit. This prevents eavesdropping and ensures that passwords are not transmitted in clear text.
2. **Implement Strong Authentication Mechanisms**: Use mechanisms like OAuth 2.0 or JSON Web Tokens (JWT) for authentication, which provide better security than simple username/password pairs.
3. **Hash Passwords**: Store passwords securely by hashing them with strong algorithms like bcrypt, scrypt, or Argon2. Never store passwords in clear text.
4. **Regular Audits and Penetration Testing**: Regularly audit your API endpoints and perform penetration testing to identify and fix vulnerabilities.
5. **Monitor Network Traffic**: Use tools like Wireshark to monitor network traffic and ensure that sensitive data is not being transmitted in clear text.

**Q5. How would you exploit a clear text password submission vulnerability in an API?**

To exploit a clear text password submission vulnerability in an API, an attacker would typically follow these steps:

1. Identify the API endpoint that accepts password submissions.
2. Use a tool like Wireshark to capture network traffic when a legitimate user submits their credentials.
3. Analyze the captured packets to locate the clear text password.
4. Use the intercepted password to authenticate as the legitimate user and access restricted resources or data.

For example, if an API endpoint `/api/v1/login` accepts a POST request with a JSON body containing `{"username": "admin", "password": "admin"}`, an attacker could use Wireshark to capture the request and extract the password.

**Q6. How can you configure an API to prevent clear text password submission?**

To configure an API to prevent clear text password submission, implement the following measures:

1. **Enable HTTPS**: Ensure that all API endpoints are accessible only via HTTPS. This encrypts the data in transit and prevents interception of clear text passwords.
2. **Use Secure Headers**: Implement secure headers such as `Content-Security-Policy`, `Strict-Transport-Security`, and `X-Frame-Options` to enhance security.
3. **Validate Input**: Validate all input parameters to ensure that they conform to expected formats and lengths.
4. **Use Strong Encryption Algorithms**: When storing passwords, use strong encryption algorithms like bcrypt, scrypt, or Argon2.
5. **Configure Access Controls**: Implement role-based access control (RBAC) and ensure that only authorized users can access sensitive endpoints.

Example configuration for enabling HTTPS in an API server using Nginx:
```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/api.example.com.crt;
    ssl_certificate_key /etc/nginx/ssl/api.example.com.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

By following these steps, you can significantly reduce the risk of clear text password submission vulnerabilities in your API.

---
<!-- nav -->
[[02-Transport Layer Security Issues Clear Text Password Submission|Transport Layer Security Issues Clear Text Password Submission]] | [[API Security/20-Transport Layer Security Issues/03-Clear Text Password Submission/00-Overview|Overview]]
