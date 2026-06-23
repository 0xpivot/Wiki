---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## How to Prevent / Defend Against XXE Injection

### Detection

To detect XXE vulnerabilities, you can use tools like Burp Suite, OWASP ZAP, or static analysis tools like SonarQube.

### Prevention

To prevent XXE vulnerabilities, follow these best practices:

- **Disable External Entity Resolution**: Configure your XML parser to disable external entity resolution.
- **Validate Input**: Validate all XML input to ensure it does not contain malicious entities.
- **Use Secure Libraries**: Use libraries that are known to be secure and up-to-date.

### Secure Coding Fixes

#### Vulnerable Code

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlInput)));
```

#### Secure Code

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlInput)));
```

### Configuration Hardening

#### Nginx Configuration

Ensure that Nginx is configured to reject requests containing XML input.

```nginx
location / {
    if ($request_body ~* "<!DOCTYPE") {
        return 403;
    }
}
```

#### Apache Configuration

Ensure that Apache is configured to reject requests containing XML input.

```apache
<Directory "/var/www/html">
    SetEnvIfNoCase Content-Type "^application/xml" bad_xml_request
    Order allow,deny
    Allow from all
    Deny from env=bad_xml_request
</Directory>
```

### Mitigations

- **Web Application Firewalls (WAF)**: Use WAFs to filter out malicious XML input.
- **Regular Audits**: Regularly audit your applications for XXE vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/08-XXE Injection/04-Lab 3 Blind XXE with out of band interaction/04-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/08-XXE Injection/04-Lab 3 Blind XXE with out of band interaction/00-Overview|Overview]] | [[Web Security (PortSwigger)/08-XXE Injection/04-Lab 3 Blind XXE with out of band interaction/06-Understanding XXE Injection|Understanding XXE Injection]]
