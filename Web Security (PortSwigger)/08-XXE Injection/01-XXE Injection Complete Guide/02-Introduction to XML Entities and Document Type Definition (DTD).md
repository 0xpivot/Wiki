---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Introduction to XML Entities and Document Type Definition (DTD)

### What are XML Entities?

XML entities are placeholders within an XML document that represent specific values or pieces of data. They are defined in a section of the XML document known as the Document Type Definition (DTD). Entities allow for the reuse of commonly used strings or values throughout the document, making the XML more manageable and maintainable.

### Document Type Definition (DTD)

The Document Type Definition (DTD) is a set of rules that define the structure and content of an XML document. It specifies the elements, attributes, and entities that can appear in the document. The DTD can be embedded within the XML document itself or referenced externally.

#### Example of a Simple Entity

Consider the following XML document:

```xml
<!DOCTYPE root [
    <!ENTITY name "Peter Kim">
]>
<root>
    <person>&name;</person>
</root>
```

In this example:
- `<!DOCTYPE root>` defines the root element of the document.
- `<!ENTITY name "Peter Kim">` declares an entity named `name` with the value `Peter Kim`.
- `&name;` is an entity reference that will be replaced by the value `Peter Kim`.

### Types of XML Entities

There are several types of XML entities, but the most important ones for understanding XXE injection vulnerabilities are:

1. **Internal Entities**
2. **External Entities**
3. **Parameter Entities**

#### Internal Entities

Internal entities are defined within the DTD and are referenced within the XML document. They are declared using the `<!ENTITY>` declaration.

##### Example of an Internal Entity

```xml
<!DOCTYPE root [
    <!ENTITY name "Peter Kim">
]>
<root>
    <person>&name;</person>
</root>
```

In this example, the entity `name` is defined internally and is referenced within the `<person>` element.

#### External Entities

External entities are defined in an external resource, such as another XML file or a URL. They are declared using the `SYSTEM` keyword followed by the location of the external resource.

##### Example of an External Entity

```xml
<!DOCTYPE root [
    <!ENTITY ext SYSTEM "http://example.com/data.xml">
]>
<root>
    <data>&ext;</data>
</root>
```

In this example, the entity `ext` is defined to point to an external resource located at `http://example.com/data.xml`.

#### Parameter Entities

Parameter entities are used within the DTD itself and are referenced using `%`. They are declared using the `%` symbol followed by the entity name.

##### Example of a Parameter Entity

```xml
<!DOCTYPE root [
    <!ENTITY % param "Peter Kim">
    <!ELEMENT person (#PCDATA)>
    <!ATTLIST person name %param;>
]>
<root>
    <person name="Peter Kim"></person>
</root>
```

In this example, the parameter entity `param` is defined and used within the attribute list declaration.

### Predefined Entities

Predefined entities are special entities that are built into XML and are used to represent characters that have special meanings in XML, such as `<`, `>`, `&`, `'`, and `"`. These entities are used to avoid conflicts with the XML parser.

##### Example of Predefined Entities

```xml
<!DOCTYPE root [
    <!ENTITY lt "&#60;">
    <!ENTITY gt "&#62;">
    <!ENTITY amp "&#38;">
    <!ENTITY apos "&#39;">
    <!ENTITY quot "&#34;">
]>
<root>
    <text>&lt; &gt; &amp; &apos; &quot;</text>
</root>
```

In this example, the predefined entities are used to represent special characters within the XML document.

### Why Use XML Entities?

Using XML entities can make XML documents more readable and maintainable. By defining commonly used values as entities, you can avoid redundancy and make changes easier to manage. Additionally, external entities can be used to include data from other sources, which can be useful for dynamic content generation.

### How XML Entities Work Under the Hood

When an XML parser encounters an entity reference, it replaces the reference with the corresponding value defined in the DTD. This process is transparent to the user, but it is crucial for the proper functioning of the XML document.

### Common Mistakes with XML Entities

One common mistake is not properly escaping special characters within entity values. This can lead to parsing errors or unexpected behavior. Another mistake is not validating the input for external entities, which can lead to security vulnerabilities like XXE injection.

### Real-World Examples of XML Entities

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A vulnerability in the Apache Struts framework allowed attackers to exploit XXE injection through the `Content-Type` header. This vulnerability was exploited in the wild, leading to unauthorized access and data exfiltration.
- **CVE-2020-14882**: A vulnerability in the Jenkins Continuous Integration server allowed attackers to exploit XXE injection through the `Jenkins.instance` object. This vulnerability was exploited to gain remote code execution capabilities.

### How to Prevent / Defend Against XXE Injection

#### Detection

To detect XXE injection vulnerabilities, you can use static analysis tools like SonarQube, Fortify, or Veracode. These tools can scan your codebase for potential vulnerabilities and provide recommendations for mitigation.

#### Prevention

To prevent XXE injection, you should:

1. **Disable External Entity Loading**: Ensure that your XML parser does not load external entities. This can be done by configuring the parser to ignore external entities or by setting the appropriate flags.

2. **Validate Input**: Validate all input data to ensure that it does not contain malicious content. Use regular expressions or other validation techniques to filter out invalid input.

3. **Use Secure Coding Practices**: Follow secure coding practices to avoid introducing vulnerabilities. Use libraries and frameworks that are known to be secure and up-to-date.

4. **Configure XML Parser Settings**: Configure your XML parser to disable features that are not needed, such as DTD loading or entity resolution. This can help prevent attacks that rely on these features.

#### Secure Code Fix

Here is an example of how to fix a vulnerable XML parser configuration:

**Vulnerable Code**

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new File("input.xml"));
```

**Fixed Code**

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new File("input.xml"));
```

In the fixed code, the `setFeature` method is used to disable the loading of DTDs and external entities, which helps prevent XXE injection attacks.

### Practice Labs

For hands-on practice with XXE injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on XXE injection, including practical exercises and challenges.
- **OWASP Juice Shop**: A deliberately insecure web application that includes XXE injection vulnerabilities for educational purposes.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that includes various security vulnerabilities, including XXE injection.

These labs provide a safe environment to practice and learn about XXE injection vulnerabilities and how to defend against them.

### Conclusion

Understanding XML entities and their role in XXE injection vulnerabilities is crucial for web security professionals. By learning about the different types of entities, how they work, and how to prevent attacks, you can ensure the security of your applications and protect against potential threats.

---
<!-- nav -->
[[01-Comprehensive Guide to XXE Injection|Comprehensive Guide to XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[03-Introduction to XML Entities and XXE Injection|Introduction to XML Entities and XXE Injection]]
