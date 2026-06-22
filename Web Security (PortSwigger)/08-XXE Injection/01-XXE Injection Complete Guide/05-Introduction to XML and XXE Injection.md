---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Introduction to XML and XXE Injection

### What is XML?

XML (Extensible Markup Language) is a markup language used to encode documents in a format that is both human-readable and machine-readable. It is widely used for data interchange between systems and applications. XML documents consist of elements, attributes, and text content. Elements are defined by tags, which are enclosed in angle brackets (`<` and `>`).

#### Example of an XML Document

```xml
<?xml version="1.0"?>
<person>
    <name>John Doe</name>
    <age>30</age>
    <city>New York</city>
</person>
```

### Why is XML Important?

XML is important because it provides a standardized way to represent structured data. It is used in various applications such as web services, configuration files, and data storage. Understanding XML is crucial for developers and security professionals because many systems rely on XML for data exchange.

### XML Syntax

To understand XML vulnerabilities, it is essential to know the basic syntax of XML. Here are some key components:

- **Elements**: Defined by opening and closing tags.
- **Attributes**: Additional information associated with an element.
- **Text Content**: Data within the element tags.

#### Example of XML with Attributes

```xml
<?xml version="1.0"?>
<person id="1">
    <name>John Doe</name>
    <age>30</age>
    <city>New York</city>
</person>
```

### XML External Entities (XXE)

XML External Entities (XXE) is a type of vulnerability that occurs when an XML processor evaluates external entities within an XML document. An external entity is a reference to an external resource, such as a file or URL, that is included in the XML document.

#### Example of an External Entity

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>&xxe;</root>
```

In this example, the `&xxe;` entity references the `/etc/passwd` file on the server. When the XML parser processes this document, it will attempt to read the contents of the `/etc/passwd` file and include it in the parsed output.

### Why XXE Matters

XXE vulnerabilities can lead to serious security issues, including:

- **Data Exfiltration**: Reading sensitive files on the server.
- **Denial of Service (DoS)**: Causing the XML parser to crash or consume excessive resources.
- **Remote Code Execution (RCE)**: In some cases, XXE can be used to execute arbitrary code on the server.

### Real-World Examples of XXE Vulnerabilities

#### CVE-2018-11776: Apache Struts XXE Vulnerability

In 2018, a critical XXE vulnerability was discovered in Apache Struts, a popular Java framework. The vulnerability allowed attackers to read arbitrary files on the server and potentially execute commands.

**Example Exploit**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<struts>
    <interceptor-ref name="defaultStack"/>
    <param name="expression">%xxe;</param>
</struts>
```

This exploit would allow an attacker to read the `/etc/passwd` file on the server.

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

### How XXE Works Under the Hood

When an XML parser encounters an external entity, it attempts to resolve the entity by fetching the referenced resource. This process can be exploited by an attacker to read sensitive files or perform other malicious actions.

#### XML Parser Behavior

1. **Entity Declaration**: The attacker declares an external entity using the `SYSTEM` keyword.
2. **Entity Reference**: The attacker references the entity within the XML document.
3. **Entity Resolution**: The XML parser resolves the entity by fetching the referenced resource.

### Common Mistakes and Pitfalls

#### Misconfigured XML Parsers

Many XML parsers are configured to resolve external entities by default. This can lead to XXE vulnerabilities if proper security measures are not in place.

#### Lack of Input Validation

Failing to validate input can allow attackers to inject malicious XML documents that exploit XXE vulnerabilities.

### Detection and Prevention of XXE Vulnerabilities

#### How to Detect XXE Vulnerabilities

1. **Static Analysis Tools**: Use tools like SonarQube, Fortify, or Checkmarx to scan code for potential XXE vulnerabilities.
2. **Dynamic Analysis Tools**: Use tools like Burp Suite or OWASP ZAP to test for XXE vulnerabilities during runtime.

#### How to Prevent XXE Vulnerabilities

1. **Disable External Entity Processing**: Configure XML parsers to disable external entity processing.
2. **Input Validation**: Validate all XML input to ensure it does not contain malicious entities.
3. **Use Secure Libraries**: Use libraries that are known to be secure against XXE vulnerabilities.

### Secure Coding Practices

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

### Configuration Hardening

#### Example of Hardening XML Parser Configuration

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
```

### Hands-On Labs

#### PortSwigger Web Security Academy

PortSwigger Web Security Academy offers a comprehensive course on XXE injection. You can practice exploiting XXE vulnerabilities and learn how to defend against them.

#### OWASP Juice Shop

OWASP Juice Shop is a deliberately insecure web application that includes XXE vulnerabilities. You can use it to practice identifying and exploiting XXE vulnerabilities.

### Conclusion

Understanding XML and XXE injection is crucial for web security professionals. By learning the syntax of XML, recognizing the risks of XXE vulnerabilities, and implementing secure coding practices, you can protect your applications from these types of attacks.

---

---
<!-- nav -->
[[04-Introduction to XML and XML Parsing|Introduction to XML and XML Parsing]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[06-Introduction to XXE Injection|Introduction to XXE Injection]]
