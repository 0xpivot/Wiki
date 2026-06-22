---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## How to Prevent / Defend Against XXE Injection

### Detection

To detect XXE attacks, implement logging and monitoring mechanisms that track XML parsing activities. Look for patterns that indicate the presence of external entities, such as unusual file accesses or network requests.

### Prevention

To prevent XXE attacks, configure XML parsers to disable external entity processing. This can be done by setting the appropriate configuration options in the parser library being used.

#### Secure Configuration Example

```python
import defusedxml.ElementTree as ET

# Disable external entity processing
ET.XMLParser(resolve_entities=False)
```

### Secure Coding Practices

Implement secure coding practices to validate and sanitize all XML input. Use libraries that provide built-in protections against XXE attacks.

#### Vulnerable Code Example

```python
import xml.etree.ElementTree as ET

def process_xml(xml_data):
    root = ET.fromstring(xml_data)
    # Process XML data
```

#### Secure Code Example

```python
import defusedxml.ElementTree as ET

def process_xml(xml_data):
    root = ET.fromstring(xml_data)
    # Process XML data
```

### Hardening Measures

Implement hardening measures to restrict access to sensitive files and systems. Use least privilege principles to limit the permissions of the application and ensure that it cannot access unnecessary resources.

#### File System Permissions Example

```bash
chmod 600 /etc/passwd
chown root:root /etc/passwd
```

### Real-World Lab Exercises

To practice defending against XXE attacks, consider the following real-world lab exercises:

- **PortSwigger Web Security Academy**: Offers interactive labs that cover XXE injection and other web security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including XXE.
- **DVWA (Damn Vulnerable Web Application)**: Includes XXE injection vulnerabilities for hands-on practice.

---
<!-- nav -->
[[16-External Entity Injection (XXE)|External Entity Injection (XXE)]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[18-Identifying Potential XXE Vulnerabilities|Identifying Potential XXE Vulnerabilities]]
