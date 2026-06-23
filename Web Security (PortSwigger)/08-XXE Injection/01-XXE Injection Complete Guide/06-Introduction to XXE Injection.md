---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Introduction to XXE Injection

### What is XXE Injection?

XML External Entity (XXE) injection is a type of security vulnerability that occurs when an application improperly processes XML input. This vulnerability allows an attacker to inject malicious XML content that can lead to various security issues, including reading sensitive files, performing port scans, interacting with internal systems, and executing denial-of-service (DoS) attacks.

### Why Does XXE Matter?

XXE injection is significant because it can expose sensitive information and allow attackers to interact with internal systems that are typically protected by firewalls. This can lead to unauthorized access, data exfiltration, and other malicious activities. Understanding and mitigating XXE vulnerabilities is crucial for securing applications that process XML data.

### How Does XXE Work Under the Hood?

XML documents can contain references to external entities, which are defined using the `<!ENTITY>` directive. These entities can reference local or remote resources. When an XML parser processes these entities, it can execute the referenced resources, leading to potential security risks.

#### Example of XML with External Entities

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

In this example, the `<!ENTITY xxe SYSTEM "file:///etc/passwd">` directive defines an external entity named `xxe` that references the `/etc/passwd` file on the local system. When the XML parser processes this document, it will attempt to read the contents of `/etc/passwd`.

### Real-World Examples of XXE Exploits

Recent real-world examples of XXE exploits include:

- **CVE-2021-3012**: A XXE vulnerability was found in the Atlassian Confluence application, allowing attackers to read arbitrary files on the server.
- **CVE-2020-14882**: A XXE vulnerability in the Oracle WebLogic Server allowed attackers to read sensitive files and perform remote code execution.

These examples highlight the severity of XXE vulnerabilities and the importance of proper mitigation strategies.

---
<!-- nav -->
[[05-Introduction to XML and XXE Injection|Introduction to XML and XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[07-What is an XXE Injection Vulnerability|What is an XXE Injection Vulnerability]]
