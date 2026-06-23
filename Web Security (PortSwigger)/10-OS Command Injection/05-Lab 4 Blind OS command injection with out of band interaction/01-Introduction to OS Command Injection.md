---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Introduction to OS Command Injection

### What is OS Command Injection?

OS Command Injection, also known as Shell Injection, is a type of security vulnerability that occurs when an application constructs a command string using untrusted input from a user or other sources. If the input is not properly sanitized, an attacker can inject malicious commands that will be executed by the operating system. This can lead to unauthorized access, data theft, or even complete system compromise.

### Why Does OS Command Injection Matter?

Command injection vulnerabilities are particularly dangerous because they allow attackers to execute arbitrary commands on the server. This can result in severe consequences such as:

- **Data Theft**: Attackers can read sensitive files and exfiltrate data.
- **System Compromise**: Attackers can gain full control over the server and perform actions like installing malware, creating new accounts, or modifying system configurations.
- **Denial of Service (DoS)**: Attackers can cause the server to crash or become unresponsive.

### How Does OS Command Injection Work Under the Hood?

When an application constructs a command string using user input, it typically uses functions like `exec`, `system`, or `shell_exec` in languages like C, Python, or PHP. These functions take a string as input and pass it to the operating system for execution. If the input is not properly validated and sanitized, an attacker can inject additional commands or modify existing ones.

For example, consider a PHP script that takes a user input and passes it to the `system` function:

```php
<?php
$user_input = $_GET['cmd'];
system("echo $user_input");
?>
```

If an attacker provides the input `; rm -rf /`, the resulting command would be:

```sh
echo ; rm -rf /
```

This would execute two separate commands: `echo` and `rm -rf /`. The latter would attempt to delete all files on the system.

### Real-World Example: CVE-2021-3185

In 2021, a critical vulnerability was discovered in the Jenkins Continuous Integration server (CVE-2021-3185). The vulnerability allowed attackers to execute arbitrary commands on the server through the Jenkins CLI. This could lead to complete system compromise.

### Out-of-Band Interaction

Out-of-band interaction refers to a technique where an attacker triggers an action that results in communication with an external domain controlled by the attacker. This is often used in scenarios where direct feedback from the server is not possible, such as in blind command injection attacks.

### Lab Setup

To understand and practice OS command injection, we will use the Web Security Academy provided by PortSwigger. The specific lab we will focus on is titled "Blind OS Command Injection with Out-of-Band Interaction."

### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL: [PortSwigger Web Security Academy](https://portswigger.net/web-security)
2. Click on the "Sign Up" button to create an account.
3. Once logged in, navigate to the "Academy."
4. Select the "Learning Path" and then choose "Command Injection."
5. Finally, select "Lab Number Four" titled "Blind OS Command Injection with Out-of-Band Interaction."

### Lab Overview

The lab contains a blind OS command injection vulnerability in the feedback function. The application executes a shell command containing the user-supplied details. The command is executed asynchronously and has no effect on the application's response. Therefore, traditional methods of exploiting command injection, such as redirecting output, do not work. Instead, you must trigger out-of-band interactions with an external domain that you control.

### Exploiting the Vulnerability

To exploit the vulnerability, you need to trigger an out-of-band interaction, such as a DNS lookup, to an external domain that you control. In this case, you will use a service like Verbal Collaborator to capture the interaction.

#### Step-by-Step Exploitation

1. **Identify the Vulnerable Parameter**:
   - The vulnerable parameter is likely part of a form or URL query string. For example, it might be `feedback?cmd=...`.

2. **Inject the Malicious Command**:
   - You need to inject a command that will trigger a DNS lookup to your controlled domain. For instance, you can use a command like `ping` or `nslookup`.

3. **Trigger the Command**:
   - Submit the form or make an HTTP request with the injected command.

4. **Monitor the External Domain**:
   - Use Verbal Collaborator to monitor for incoming DNS requests.

#### Example Code

Here is an example of how you might construct the HTTP request to exploit the vulnerability:

```http
POST /feedback HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded

cmd=ping%20X.Y.Z.W
```

Where `X.Y.Z.W` is the IP address of your controlled domain.

### Monitoring the Interaction

Once you have triggered the command, you should monitor your controlled domain for incoming requests. Verbal Collaborator will log any DNS lookups or other interactions initiated by the vulnerable application.

### Detection and Prevention

#### How to Detect OS Command Injection

1. **Static Analysis**:
   - Use tools like SonarQube, Fortify, or Checkmarx to scan your codebase for potential command injection vulnerabilities.
   
2. **Dynamic Analysis**:
   - Use automated penetration testing tools like Burp Suite, ZAP, or OWASP Dependency-Check to test your application for runtime vulnerabilities.

3. **Logging and Monitoring**:
   - Implement logging and monitoring to detect unusual patterns of behavior that may indicate an attempted command injection attack.

#### How to Prevent OS Command Injection

1. **Input Validation**:
   - Validate and sanitize all user inputs to ensure they do not contain malicious characters or commands.

2. **Use Safe APIs**:
   - Use safe APIs that do not execute shell commands. For example, in Python, use `subprocess.run` instead of `os.system`.

3. **Least Privilege Principle**:
   - Run the application with the least privileges necessary to minimize the damage in case of a successful attack.

4. **Secure Coding Practices**:
   - Follow secure coding practices such as those outlined in the OWASP Top Ten and the CWE/SANS Top 25.

#### Secure Code Example

Here is an example of how to securely handle user input in Python:

```python
import subprocess

def run_safe_command(user_input):
    # Sanitize user input
    sanitized_input = user_input.strip()
    
    # Use subprocess.run to safely execute the command
    try:
        result = subprocess.run(['echo', sanitized_input], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr.decode()}")

# Example usage
run_safe_command("user supplied input")
```

### Common Pitfalls

1. **Assuming Input is Trusted**:
   - Always assume user input is untrusted and potentially malicious.

2. **Ignoring Asynchronous Execution**:
   - Be aware of asynchronous execution and ensure that all commands are properly monitored and logged.

3. **Overlooking Out-of-Band Interactions**:
   - Recognize that out-of-band interactions can be used to bypass traditional feedback mechanisms.

### Conclusion

Understanding and preventing OS command injection is crucial for maintaining the security of web applications. By following secure coding practices, validating user input, and using safe APIs, you can significantly reduce the risk of such vulnerabilities. Regularly testing and monitoring your applications can help detect and mitigate potential threats.

### Practice Labs

For hands-on experience with OS command injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs specifically designed to teach and practice web security concepts, including command injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and practicing web security techniques.

By engaging with these labs, you can gain practical experience and deepen your understanding of OS command injection vulnerabilities and their mitigation strategies.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/05-Lab 4 Blind OS command injection with out of band interaction/00-Overview|Overview]] | [[02-Blind OS Command Injection|Blind OS Command Injection]]
