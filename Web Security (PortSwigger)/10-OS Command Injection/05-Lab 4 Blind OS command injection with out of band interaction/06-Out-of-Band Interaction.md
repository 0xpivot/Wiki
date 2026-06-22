---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Out-of-Band Interaction

### What is Out-of-Band Interaction?

Out-of-Band Interaction is a technique used in Blind OS Command Injection where the attacker triggers an interaction with an external server that they control. This external server acts as a beacon, allowing the attacker to confirm the success of their injection.

### Why is Out-of-Band Interaction Useful?

Out-of-Band Interaction is useful because it provides a reliable method for the attacker to verify the success of their injection. By monitoring the external server, the attacker can determine whether the injected command was executed, even if the application itself does not provide direct feedback.

### How Does Out-of-Band Interaction Work?

In Out-of-Band Interaction, the attacker injects a command that causes the server to make a network request to an external server. This external server logs the request, providing evidence that the injection was successful. For example, the attacker might inject a command that performs a DNS lookup on a domain controlled by the attacker.

### Real-World Example: CVE-2021-2109

CVE-2021-2109 is a real-world example of Out-of-Band Interaction affecting the VMware Workspace ONE Access product. In this case, an attacker could inject commands into the `User-Agent` header of an HTTP request. Although the server did not provide direct feedback, the attacker could observe the effects of the injected commands by monitoring network traffic to an external server.

---
<!-- nav -->
[[05-OS Command Injection|OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/05-Lab 4 Blind OS command injection with out of band interaction/00-Overview|Overview]] | [[07-Understanding Out-of-Band Interaction|Understanding Out-of-Band Interaction]]
