---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Detection and Prevention

### How to Detect XXE Injection

Detection of XXE vulnerabilities can be done through automated scanning tools and manual testing.

#### Automated Scanning Tools

Tools like OWASP ZAP, Burp Suite, and Nessus can scan for XXE vulnerabilities by sending specially crafted XML payloads.

#### Manual Testing

Manual testing involves crafting and sending XML payloads that include external entity references and observing the server's response.

### How to Prevent XXE Injection

Preventing XXE injection requires configuring XML parsers to disable the processing of external entities and validating XML input.

#### Secure Configuration

1. **Disable External Entities**: Configure XML parsers to disallow the processing of external entities.
2. **Validate XML Input**: Use XML validation schemas to ensure that input conforms to expected structures.

#### Example Secure Configuration

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlInput)));
```

### Secure Coding Practices

Secure coding practices involve validating and sanitizing XML input to prevent XXE attacks.

#### Example Vulnerable Code

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlInput)));
```

#### Example Secure Code

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlInput)));
```

### Hardening XML Parsers

Hardening XML parsers involves disabling unnecessary features and ensuring that only trusted input is processed.

#### Example Hardening Configuration

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/ssax/features/external-parameter-entities", false);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlInput)));
```

### Conclusion

XXE injection is a serious security vulnerability that can lead to data exfiltration and other malicious activities. By understanding how XXE works, identifying vulnerable endpoints, and implementing secure configurations and coding practices, you can effectively prevent XXE attacks.

### Practice Labs

For hands-on practice with XXE injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs specifically designed to teach and test XXE injection.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several XXE vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable to various web attacks, including XXE.

By completing these labs, you can gain practical experience in detecting and preventing XXE injection vulnerabilities.

---
<!-- nav -->
[[04-Blind XXE with Out-of-Band Interaction|Blind XXE with Out-of-Band Interaction]] | [[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/00-Overview|Overview]] | [[06-How to Prevent  Defend Against XXE Attacks|How to Prevent  Defend Against XXE Attacks]]
