---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Introduction to XML Entities and XXE Injection

XML (Extensible Markup Language) is a markup language designed to store and transport data. It uses tags to define elements, attributes, and values. One of the key features of XML is the ability to handle special characters that might otherwise interfere with the parsing process. To address this, XML introduces the concept of **entity references** and **XML entities**.

### Entity References

Entity references are placeholders for characters that are not allowed within the content of an XML element. These characters include `<`, `>`, `&`, `'`, and `"`. For instance, the less-than sign (`<`) is represented as `&lt;`, the greater-than sign (`>`) as `&gt;`, the ampersand (`&`) as `&amp;`, the single quote (`'`) as `&apos;`, and the double quote (`"`) as `&quot;`.

#### Example of Entity References

Consider the following XML snippet:

```xml
<person>
    <name>&apos;John Doe&apos;</name>
</person>
```

In this example, the single quotes around "John Doe" are replaced with `&apos;` to ensure proper parsing by the XML parser.

### XML Entities

XML entities are a way of representing an item of data within an XML document. They can be thought of as variables in a programming language. An entity is assigned a value, and this value can be referenced multiple times throughout the document.

There are two main types of XML entities:
1. **Predefined entities**: These are built into the XML specification and do not require explicit definition.
2. **Custom entities**: These are defined by the user within the XML document.

#### Predefined Entities

The predefined entities include:
- `&amp;` for `&`
- `&lt;` for `<`
- `&gt;` for `>`
- `&apos;` for `'`
- `&quot;` for `"`

These entities are already defined in the XML specification and can be used directly in the document.

#### Custom Entities

Custom entities allow users to define their own entities. This is done using the `<!ENTITY>` declaration within the DTD (Document Type Definition).

##### Example of Custom Entities

Consider the following XML document with a custom entity:

```xml
<!DOCTYPE person [
    <!ENTITY greeting "Hello, World!">
]>
<person>
    <message>&greeting;</message>
</person>
```

In this example, the custom entity `&greeting;` is defined to represent the string "Hello, World!". This entity is then used within the `<message>` element.

### XML External Entities (XXE)

XML External Entities (XXE) is a type of attack that exploits the way XML processors handle external entities. In an XXE attack, an attacker can inject malicious content into an XML document, potentially leading to information disclosure, denial of service, or other vulnerabilities.

#### How XXE Works

An XXE attack typically involves the following steps:
1. **Injection of Malicious Content**: The attacker injects a malicious XML document into the application.
2. **Processing by XML Parser**: The XML parser processes the document, including any external entities.
3. **Exploitation**: Depending on the context, the attacker can exploit the parsed content to achieve various goals.

##### Example of XXE Attack

Consider the following XML document with an external entity:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

In this example, the external entity `&xxe;` is defined to read the contents of the `/etc/passwd` file. When this XML document is processed by an XML parser, it will attempt to read the contents of the specified file and include them in the document.

### Real-World Examples of XXE Attacks

XXE attacks have been exploited in various real-world scenarios. Here are a few notable examples:

#### CVE-2019-14546

This vulnerability affected the Apache Struts framework. An attacker could exploit this vulnerability by injecting a malicious XML document containing an external entity, leading to remote code execution.

#### CVE-2018-11776

This vulnerability affected the Atlassian Confluence application. An attacker could exploit this vulnerability by injecting a malicious XML document containing an external entity, leading to information disclosure.

### How to Prevent / Defend Against XXE Attacks

To prevent XXE attacks, it is crucial to properly configure and validate XML parsers. Here are some best practices:

#### Disable External Entity Processing

Most modern XML parsers provide options to disable external entity processing. This can be achieved by setting appropriate configuration parameters.

##### Example Configuration for Java's `DocumentBuilderFactory`

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
```

#### Validate Input Data

Always validate input data to ensure it does not contain malicious content. This can be achieved using regular expressions or other validation techniques.

##### Example Validation Using Regular Expressions

```java
public boolean isValidXml(String xml) {
    // Regular expression to match XML content
    String regex = "<\\?xml.*\\?>.*";
    return xml.matches(regex);
}
```

#### Use Secure Libraries

Use libraries that are known to be secure and regularly updated. Libraries such as `Xerces` and `JDOM` provide robust security features.

### Conclusion

Understanding XML entities and XXE injection is crucial for securing applications that process XML documents. By properly configuring XML parsers and validating input data, developers can mitigate the risks associated with XXE attacks.

### Practice Labs

For hands-on practice with XXE injection, consider the following resources:
- **PortSwigger Web Security Academy**: Offers interactive labs on XXE injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including XXE.

By leveraging these resources, you can gain practical experience in identifying and defending against XXE attacks.

---

This expanded section covers the fundamental concepts of XML entities and XXE injection, providing detailed explanations, real-world examples, and comprehensive guidance on how to prevent and defend against such attacks.

---
<!-- nav -->
[[02-Introduction to XML Entities and Document Type Definition (DTD)|Introduction to XML Entities and Document Type Definition (DTD)]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[04-Introduction to XML and XML Parsing|Introduction to XML and XML Parsing]]
