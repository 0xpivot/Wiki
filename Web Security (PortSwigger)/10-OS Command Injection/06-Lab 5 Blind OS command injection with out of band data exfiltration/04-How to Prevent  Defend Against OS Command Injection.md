---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## How to Prevent / Defend Against OS Command Injection

### Secure Coding Practices

#### Vulnerable Code Example

```php
<?php
$user_input = $_GET['feedback'];
system("echo $user_input > /dev/null &");
?>
```

#### Secure Code Example

```php
<?php
$user_input = filter_var($_GET['feedback'], FILTER_SANITIZE_STRING);
system("echo \"$user_input\" > /dev/null &");
?>
```

In the secure code example, `filter_var` is used to sanitize the user input, ensuring that it does not contain harmful characters.

### Configuration Hardening

Ensure that your application's configuration is hardened against command injection attacks. This includes setting appropriate permissions and disabling unnecessary features.

### Detection and Monitoring

Implement robust logging and monitoring to detect and respond to potential command injection attempts. Use tools like intrusion detection systems (IDS) and security information and event management (SIEM) systems to monitor for suspicious activity.

### Regular Security Audits

Regularly conduct security audits and penetration testing to identify and mitigate vulnerabilities. This includes reviewing code for insecure practices and ensuring that all dependencies are up-to-date.

### Real-World Example: CVE-2021-3186 Mitigation

For the CVE-2021-3186 vulnerability in Jenkins, the mitigation involved updating to a patched version of the affected plugin and ensuring that all user inputs were properly validated and sanitized.

---
<!-- nav -->
[[03-Common Mistakes and Pitfalls|Common Mistakes and Pitfalls]] | [[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/00-Overview|Overview]] | [[05-OS Command Injection An In-Depth Analysis|OS Command Injection An In-Depth Analysis]]
