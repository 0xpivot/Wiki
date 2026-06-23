---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Understanding XML and Its Role in Web Security

### Introduction to XML

XML, or Extensible Markup Language, is a markup language designed for storing, transmitting, and reconstructing arbitrary data. It is widely used in various applications, particularly in web services and data exchange between different systems. XML is similar to HTML in structure but serves a different purpose. While HTML is primarily focused on data representation, XML is geared towards data transportation and storage.

#### Key Characteristics of XML

- **Extensibility**: XML is extensible, meaning that applications can work correctly even if new data is added or existing data is removed. This flexibility allows developers to create their own self-describing tags tailored to specific applications.
- **Markup Language**: Like HTML, XML is a markup language that is human-readable and uses tags to define elements within a document. However, unlike HTML, which relies heavily on predefined tags, XML allows for the creation of custom tags.

### Example of an XML Document

To better understand how XML works, consider the following example of an XML document used for managing a bookstore application:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book id="1">
        <title>Effective Java</title>
        <author>Joshua Bloch</author>
        <year>2008</year>
        <price>39.99</price>
    </book>
    <book id="2">
        <title>Clean Code</title>
        <author>Robert C. Martin</author>
        <year>2008</year>
        <price>44.99</price>
    </book>
</bookstore>
```

In this example, the first line is the XML declaration, which provides essential information for parsing the document. The declaration includes the version of the XML standard (`version="1.0"`) and the character encoding used (`encoding="UTF-8"`).

### XML Declaration

The XML declaration is optional but highly recommended, especially when dealing with international characters or specific encoding requirements. Here’s a breakdown of the XML declaration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
```

- **Version**: Specifies the version of the XML standard being used. Common versions include `1.0` and `1.1`.
- **Encoding**: Defines the character encoding used in the document. Common encodings include `UTF-8`, `ISO-8859-1`, etc.

### XML Elements and Attributes

XML documents consist of elements and attributes. Elements are defined using tags, and attributes provide additional information about the element.

- **Elements**: Defined using opening and closing tags. For example, `<book>` and `</book>`.
- **Attributes**: Provide metadata about an element. For example, `<book id="1">`.

### Example of XML Parsing

Consider the following example of an XML document being parsed by a web service:

```http
POST /api/bookstore HTTP/1.1
Host: example.com
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book id="1">
        <title>Effective Java</title>
        <author>Joshua Bloch</author>
        <year>2008</year>
        <price>39.99</price>
    </book>
</bookstore>
```

The server receives this XML document and processes it accordingly. The response might look like this:

```http
HTTP/1.1 200 OK
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<response>
    <status>success</status>
    <message>Book successfully added to the bookstore.</message>
</response>
```

### XML Injection Vulnerabilities

XML injection, also known as XXE (XML External Entity) injection, is a type of security vulnerability that occurs when an attacker can inject malicious XML content into an application. This can lead to unauthorized access, data leakage, and other security issues.

#### Real-World Examples of XXE Injection

One notable example of XXE injection is the CVE-2018-11776, which affected the Apache Struts framework. This vulnerability allowed attackers to execute arbitrary commands on the server by injecting malicious XML content.

Another example is the CVE-2019-11510, which affected the Atlassian Confluence application. This vulnerability allowed attackers to read sensitive files on the server by exploiting XXE injection.

### How XXE Injection Works

XXE injection exploits the way XML parsers handle external entities. An external entity is a reference to an external resource, such as a file or a URL. By injecting malicious XML content that references these external entities, an attacker can manipulate the behavior of the XML parser.

#### Example of XXE Injection

Consider the following XML document that includes an external entity:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<bookstore>
    <book id="1">
        <title>&xxe;</title>
        <author>Joshua Bloch</author>
        <year>2008</year>
        <price>39.99</price>
    </book>
</bookstore>
```

When this XML document is parsed, the `&xxe;` entity will be replaced with the contents of `/etc/passwd`, potentially exposing sensitive information.

### How to Prevent / Defend Against XXE Injection

#### Detection

To detect XXE injection vulnerabilities, you can use tools like Burp Suite, OWASP ZAP, or static analysis tools like SonarQube. These tools can help identify potential XXE injection points in your code.

#### Prevention

To prevent XXE injection, follow these best practices:

1. **Disable External Entities**: Configure your XML parser to disable external entities. This can be done by setting the `allowExternalEntities` property to `false`.

2. **Validate Input**: Validate all user input to ensure it does not contain malicious XML content. Use regular expressions or XML validation libraries to enforce strict input rules.

3. **Use Secure Libraries**: Use secure XML parsing libraries that are designed to handle XXE injection vulnerabilities. Libraries like `defusedxml` in Python provide safer alternatives to standard XML parsers.

4. **Secure Configuration**: Ensure that your XML parser is configured securely. Disable features like DTD processing and external entity resolution unless absolutely necessary.

#### Secure Coding Fixes

Here is an example of how to secure an XML parser in Python using the `defusedxml` library:

**Vulnerable Code:**

```python
import xml.etree.ElementTree as ET

xml_data = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<bookstore>
    <book id="1">
        <title>&xxe;</title>
        <author>Joshua Bloch</author>
        <year>2008</year>
        <price>39.99</price>
    </book>
</bookstore>
"""

tree = ET.fromstring(xml_data)
print(tree.find('book/title').text)
```

**Secure Code:**

```python
from defusedxml import ElementTree as ET

xml_data = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<bookstore>
    <book id="1">
        <title>&xxe;</title>
        <author>Joshua Bloch</author>
        <year>2008</year>
        <price>39.99</price>
    </book>
</bookstore>
"""

tree = ET.fromstring(xml_data)
print(tree.find('book/title').text)
```

### Conclusion

Understanding XML and its role in web security is crucial for developing secure applications. By recognizing the potential risks associated with XML injection vulnerabilities and implementing proper defenses, you can protect your applications from attacks. Always validate user input, configure your XML parsers securely, and use secure libraries to mitigate the risk of XXE injection.

### Practice Labs

For hands-on practice with XXE injection and related web security topics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on XML injection and other web security vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including XXE injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including XXE injection.

These labs provide practical experience in identifying and mitigating XXE injection vulnerabilities, helping you to become proficient in web security.

---
<!-- nav -->
[[21-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[23-XML External Entity (XXE) Injection|XML External Entity (XXE) Injection]]
