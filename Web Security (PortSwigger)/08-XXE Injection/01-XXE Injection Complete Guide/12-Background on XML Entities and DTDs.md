---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Background on XML Entities and DTDs

Before diving into XXE injection vulnerabilities, it's crucial to understand the basics of XML entities and Document Type Definitions (DTDs).

### What Are XML Entities?

XML entities are placeholders that can be used to represent specific pieces of data within an XML document. They can be thought of as variables that hold certain values. There are two main types of XML entities:

1. **General Entities**: These are the most commonly used entities and can be referenced anywhere in the document body. They start with an ampersand (`&`) and end with a semicolon (`;`). For example, `&lt;` represents the less-than symbol `<`.

2. **Parameter Entities**: These are special entities that can only be referenced within the DTD section of an XML document. They start with a percent sign (`%`) and also end with a semicolon (`;`). For example, `%param;` might represent a specific value that is used within the DTD.

### Document Type Definition (DTD)

A DTD is a set of rules that defines the structure and constraints of an XML document. It specifies the elements, attributes, and entities that are allowed in the document. DTDs can be included within the XML document itself or referenced externally.

Here is an example of a simple DTD:

```xml
<!DOCTYPE note [
    <!ELEMENT note (to,from,heading,body)>
    <!ELEMENT to (#PCDATA)>
    <!ELEMENT from (#PCDATA)>
    <!ELEMENT heading (#PCDATA)>
    <!ELEMENT body (#PCDATA)>
]>
```

In this example, the DTD defines the structure of a `note` element, which consists of four child elements: `to`, `from`, `heading`, and `body`. Each of these child elements contains parsed character data (`#PCDATA`).

### Parameter Entities in DTDs

Parameter entities are used within the DTD to define reusable values or structures. They are particularly useful for defining complex structures that can be reused throughout the DTD.

For example, consider the following DTD with a parameter entity:

```xml
<!DOCTYPE note [
    <!ENTITY % address "to | from">
    <!ELEMENT note (%address;, heading, body)>
    <!ELEMENT to (#PCDATA)>
    <!ELEMENT from (#PCDATA)>
    <!ELEMENT heading (#PCDATA)>
    <!ELEMENT body (#PCDATA)>
]>
```

In this example, the parameter entity `%address;` is defined to represent the choice between `to` and `from` elements. This parameter entity is then used within the definition of the `note` element.

### External Entities

External entities allow an XML document to reference external resources, such as files or URLs. This can be useful for including large chunks of data or for modularizing the XML document.

An external entity is defined using the `SYSTEM` keyword followed by a URI. For example:

```xml
<!DOCTYPE note [
    <!ENTITY ext SYSTEM "http://example.com/data.xml">
]>
```

In this example, the external entity `ext` references the resource at `http://example.com/data.xml`.

### Why External Entities Matter

External entities become problematic when they are used in a way that allows an attacker to control the content of the referenced resource. This can lead to various security issues, including XXE injection vulnerabilities.

---
<!-- nav -->
[[11-Background Theory|Background Theory]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[13-Confirming XXE Vulnerabilities|Confirming XXE Vulnerabilities]]
