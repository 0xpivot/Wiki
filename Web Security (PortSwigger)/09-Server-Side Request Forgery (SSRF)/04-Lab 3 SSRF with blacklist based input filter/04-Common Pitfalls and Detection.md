---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Common Pitfalls and Detection

### Common Pitfalls

When dealing with SSRF vulnerabilities, several common pitfalls can lead to exploitation:

- **Incomplete Blacklists**: Relying solely on blacklists without considering alternative representations.
- **Improper Validation**: Failing to validate input thoroughly, allowing bypasses.
- **Insufficient Logging**: Not logging requests to internal systems, making it difficult to detect SSRF attempts.

### Detection

Detecting SSRF vulnerabilities requires monitoring and logging of server-side requests. Tools like intrusion detection systems (IDS) and security information and event management (SIEM) systems can help identify suspicious activity.

#### Example Detection

Monitor for requests to internal IP addresses or domains:

```bash
grep "localhost" /var/log/nginx/access.log
```

---
<!-- nav -->
[[03-Blacklist-Based Input Filtering|Blacklist-Based Input Filtering]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/05-How to Prevent  Defend Against SSRF|How to Prevent  Defend Against SSRF]]
