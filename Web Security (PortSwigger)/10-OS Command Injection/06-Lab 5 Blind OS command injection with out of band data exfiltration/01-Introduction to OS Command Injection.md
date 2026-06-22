---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Introduction to OS Command Injection

### What is OS Command Injection?

OS Command Injection is a type of vulnerability that occurs when an application constructs and executes a system command using untrusted input. This can allow an attacker to inject arbitrary commands into the system, potentially leading to unauthorized actions such as data theft, denial of service, or even full system compromise.

### Why Does OS Command Injection Matter?

Command injection vulnerabilities are critical because they can lead to severe security breaches. An attacker can leverage these vulnerabilities to execute arbitrary commands on the server, bypassing intended security controls. This can result in unauthorized access to sensitive data, execution of malicious code, and even complete control over the server.

### How Does OS Command Injection Work Under the Hood?

When an application constructs a system command using user-supplied input, it typically uses functions like `exec()`, `system()`, or `shell_exec()` in various programming languages. If the input is not properly sanitized or validated, an attacker can inject additional commands or modify existing ones.

For example, consider a PHP script that executes a system command based on user input:

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

This would execute both the `echo` command and the `rm -rf /` command, which could delete all files on the server.

### Real-World Example: CVE-2021-3186

A notable real-world example of OS Command Injection is CVE-2021-3186, which affected the Jenkins CI/CD platform. The vulnerability allowed attackers to inject arbitrary commands into the Jenkins environment, leading to potential remote code execution. This was due to improper validation of user input in certain Jenkins plugins.

### Out-of-Band Data Exfiltration

In some cases, the application may not provide direct feedback about the injected command's output. Instead, the attacker can use out-of-band techniques to exfiltrate data. This often involves triggering interactions with external domains, such as DNS queries, to retrieve the desired information.

### Lab Setup: Blind OS Command Injection

The lab described in the transcript involves a blind OS command injection vulnerability where the application executes a shell command containing user-supplied details. The command is executed asynchronously and does not affect the application's response. However, the attacker can trigger out-of-band interactions with an external domain to exfiltrate data.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit the Web Security Academy at [portswigger.net/web-security](https://portswigger.net/web-security).
2. Click on the sign-up button to create an account.
3. Log in and navigate to the Academy section.
4. Select the learning path and then choose the command injection module.
5. Finally, select lab number five titled "Blind OS Command Injection without a band data exfiltration."

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/00-Overview|Overview]] | [[02-OS Command Injection Overview|OS Command Injection Overview]]
