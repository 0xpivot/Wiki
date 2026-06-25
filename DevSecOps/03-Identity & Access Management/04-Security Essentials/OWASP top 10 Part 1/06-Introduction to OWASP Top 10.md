---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Introduction to OWASP Top 10

The Open Web Application Security Project (OWASP) is a non-profit organization dedicated to improving the security of software. One of its most prominent contributions is the OWASP Top 10, a list of the most critical security risks faced by web applications. This list is updated periodically to reflect the evolving landscape of web application security threats. Understanding and addressing these risks is crucial for developers and security professionals involved in the development and maintenance of web applications.

### Why OWASP Top 10 Matters

Web applications are increasingly becoming the primary interface for businesses to interact with their customers. As such, they are also prime targets for cybercriminals. The OWASP Top 10 provides a structured approach to identifying and mitigating the most significant security risks. By adhering to this list, organizations can significantly reduce their exposure to common vulnerabilities and improve the overall security posture of their applications.

### Structure of OWASP Top 10

The OWASP Top 10 is organized into ten categories, each representing a specific type of security risk. These categories are:

1. **Injection**
2. **Broken Authentication**
3. **Sensitive Data Exposure**
4. **XML External Entities (XXE)**
5. **Broken Access Control**
6. **Security Misconfiguration**
7. **Cross-Site Scripting (XSS)**
8. **Insecure Deserialization**
9. **Using Components with Known Vulnerabilities**
10. **Insufficient Logging & Monitoring**

Each category includes detailed descriptions of the vulnerabilities, their potential impacts, and recommendations for mitigation. Let's delve into each category in detail.

### Injection

#### What is Injection?

Injection attacks occur when untrusted data is sent to an interpreter as part of a command or query. The attacker’s hostile data can trick the interpreter into executing unintended commands or accessing unauthorized data. Common types of injection attacks include SQL injection, OS command injection, and LDAP injection.

#### Real-World Example: SQL Injection

SQL injection is one of the most prevalent forms of injection attacks. A classic example is the infamous SQL injection attack against the Heartland Payment Systems in 2008, which resulted in the theft of over 130 million credit card numbers. The attackers exploited a vulnerability in the company's web application, allowing them to inject malicious SQL commands that bypassed authentication mechanisms.

#### How to Prevent / Defend Against Injection Attacks

**Secure Coding Practices:**
- Use parameterized queries or prepared statements.
- Validate and sanitize user input.

```python
# Vulnerable Code
query = "SELECT * FROM users WHERE username = '" + username + "'"

# Secure Code
import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

**Configuration Hardening:**
- Disable unnecessary database features.
- Use least privilege principle for database access.

### Broken Authentication

#### What is Broken Authentication?

Broken authentication occurs when an application does not properly implement authentication mechanisms, allowing attackers to compromise passwords, keys, or session tokens, or to exploit other implementation flaws to assume other users' identities temporarily or permanently.

#### Real-World Example: LinkedIn Password Breach

In 2012, LinkedIn suffered a massive breach where over 6.5 million hashed passwords were stolen. The breach was attributed to weak password storage practices, including the use of unsalted SHA-1 hashes, which made it easier for attackers to crack the passwords.

#### How to Prevent / Defend Against Broken Authentication

**Secure Coding Practices:**
- Use strong hashing algorithms (e.g., bcrypt, scrypt).
- Implement multi-factor authentication (MFA).

```python
# Vulnerable Code
import hashlib
hashed_password = hashlib.sha1(password.encode()).hexdigest()

# Secure Code
import bcrypt
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode(), salt)
```

**Configuration Hardening:**
- Enable and enforce strong password policies.
- Regularly audit and rotate credentials.

### Sensitive Data Exposure

#### What is Sensitive Data Exposure?

Sensitive data exposure occurs when sensitive data is exposed to unauthorized parties due to improper protection mechanisms. This can include personal information, financial data, and authentication credentials.

#### Real-World Example: Equifax Data Breach

In 2017, Equifax suffered a massive data breach that exposed the personal information of over 143 million individuals. The breach was caused by a vulnerability in Apache Struts, which allowed attackers to access sensitive data stored in the company's databases.

#### How to Prevent / Defend Against Sensitive Data Exposure

**Secure Coding Practices:**
- Encrypt sensitive data both at rest and in transit.
- Use strong encryption algorithms (e.g., AES-256).

```plaintext
# Vulnerable Configuration
Server {
    listen 80;
}

