---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Common Pitfalls and Mistakes

### Incorrect Host Header Manipulation

One common mistake is incorrectly manipulating the `Host` header. Ensure that the `Host` header is set correctly to the target internal server.

### Not Using the Same Connection

Another common pitfall is not using the same connection for both requests. Ensure that both requests are sent within the same connection to exploit the vulnerability effectively.

### Lack of Proper Validation

Improper validation of the `Host` header is a significant security risk. Always validate the `Host` header against a whitelist of trusted domains.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/01-Introduction to HTTP Host Header Attacks|Introduction to HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/03-Exploiting the Vulnerability|Exploiting the Vulnerability]]
