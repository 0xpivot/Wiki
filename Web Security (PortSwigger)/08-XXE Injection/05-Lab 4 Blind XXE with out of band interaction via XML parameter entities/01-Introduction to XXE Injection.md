---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Introduction to XXE Injection

### What is XXE Injection?

XML External Entity (XXE) injection is a type of attack against an application that parses XML input. This attack occurs when an application improperly processes XML input containing references to external entities. These external entities can reference local or remote resources, leading to various types of vulnerabilities such as information disclosure, denial of service, or even remote code execution.

### Why Does XXE Matter?

XXE attacks are significant because they can lead to severe security issues. For instance, an attacker could exploit an XXE vulnerability to read sensitive files on the server, execute commands, or even exfiltrate data. This makes XXE a critical vulnerability to understand and mitigate.

### How Does XXE Work Under the Hood?

When an application parses XML input, it typically uses an XML parser. If the parser is not configured correctly, it may process external entities referenced within the XML input. These entities can be defined using `<!ENTITY>` declarations. For example:

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root><data>&xxe;</data></root>
```

In this example, the `&xxe;` entity references the `/etc/passwd` file on the server. If the XML parser is not properly configured to disable external entity processing, it will attempt to read the contents of `/etc/passwd` and include it in the parsed XML.

### Common Mistakes Without XXE Prevention

Without proper prevention measures, applications are vulnerable to XXE attacks. This can lead to unauthorized access to sensitive data, denial of service, and other malicious activities. For instance, an attacker could use an XXE attack to read sensitive files, execute commands, or even cause the application to crash.

---
<!-- nav -->
[[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/00-Overview|Overview]] | [[02-Blind XXE Injection with Out-of-Band Interaction|Blind XXE Injection with Out-of-Band Interaction]]
