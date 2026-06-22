---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Common Pitfalls and Mistakes

### Incorrect Header Modification

One common mistake is incorrectly modifying the `Referer` header. Ensure that the header is set correctly and that the domain is valid.

### Firewall Blocking

Another pitfall is that the server's firewall may block interactions with external systems. This can prevent the request from reaching the Burp Collaborator server. Always check the server's firewall rules and ensure that the request is not being blocked.

### Lack of Out-of-Band Detection

Without proper out-of-band detection, it can be difficult to confirm whether the request was made successfully. Always use a reliable out-of-band detection mechanism like Burp Collaborator.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/01-Introduction to Server-Side Request Forgery (SSRF)|Introduction to Server-Side Request Forgery (SSRF)]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[03-Exploiting Blind SSRF Using Burp Suite Professional|Exploiting Blind SSRF Using Burp Suite Professional]]
