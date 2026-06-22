---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## How to Prevent / Defend Against XXE Attacks

### Detection

To detect XXE attacks, organizations should implement logging and monitoring mechanisms that track unusual activity related to XML parsing. This includes monitoring for unexpected network requests, file reads, and other suspicious behavior.

### Prevention

To prevent XXE attacks, organizations should follow these best practices:

1. **Disable External Entity Processing**:
   - Disable the processing of external entities in the XML parser.
   - This can be done by setting the appropriate configuration options in the XML parser library.

2. **Validate and Sanitize Input**:
   - Validate and sanitize all XML input to ensure that it does not contain malicious entities.
   - Use a whitelist approach to allow only trusted XML content.

3. **Use Secure Coding Practices**:
   - Follow secure coding practices to avoid introducing vulnerabilities in the first place.
   - Use libraries and frameworks that have built-in protections against XXE attacks.

### Secure-Coding Fixes

Here is an example of how to securely configure an XML parser to prevent XXE attacks:

#### Vulnerable Configuration

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new File("input.xml"));
```

#### Secure Configuration

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new File("input.xml"));
```

### Configuration Hardening

To harden the configuration of the XML parser, organizations should set the following features:

- `http://apache.org/xml/features/disallow-doctype-decl`: Set to `true` to disallow DOCTYPE declarations.
- `http://apache.org/xml/features/nonvalidating/load-external-dtd`: Set to `false` to prevent loading external DTDs.

### Mitigations

To mitigate the impact of XXE attacks, organizations should implement the following mitigations:

1. **Network Segmentation**:
   - Segment the network to limit the spread of attacks.
   - Use firewalls and network segmentation to isolate sensitive systems.

2. **Access Controls**:
   - Implement strict access controls to limit the ability of attackers to access sensitive data.
   - Use role-based access control (RBAC) to ensure that users have only the necessary permissions.

3. **Regular Audits**:
   - Perform regular audits to identify and remediate vulnerabilities.
   - Use automated tools to scan for XXE vulnerabilities and other security issues.

### Hands-On Labs

For hands-on practice with XXE attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on XXE injection and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

These labs provide a safe environment to practice and understand XXE attacks in depth.

By thoroughly understanding the concepts, mechanics, and defenses against XXE attacks, organizations can better protect themselves from these types of vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/05-Detection and Prevention|Detection and Prevention]] | [[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/00-Overview|Overview]] | [[07-Lab Setup and Environment|Lab Setup and Environment]]