# Secure Configuration
Server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;
}
```

**Configuration Hardening:**
- Implement strict access controls.
- Regularly audit and monitor data access logs.

### XML External Entities (XXE)

#### What is XXE?

XML External Entities (XXE) attacks occur when an application parses untrusted XML input without proper validation. This can lead to various security issues, including data exfiltration, denial of service, and remote code execution.

#### Real-World Example: Apache Struts XXE Vulnerability

In 2017, a critical XXE vulnerability was discovered in Apache Struts, affecting versions 2.3.5 to 2.3.31 and 2.5 to 2.5.10. This vulnerability allowed attackers to execute arbitrary commands on the server, leading to several high-profile breaches.

#### How to Prevent / Defend Against XXE Attacks

**Secure Coding Practices:**
- Disable external entity processing in XML parsers.
- Use secure XML parsing libraries.

```xml
<!-- Vulnerable XML -->
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<foo>&xxe;</foo>

<!-- Secure XML -->
<foo>Safe Content</foo>
```

**Configuration Hardening:**
- Configure XML parsers to reject external entities.
- Regularly update and patch XML parsing libraries.

### Broken Access Control

#### What is Broken Access Control?

Broken access control occurs when an application fails to properly restrict access to resources based on user roles and permissions. This can allow unauthorized users to access sensitive data or perform actions they should not be able to.

#### Real-World Example: Capital One Data Breach

In 2019, Capital One suffered a data breach that exposed the personal information of over 100 million customers. The breach was caused by a misconfigured web application firewall (WAF) that allowed an attacker to access sensitive data stored in the company's cloud environment.

#### How to Prevent / Defend Against Broken Access Control

**Secure Coding Practices:**
- Implement role-based access control (RBAC).
- Enforce least privilege principle.

```python
# Vulnerable Code
def get_user_data(user_id):
    return User.objects.get(id=user_id)

# Secure Code
def get_user_data(user_id):
    if user_id == request.user.id:
        return User.objects.get(id=user_id)
    else:
        raise PermissionDenied
```

**Configuration Hardening:**
- Regularly audit and review access control policies.
- Implement strict segregation of duties.

### Security Misconfiguration

#### What is Security Misconfiguration?

Security misconfiguration occurs when an application or its underlying infrastructure is not properly configured to follow security best practices. This can include default settings, open ports, and unnecessary services.

#### Real-World Example: Docker Hub Breach

In 2019, Docker Hub suffered a breach that exposed the credentials of over 190,000 users. The breach was caused by a misconfiguration in the company's cloud environment, which allowed attackers to access sensitive data stored in the company's databases.

#### How to Prevent / Defend Against Security Misconfiguration

**Secure Coding Practices:**
- Follow security best practices for application configuration.
- Use secure defaults for all configurations.

```yaml
# Vulnerable Configuration
server:
  port: 8080

# Secure Configuration
server:
  port: 8443
  ssl:
    enabled: true
    key-store: classpath:keystore.jks
    key-store-password: secret
```

**Configuration Hardening:**
- Regularly audit and review configuration settings.
- Implement strict change management processes.

### Cross-Site Scripting (XSS)

#### What is XSS?

Cross-site scripting (XSS) occurs when an application includes untrusted data in a web page without proper validation or escaping. This can allow attackers to inject malicious scripts that execute in the context of the victim's browser.

#### Real-World Example: Twitter XSS Vulnerability

In 2010, Twitter suffered an XSS vulnerability that allowed attackers to inject malicious scripts into tweets. This led to a widespread attack that affected millions of users.

#### How to Prevent / Defend Against XSS Attacks

**Secure Coding Practices:**
- Sanitize and escape user input.
- Use Content Security Policy (CSP).

```html
<!-- Vulnerable Code -->
<p>User Input: <span>{{ user_input }}</span></p>

