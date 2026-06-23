---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## OS Command Injection: Blind Injection with Output Redirection

### Introduction to OS Command Injection

OS Command Injection is a type of vulnerability that occurs when an application executes operating system commands using input provided by an attacker. This can lead to unauthorized access to sensitive information, execution of arbitrary commands, and even full system compromise. The vulnerability arises due to improper validation or sanitization of user input, allowing attackers to inject malicious commands.

### Understanding Blind OS Command Injection

Blind OS Command Injection is a variant where the attacker cannot directly observe the output of the injected command. Instead, the attacker must infer the success of the command through indirect means, such as checking for the existence of a file or observing changes in the application's behavior.

#### Example Scenario

Consider a web application that allows users to upload images. The application processes the uploaded image by executing a series of shell commands. An attacker can exploit this by injecting a command that writes the output of a sensitive command (like `whoami`) to a file in a writable directory.

### Steps to Exploit Blind OS Command Injection

1. **Identify Writable Directory**: Find a directory where the application has write permissions.
2. **Inject Command**: Inject a command that redirects the output to a file in the writable directory.
3. **Verify Output**: Check if the file was successfully written and retrieve its contents.

#### Detailed Walkthrough

Let's walk through the process step-by-step using the example from the lecture.

1. **Identify Writable Directory**:
    - In the lecture, the writable directory identified is `/var/www/images`.

2. **Inject Command**:
    - The goal is to execute the `whoami` command and redirect its output to a file in the writable directory.
    - The command to inject would look like this:
      ```bash
      whoami > /var/www/images/output.txt
      ```

3. **URL Encoding**:
    - To ensure the command is properly interpreted by the application, it needs to be URL-encoded.
    - The encoded command would be:
      ```bash
      %60whoami%20%3E%20/var/www/images/output.txt%60
      ```

4. **Send Request**:
    - Use a tool like Burp Suite Repeater to send the request.
    - The full HTTP request would look like this:

```http
POST /upload.php HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 30

image=%60whoami%20%3E%20/var/www/images/output.txt%60
```

5. **Check for File Existence**:
    - After sending the request, check if the file `output.txt` exists in the `/var/www/images` directory.
    - The HTTP request to check for the file would be:

```http
GET /images/output.txt HTTP/1.1
Host: vulnerable-app.com
```

6. **Retrieve File Content**:
    - If the file exists, retrieve its content to see the output of the `whoami` command.

### Real-World Examples and Recent Breaches

#### CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) is a prime example of how OS command injection can be exploited. Attackers could inject malicious JNDI lookup strings into logs, leading to remote code execution. While this specific vulnerability is related to Java logging, the principle of injecting commands and redirecting output applies similarly.

#### Example Code Snippet

Here’s a simplified example of how an application might be vulnerable to OS command injection:

```python
import subprocess

def process_image(image_path):
    # Vulnerable code
    command = f"convert {image_path} -resize 50% /tmp/resized.jpg"
    subprocess.run(command, shell=True)
```

In this example, the `image_path` parameter is directly used in the shell command, making it susceptible to injection attacks.

### How to Prevent / Defend Against OS Command Injection

#### Secure Coding Practices

1. **Avoid Shell Commands**: Avoid using shell commands whenever possible. Use built-in functions or libraries that do not rely on shell execution.
2. **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious characters.
3. **Use Safe Libraries**: Use libraries that provide safe methods for executing commands, such as `subprocess.run()` without `shell=True`.

#### Secure Code Example

Here’s how the previous example can be made secure:

```python
import subprocess

def process_image(image_path):
    # Secure code
    command = ["convert", image_path, "-resize", "50%", "/tmp/resized.jpg"]
    subprocess.run(command, check=True)
```

In this secure version, the command is passed as a list of arguments, avoiding the use of the shell.

#### Detection and Prevention Tools

1. **Static Analysis Tools**: Use tools like SonarQube, Fortify, or Veracode to scan code for potential vulnerabilities.
2. **Dynamic Analysis Tools**: Use tools like Burp Suite, OWASP ZAP, or Nessus to test applications for runtime vulnerabilities.
3. **Web Application Firewalls (WAF)**: Implement WAFs to filter out malicious requests.

### Hands-On Labs

For practical experience with OS Command Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including OS command injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

OS Command Injection is a serious vulnerability that can lead to significant security breaches. By understanding the principles behind this attack vector and implementing robust defensive measures, developers can protect their applications from such threats. Always validate and sanitize user inputs, avoid using shell commands unnecessarily, and use secure coding practices to mitigate the risk of OS command injection.

---
<!-- nav -->
[[06-Lab Setup Blind OS Command Injection with Output Redirection|Lab Setup Blind OS Command Injection with Output Redirection]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/00-Overview|Overview]] | [[08-OS Command Injection with Output Redirection|OS Command Injection with Output Redirection]]
