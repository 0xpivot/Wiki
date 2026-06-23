---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Pitfalls and Common Mistakes

### Misconfigured XML Parsers

One common mistake is using XML parsers that are configured to process external entities by default. This can be exploited by attackers to inject malicious content.

### Lack of Input Validation

Another common issue is the lack of proper input validation. Applications should validate and sanitize all XML input to prevent the inclusion of malicious content.

### Insufficient Logging and Monitoring

Insufficient logging and monitoring can make it difficult to detect XXE attacks. Proper logging and monitoring mechanisms should be in place to identify and respond to suspicious activity.

---
<!-- nav -->
[[19-Internal vs External XML Entities|Internal vs External XML Entities]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[21-Practice Labs|Practice Labs]]