<!-- Secure Code -->
<p>User Input: <span>{{ user_input | escape }}</span></p>
```

**Configuration Hardening:**
- Implement CSP to restrict script sources.
- Regularly audit and review input validation practices.

### Insecure Deserialization

#### What is Insecure Deserialization?

Insecure deserialization occurs when an application deserializes untrusted data without proper validation. This can allow attackers to execute arbitrary code or manipulate objects in memory.

#### Real-World Example: Java Deserialization Vulnerability

In 2015, a critical deserialization vulnerability was discovered in Java, affecting versions 6, 7, and 8. This vulnerability allowed attackers to execute arbitrary code on the server, leading to several high-profile breaches.

#### How to Prevent / Defend Against Insecure Deserialization

**Secure Coding Practices:**
- Validate and sanitize serialized data.
- Use secure serialization libraries.

```java
// Vulnerable Code
ObjectInputStream ois = new ObjectInputStream(new FileInputStream("data.ser"));
Object obj = ois.readObject();

// Secure Code
ObjectInputStream ois = new ObjectInputStream(new FileInputStream("data.ser")) {
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        // Custom validation logic
        return super.resolveClass(desc);
    }
};
Object obj = ois.readObject();
```

**Configuration Hardening:**
- Regularly audit and review deserialization practices.
- Implement strict input validation.

### Using Components with Known Vulnerabilities

#### What is Using Components with Known Vulnerabilities?

Using components with known vulnerabilities occurs when an application uses third-party libraries or frameworks that contain known security vulnerabilities. This can allow attackers to exploit these vulnerabilities to gain unauthorized access or execute malicious code.

#### Real-World Example: Log4j Vulnerability

In 2021, a critical vulnerability was discovered in the popular logging framework Log4j, affecting versions 2.0 to 2.14.1. This vulnerability allowed attackers to execute arbitrary code on the server, leading to several high-profile breaches.

#### How to Prevent / Defend Against Using Components with Known Vulnerabilities

**Secure Coding Practices:**
- Regularly update and patch third-party components.
- Use dependency management tools to track component versions.

```json
{
  "dependencies": [
    {
      "name": "log4j",
      "version": "2.15.0"
    }
  ]
}
```

**Configuration Hardening:**
- Implement strict change management processes for component updates.
- Regularly audit and review component usage.

### Insufficient Logging & Monitoring

#### What is Insufficient Logging & Monitoring?

Insufficient logging and monitoring occurs when an application does not properly log and monitor security events. This can make it difficult to detect and respond to security incidents in a timely manner.

#### Real-World Example: Yahoo Data Breach

In 2013, Yahoo suffered a massive data breach that exposed the personal information of over 3 billion users. The breach was initially detected due to insufficient logging and monitoring, which delayed the company's response to the incident.

#### How to Prevent / Defend Against Insufficient Logging & Monitoring

**Secure Coding Practices:**
- Implement comprehensive logging and monitoring.
- Use centralized logging and monitoring tools.

```bash
# Vulnerable Configuration
access_log /var/log/nginx/access.log;

# Secure Configuration
access_log /var/log/nginx/access.log main;
error_log /var/log/nginx/error.log warn;
```

**Configuration Hardening:**
- Regularly audit and review logging and monitoring practices.
- Implement alerting and incident response processes.

### Conclusion

Understanding and addressing the OWASP Top 10 security risks is essential for developing and maintaining secure web applications. By following the best practices outlined in this chapter, organizations can significantly reduce their exposure to common vulnerabilities and improve their overall security posture. Regular audits, updates, and reviews are crucial to staying ahead of emerging threats and ensuring the continued security of web applications.

### Practice Labs

For hands-on experience with OWASP Top 10 vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs covering a wide range of web security topics, including the OWASP Top 10.
- **OWASP Juice Shop**: An intentionally insecure web application designed to teach web security concepts.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide practical experience in identifying and mitigating the OWASP Top 10 vulnerabilities, helping to reinforce the theoretical knowledge gained from this chapter.

---
<!-- nav -->
[[05-Introduction to OWASP Top 10 Part 1|Introduction to OWASP Top 10 Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 1/00-Overview|Overview]] | [[07-Introduction to Security Essentials|Introduction to Security Essentials]]
