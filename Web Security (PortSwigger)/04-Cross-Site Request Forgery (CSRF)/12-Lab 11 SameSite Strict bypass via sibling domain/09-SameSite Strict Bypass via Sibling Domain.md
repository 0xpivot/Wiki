---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## SameSite Strict Bypass via Sibling Domain

### Background Theory

The `SameSite` attribute for cookies was introduced to mitigate CSRF attacks. When set to `Strict`, the cookie is only sent with first-party requests. However, there are ways to bypass this protection, particularly through sibling domains.

#### What Are Sibling Domains?

Sibling domains are domains that share the same parent domain but differ in the subdomain level. For example, `sub1.example.com` and `sub2.example.com` are sibling domains of `example.com`.

### How the Bypass Works

An attacker can exploit sibling domains to bypass the `SameSite=Strict` restriction by setting up a malicious subdomain that shares the same parent domain as the target application. By doing so, the browser treats the request as a first-party request, allowing the cookie to be sent.

#### Example Scenario

Suppose a banking application uses `bank.example.com` and sets its cookies with `SameSite=Strict`. An attacker could register `malicious.example.com` and craft a malicious request that, when executed by the victim, will be treated as a first-party request.

### Real-World Example

In 2021, a similar technique was used in a [real-world attack](https://www.securityweek.com/critical-vulnerability-exposed-billions-of-users-to-phishing-attacks) against a popular email service. The attacker exploited sibling domains to bypass `SameSite=Strict` protections and steal session cookies.

### Code Example

Here’s an example of how an attacker might set up a sibling domain to bypass `SameSite=Strict`:

```html
<!-- Malicious page hosted on malicious.example.com -->
<a href="https://bank.example.com/transfer?amount=1000&to=attacker">Click here</a>
```

When the victim clicks the link, the browser sends the session cookie because the request is considered first-party.

### Mermaid Diagram

A diagram illustrating the sibling domain bypass:

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant Server
    User->>Server: GET /login
    Server-->>User: Set-Cookie: session_id=abc123; SameSite=Strict
    Attacker->>User: Click this link!
    User->>Attacker: GET https://malicious.example.com/malicious_page
    User->>Server: POST /transfer?amount=1000&to=attacker
    Server-->>User: Transfer successful
```

### How to Prevent / Defend

To defend against this type of attack, web applications should implement additional layers of protection:

1. **Subdomain Isolation**: Ensure that sensitive operations are performed on a dedicated subdomain that does not share the same parent domain.
2. **Strict CSP Policies**: Implement Content Security Policy (CSP) to restrict the sources of scripts and other resources.
3. **Token-Based Authentication**: Use token-based authentication methods like OAuth or JWT, which can be more resilient to such attacks.

#### Secure Coding Fix

Here’s an example of how to implement subdomain isolation:

```python
# In the server-side code
if request.host.endswith('.example.com'):
    return HttpResponseForbidden("Access denied")

# In the client-side code
<script>
if (window.location.hostname.endsWith('.example.com')) {
    alert('Access denied');
}
</script>
```

### Detection and Mitigation

Detection of such attacks can be challenging, but monitoring for unusual activity and implementing logging can help. Regularly reviewing access logs and implementing anomaly detection systems can identify potential CSRF attempts.

### Conclusion

Cross-Site Request Forgery (CSRF) remains a significant threat to web applications. Understanding the mechanics of CSRF and its variants, such as the sibling domain bypass, is crucial for developing robust security measures. By implementing strong CSRF protections and staying vigilant, developers can significantly reduce the risk of such attacks.

### Practice Labs

For hands-on experience with CSRF and related vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on CSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing various web security exploits.
- **DVWA (Damn Vulnerable Web Application)**: Another popular choice for learning about web security vulnerabilities.

These labs provide practical scenarios to understand and mitigate CSRF attacks effectively.

---
<!-- nav -->
[[08-SameSite Attribute and Its Importance|SameSite Attribute and Its Importance]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/10-Conclusion|Conclusion]]
