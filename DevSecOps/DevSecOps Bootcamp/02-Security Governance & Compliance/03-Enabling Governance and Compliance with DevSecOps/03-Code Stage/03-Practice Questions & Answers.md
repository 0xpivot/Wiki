---
course: DevSecOps
topic: Enabling Governance and Compliance with DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of "shifting left" in the context of DevSecOps and how it relates to static application security testing (SAST).**

Shifting left in DevSecOps refers to the practice of integrating security practices earlier into the software development lifecycle (SDLC), ideally at the beginning. This means incorporating security measures during the design and coding stages rather than waiting until later stages like testing or deployment. Static Application Security Testing (SAST) is a key component of shifting left because it allows developers to identify and fix security vulnerabilities in the code while it is being written. By catching issues early, teams can reduce the overall cost and time required to address security problems, as fixing bugs becomes more expensive the later they are found in the SDLC.

**Q2. How does SAST help prevent SQL injection attacks in code? Provide an example.**

SAST tools analyze the source code to identify patterns that could lead to SQL injection vulnerabilities. For instance, if a piece of code accepts user input and uses it directly in a SQL query without proper sanitization, a SAST tool would flag this as a potential issue. Here’s an example:

```python
# Vulnerable code
user_input = request.form['username']
query = f"SELECT * FROM users WHERE username = '{user_input}'"
```

A SAST tool would flag the `query` line as potentially vulnerable to SQL injection. It would suggest that the developer sanitize the input or use parameterized queries instead, such as:

```python
# Secure code
user_input = request.form['username']
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (user_input,))
```

This way, the tool helps developers write secure code by identifying and suggesting fixes for common vulnerabilities like SQL injection.

**Q3. What are some popular SAST tools used in DevSecOps, and how do they integrate into the development environment?**

Some popular SAST tools include:

- **SonarQube**: A widely-used tool that integrates with various IDEs and CI/CD pipelines. It provides detailed reports on code quality and security vulnerabilities. Developers can see issues directly in their IDE and get suggestions on how to fix them.
  
- **Checkmarx**: Another comprehensive SAST tool that supports multiple programming languages and integrates with various development environments. It offers real-time feedback and can enforce custom security policies defined by the organization.

These tools typically integrate into the development environment through plugins or extensions for IDEs like Eclipse, IntelliJ IDEA, and Visual Studio. They can also be configured to run as part of the continuous integration process, ensuring that code is checked for vulnerabilities before it is committed to the repository.

**Q4. How can organizations customize SAST tools to enforce their specific security policies?**

Organizations can customize SAST tools to enforce their specific security policies by configuring the tools to recognize and flag violations of those policies. This involves defining rules and checks that align with the organization's security standards. For example, if an organization has a policy that all user inputs must be validated and sanitized, the SAST tool can be configured to flag any instances where this is not done.

Customization can be achieved through configuration files or interfaces provided by the SAST tool. These configurations can specify what types of code patterns are considered insecure and what actions should be taken when such patterns are detected. Additionally, organizations can create custom rulesets that extend the capabilities of the tool to cover specific organizational requirements.

**Q5. Discuss a recent real-world example where SAST could have prevented a security breach.**

One recent example is the Capital One data breach in 2019, where a misconfigured web application firewall led to unauthorized access to sensitive customer data. While this particular breach was due to a configuration error rather than a coding vulnerability, a robust SAST tool integrated into the development process could have helped prevent similar issues by identifying and flagging insecure code patterns related to access control and data handling.

For instance, if the developers had been using a SAST tool that flagged insecure coding practices related to authentication and authorization, they might have caught the misconfiguration earlier. This highlights the importance of integrating SAST into the development process to catch and fix security issues early, reducing the risk of breaches.

---
<!-- nav -->
[[02-Implementing Security Compliance and Governance in the Coding Stage|Implementing Security Compliance and Governance in the Coding Stage]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/03-Enabling Governance and Compliance with DevSecOps/03-Code Stage/00-Overview|Overview]]
