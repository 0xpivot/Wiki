---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Understanding Time-Based OS Command Injection

### What is Time-Based OS Command Injection?

Time-Based OS Command Injection is a specific type of OS Command Injection where the attacker uses time delays to determine if the injection was successful. This technique is often used when the application does not provide direct feedback on the success of the injection.

### Why Use Time Delays?

Time delays are used because they can help confirm whether the injected command was executed. By introducing a delay, the attacker can observe changes in the response time of the application, indicating that the command was successfully executed.

### Example Scenario

Consider a web application that accepts user input and executes a command on the server. The attacker can inject a command like `sleep 5` to introduce a 5-second delay. If the response time increases by 5 seconds, the attacker knows the injection was successful.

### Real-World Example

A real-world example of Time-Based OS Command Injection is the exploitation of a vulnerability in a web application that allowed attackers to inject commands via the `PATH` environment variable. By injecting a `sleep` command, attackers were able to confirm the vulnerability and gain unauthorized access.

### Lab Setup

For this lab, we will use the PortSwigger Web Security Academy, which provides a scenario where the application is vulnerable to Time-Based OS Command Injection.

---
<!-- nav -->
[[06-OS Command Injection with Time Delays|OS Command Injection with Time Delays]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/00-Overview|Overview]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/08-Understanding the Vulnerability|Understanding the Vulnerability]]
