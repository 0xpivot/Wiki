---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Introduction to OS Command Injection

### What is OS Command Injection?

OS Command Injection is a type of security vulnerability that occurs when an application constructs a command string using untrusted input from a user. If the input is not properly sanitized, an attacker can inject malicious commands that will be executed by the operating system. This can lead to unauthorized access, data theft, or even complete control over the server.

### Why Does OS Command Injection Matter?

Command injection vulnerabilities can have severe consequences. An attacker can execute arbitrary commands on the server, potentially leading to:

- **Data Theft**: Accessing sensitive files and databases.
- **Server Control**: Taking control of the server and executing arbitrary commands.
- **Denial of Service**: Overloading the server with resource-intensive commands.

### How Does OS Command Injection Work?

The core mechanism of OS Command Injection involves the execution of shell commands. When an application takes user input and uses it to construct a shell command, it can be exploited if the input is not properly validated or sanitized. For example, consider a simple PHP script that executes a shell command based on user input:

```php
<?php
$cmd = $_GET['cmd'];
exec($cmd);
?>
```

If an attacker inputs `whoami; rm -rf /`, the `exec` function will execute both commands, first displaying the current user and then attempting to delete all files on the system.

### Real-World Example: CVE-2021-21972

A notable real-world example of OS Command Injection is CVE-2021-21972, which affected the Jenkins Continuous Integration server. The vulnerability allowed attackers to inject malicious commands through the `JENKINS_URL` environment variable. By manipulating this variable, an attacker could execute arbitrary commands on the server, leading to potential data theft and server compromise.

### Lab Setup: Blind OS Command Injection with Time Delays

In this lab, we will explore a blind OS command injection vulnerability where the output of the injected command is not visible in the response. Instead, we will use time delays to confirm the presence of the vulnerability.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you don't already have one.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path for command injection.
6. Choose Lab Number Two titled "Blind OS Command Injection with Time Delays."

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/00-Overview|Overview]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/02-Exploiting the Vulnerability|Exploiting the Vulnerability]]
