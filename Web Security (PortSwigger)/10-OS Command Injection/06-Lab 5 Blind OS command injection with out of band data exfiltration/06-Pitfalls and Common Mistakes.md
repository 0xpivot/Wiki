---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Pitfalls and Common Mistakes

### Improper Input Validation

One common mistake is failing to validate user input properly. Always ensure that user input is sanitized and validated before being used in system commands.

### Lack of Output Redirection

Another pitfall is not redirecting the command's output properly. This can make it difficult to observe the command's effects, but it does not prevent exploitation through out-of-band methods.

### Insufficient Logging

Insufficient logging can make it challenging to detect and respond to command injection attempts. Ensure that your application logs all relevant events, including system command executions.

---
<!-- nav -->
[[05-OS Command Injection An In-Depth Analysis|OS Command Injection An In-Depth Analysis]] | [[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/00-Overview|Overview]] | [[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/07-Practice Labs|Practice Labs]]
