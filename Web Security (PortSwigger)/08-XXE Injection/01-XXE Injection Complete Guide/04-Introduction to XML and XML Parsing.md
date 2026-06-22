---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Introduction to XML and XML Parsing

XML (Extensible Markup Language) is a markup language designed to store and transport data. Unlike HTML, which is primarily used for displaying data, XML focuses on the structure and semantics of the data. XML documents consist of elements, attributes, and text content. Each element is defined by a start tag and an end tag, and elements can contain other elements, attributes, and text.

### XML Document Structure

An XML document typically follows a hierarchical structure, with a single root element containing nested child elements. Here is an example of a simple XML document:

```xml
<?xml version="1.0"?>
<bookstore>
    <book>
        <title>Harry Potter</title>
        <author>J.K. Rowling</author>
        <year>1997</year>
    </book>
    <book>
        <title>The Hobbit</title>
        <author>J.R.R. Tolkien</author>
        <year>1937</year>
    </book>
</bookstore>
```

In this example:
- `<?xml version="1.0"?>` is the XML declaration, specifying the version of XML being used.
- `<bookstore>` is the root element.
- `<book>` is a child element of `<bookstore>`.
- `<title>`, `<author>`, and `<year>` are child elements of `<book>`.

### Syntactical Rules for Well-Formed XML Documents

To ensure that an XML document is well-formed, it must adhere to certain syntactical rules:

1. **Start and End Tags**: Every element that has a start tag must have a corresponding end tag. For example:
    ```xml
    <bookstore>
        <!-- Content -->
    </bookstore>
    ```

2. **Case Sensitivity**: XML tags are case-sensitive. Therefore, `<Title>` and `<title>` are considered different tags. For instance:
    ```xml
    <title>Harry Potter</title>
    ```

3. **Tag Closure Order**: XML tags must be closed in the correct order. An inner tag must be closed before its parent tag. For example:
    ```xml
    <book>
        <title>Harry Potter</title>
        <author>J.K. Rowling</author>
        <year>1997</year>
    </book>
    ```

### XML Parsing and Security Risks

XML parsing is the process of reading an XML document and converting it into a structured format that can be processed by a program. However, improper handling of XML parsing can lead to various security vulnerabilities, including XML External Entity (XXE) injection attacks.

---
<!-- nav -->
[[03-Introduction to XML Entities and XXE Injection|Introduction to XML Entities and XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[05-Introduction to XML and XXE Injection|Introduction to XML and XXE Injection]]
