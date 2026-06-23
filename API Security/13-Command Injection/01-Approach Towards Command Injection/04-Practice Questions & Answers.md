---
course: API Security
topic: Command Injection
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is command injection and how does it occur in an application?**

Command injection occurs when an application takes input from an untrusted source and uses it in a system command without proper validation or sanitization. The input is then executed as part of a command, potentially giving an attacker unauthorized access or control over the system. For example, if an application constructs a command string using user input and executes it, an attacker could inject malicious commands to manipulate the execution flow.

**Q2. How can an attacker exploit a command injection vulnerability in an API endpoint?**

An attacker can exploit a command injection vulnerability by injecting malicious commands through an API endpoint. For instance, if an API endpoint accepts a parameter that is used in a system command, the attacker can insert a command that alters the intended behavior. An example payload might be `email=attacker@example.com; ls /etc` which, if not properly sanitized, could execute the `ls /etc` command on the server, revealing sensitive files.

**Q3. Explain the difference between explicit and implicit command injection.**

Explicit command injection involves the attacker directly controlling the command that is executed. For example, if an application constructs a command string using user input, an attacker can inject a new command like `command="echo 'hello'; rm -rf /"`.

Implicit command injection involves the attacker changing the environment in which the command executes, thereby altering its meaning. For example, setting environment variables or manipulating the current directory can change how a command behaves. An example might involve setting the `PATH` variable to point to a malicious script.

**Q4. How can you detect and test for command injection vulnerabilities in an API?**

To detect and test for command injection vulnerabilities in an API, you can use tools like Burp Suite or Postman to send payloads that attempt to execute additional commands. For example, you can test parameters that are used in shell commands by appending `; ls /etc` or `&& whoami`. If the API returns unexpected results or errors, it may indicate a vulnerability.

**Q5. Provide a recent real-world example of a command injection attack and explain how it was exploited.**

A notable example is the 2017 Equifax breach, where attackers exploited a vulnerability in Apache Struts, leading to a command injection attack. The vulnerability allowed attackers to inject malicious commands into the application, gaining unauthorized access to sensitive data. The attackers used a crafted HTTP request to execute arbitrary commands on the server, demonstrating the severe impact of command injection vulnerabilities.

**Q6. How can developers prevent command injection vulnerabilities in their APIs?**

Developers can prevent command injection vulnerabilities by ensuring that user input is properly validated and sanitized before being used in any system command. Using safe libraries and functions that avoid shell command execution is recommended. Additionally, employing security mechanisms such as input validation, parameterized queries, and least privilege principles can significantly reduce the risk of command injection attacks.

**Q7. Describe the process of exploiting a command injection vulnerability using the `cat` command to read sensitive files.**

To exploit a command injection vulnerability using the `cat` command, an attacker would inject a command that reads sensitive files. For example, if an API endpoint uses a parameter in a shell command, the attacker could inject `cat /etc/passwd` to read the contents of the `/etc/passwd` file. The payload might look like `email=attacker@example.com; cat /etc/passwd`, which, if not properly sanitized, could execute the `cat /etc/passwd` command and return the file contents to the attacker.

---
<!-- nav -->
[[03-Command Injection in APIs|Command Injection in APIs]] | [[API Security/13-Command Injection/01-Approach Towards Command Injection/00-Overview|Overview]]
