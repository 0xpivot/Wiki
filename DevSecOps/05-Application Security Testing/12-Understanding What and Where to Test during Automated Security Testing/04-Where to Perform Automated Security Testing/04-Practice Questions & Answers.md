---
course: DevSecOps
topic: Understanding What and Where to Test during Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of "Shift Left" in the context of security testing.**

Shift Left refers to the practice of moving security testing earlier in the software development lifecycle (SDLC). Traditionally, security testing was often performed late in the SDLC, typically after deployment, in the form of penetration testing. By shifting security testing to the left, meaning earlier stages such as development and deployment, organizations can identify and address vulnerabilities sooner, making it cheaper and easier to fix issues before they reach production.

**Q2. What are the advantages of performing security testing earlier in the SDLC?**

Performing security testing earlier in the SDLC offers several advantages:

1. **Better Accountability**: Developers receive immediate feedback on the security quality of their code, encouraging better coding practices.
2. **Cost Efficiency**: Finding and fixing vulnerabilities early reduces the cost associated with fixing issues later in the development process.
3. **Faster Deployment**: Issues are resolved before the code reaches production, ensuring smoother and faster deployment cycles.
4. **Codified Security Requirements**: Early integration of security testing ensures that security requirements are clearly defined and enforced throughout the development process.

**Q3. How can pre-commit hooks be used for security testing?**

Pre-commit hooks can be used to perform basic security checks before code is committed to the repository. These checks include:

1. **Linters**: Ensuring code readability and clarity.
2. **Hard-Coded Secrets Detection**: Preventing developers from accidentally committing sensitive information like API keys or passwords.
3. **Formatting Checks**: Ensuring code adheres to a consistent style guide.

For example, a pre-commit hook could use a tool like `git-secrets` to scan for hard-coded secrets:

```bash
#!/bin/sh
git secrets --register-aws --update
git secrets --scan
```

**Q4. What types of security tests can be performed during the commit phase?**

During the commit phase, you can perform various security tests, including:

1. **Static Source Code Analysis**: Tools like SonarQube or Fortify can detect insecure coding patterns.
2. **Maintainability Checks**: Integration tests can ensure that the code maintains its security properties.
3. **Hard-Coded Secrets Detection**: Similar to pre-commit hooks, these checks prevent sensitive data from being committed.
4. **Third-Party Library Scanning**: Tools like Snyk can scan for known vulnerabilities in third-party libraries.

For example, a static analysis tool might flag insecure coding patterns:

```bash
sonar-scanner -Dsonar.projectKey=my_project -Dsonar.sources=.
```

**Q5. Describe the role of dynamic scanning tools in the build phase.**

Dynamic scanning tools are used during the build phase to simulate attacks and identify vulnerabilities in the application’s runtime behavior. Common tools include:

1. **Attack Proxies**: Tools like OWASP ZAP can intercept and manipulate HTTP traffic to test for vulnerabilities.
2. **Fuzzing Tools**: These tools send random or malformed input to the application to test for unexpected behaviors or crashes.
3. **Configuration Error Checking**: Ensuring that configurations are hardened and free from common misconfigurations.

For example, OWASP ZAP can be configured to automatically scan an application during the build phase:

```bash
zap-cli.py -t http://localhost:8080 -r report.html
```

**Q6. How can automated security testing be utilized during the deploy phase?**

During the deploy phase, automated security testing focuses on ensuring the application is secure in its production environment. Key activities include:

1. **Dynamic Application Security Testing (DAST)**: Tools like Burp Suite or OWASP ZAP can be used to test the application’s security while it is running.
2. **Compliance Checks**: Verifying that the application meets specific security standards and policies.
3. **Runtime Defense Tools**: Implementing security measures like Web Application Firewalls (WAFs) to protect against real-time threats.

For example, a DAST tool might be configured to run automated scans during deployment:

```bash
burp_suite_scan.sh --target http://production-app.com --report report.xml
```

**Q7. Provide a recent real-world example of how shifting security testing left has helped in mitigating vulnerabilities.**

A recent example is the case of the Log4j vulnerability (CVE-2021-44228), which affected many organizations globally. Companies that had implemented Shift Left practices were able to identify and mitigate the vulnerability faster compared to those who only tested security in production. By integrating automated security testing tools like Snyk or OWASP Dependency Check into their CI/CD pipelines, organizations could quickly detect and patch the vulnerable versions of Log4j, reducing the risk of exploitation.

---
<!-- nav -->
[[03-Understanding What and Where to Test during Automated Security Testing|Understanding What and Where to Test during Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/04-Where to Perform Automated Security Testing/00-Overview|Overview]]
