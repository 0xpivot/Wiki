---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Common Pitfalls and Mistakes

### Incorrect Payload Encoding

One common mistake is not properly encoding the payload. If the payload is not correctly encoded, it may be sanitized or blocked by the server.

### Missing Key Combinations

Another common mistake is forgetting to include the specified key combinations. Without these key combinations, the payload may not be executed in the intended browser.

### Incomplete Escaping

If the escaping mechanism is incomplete, it may allow for the injection of a script. Always ensure that user input is properly validated and sanitized.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/02-Background Theory|Background Theory]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[04-Detailed Exploit Walkthrough|Detailed Exploit Walkthrough]]
