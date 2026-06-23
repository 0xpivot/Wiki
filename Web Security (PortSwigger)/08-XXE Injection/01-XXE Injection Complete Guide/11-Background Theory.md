---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Background Theory

### XML Processing and External Entities

XML documents are processed by parsers that interpret the structure and content of the document. External entities are a feature of XML that allows the inclusion of external resources within the document. This can be useful for referencing large datasets or other resources, but it also introduces security risks if not properly controlled.

### XML DTD and Entity Definitions

The Document Type Definition (DTD) is used to define the structure and rules of an XML document. Within the DTD, external entities can be defined using the `SYSTEM` keyword, which specifies the location of the external resource.

#### Example of XML DTD with External Entities

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://example.com/resource">
]>
<root>&xxe;</root>
```

In this example, the `<!ENTITY xxe SYSTEM "http://example.com/resource">` directive defines an external entity named `xxe` that references a remote resource. When the XML parser processes this document, it will attempt to fetch the content from `http://example.com/resource`.

### XML Parsing Modes

XML parsers can operate in different modes, such as permissive mode and strict mode. Permissive mode allows the parser to process external entities, while strict mode disables this feature. Disabling external entity processing is a key defense against XXE vulnerabilities.

---
<!-- nav -->
[[10-Advanced Topics in XXE Injection|Advanced Topics in XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[12-Background on XML Entities and DTDs|Background on XML Entities and DTDs]]
