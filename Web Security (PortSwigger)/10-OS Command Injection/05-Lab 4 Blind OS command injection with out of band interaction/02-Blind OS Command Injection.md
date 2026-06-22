---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Blind OS Command Injection

### What is Blind OS Command Injection?

Blind OS Command Injection is a variant of OS Command Injection where the attacker does not receive direct feedback from the executed command. Instead, the attacker relies on indirect methods to determine whether the injection was successful. This makes the attack more challenging but also more stealthy.

### Why is Blind OS Command Injection Important?

Blind OS Command Injection is significant because it allows attackers to bypass traditional feedback mechanisms. Without immediate confirmation, the attacker must use creative methods to verify the success of their injection. This often involves leveraging side effects of the command execution, such as network interactions or changes in application behavior.

### How Does Blind OS Command Injection Work?

In Blind OS Command Injection, the attacker injects a command that triggers some observable effect. For example, the command might cause the server to make a network request to a server controlled by the attacker. By monitoring this external server, the attacker can infer whether the injection was successful.

### Real-World Example: CVE-2020-14882

CVE-2020-14882 is a real-world example of Blind OS Command Injection affecting the Apache Struts framework. In this case, an attacker could inject commands into the `Content-Type` header of an HTTP request. Although the server did not provide direct feedback, the attacker could observe the effects of the injected commands by monitoring network traffic.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/05-Lab 4 Blind OS command injection with out of band interaction/01-Introduction to OS Command Injection|Introduction to OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/05-Lab 4 Blind OS command injection with out of band interaction/00-Overview|Overview]] | [[03-Lab Setup Blind OS Command Injection with Out-of-Band Interaction|Lab Setup Blind OS Command Injection with Out-of-Band Interaction]]
