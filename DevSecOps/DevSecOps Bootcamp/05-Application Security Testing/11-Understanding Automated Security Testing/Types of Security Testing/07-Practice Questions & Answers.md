---
course: DevSecOps
topic: Understanding Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between static and dynamic application security testing.**

Static Application Security Testing (SAST) involves analyzing the source code without executing it. SAST tools can identify potential security flaws such as hard-coded secrets, improper error handling, and coding standards violations. For example, a linter can check for formatting and consistency issues, while a static source code analysis tool can detect security vulnerabilities like SQL injection points.

Dynamic Application Security Testing (DAST), on the other hand, involves running the application and testing it in its runtime environment. DAST tools can simulate attacks to find security issues, such as input validation problems or buffer overflows. Fuzzing is a common technique used in DAST, where the tool sends random data to the application to see how it responds. Attack proxies, like the open-source security scanner OASP SAP, also fall under DAST by attempting to exploit vulnerabilities in the running code.

**Q2. How would you use a static source code analysis tool to identify hard-coded secrets in your codebase?**

To identify hard-coded secrets using a static source code analysis tool, you would configure the tool to scan for patterns indicative of secrets. For example, the tool could search for strings that resemble API keys, passwords, or database connection strings. A typical configuration might include regular expressions to match common secret formats. Once configured, the tool would scan the entire codebase and report any instances where it detects a potential secret.

Here’s an example of how you might configure a tool like `TruffleHog` to scan for secrets:

```bash
trufflehog --regex --entropy=False /path/to/codebase
```

This command will scan the specified directory for hardcoded secrets using predefined regex patterns.

**Q3. What is the role of a vulnerability scanner in the context of DevSecOps?**

A vulnerability scanner plays a critical role in identifying known vulnerabilities within an organization's systems and applications. It automates the process of checking for vulnerabilities by following these steps:

1. **Fingerprinting Assets**: The scanner identifies and catalogs all the assets in use, such as servers, containers, and third-party libraries, often using checksums or other unique identifiers.
   
2. **Ingesting Vulnerability Lists**: The scanner retrieves lists of known vulnerabilities from trusted sources on the internet, such as the National Vulnerability Database (NVD).

3. **Comparing Assets with Known Vulnerabilities**: The scanner compares the identified assets against the list of known vulnerabilities to determine if any matches exist. If a match is found, the scanner reports the vulnerability.

For example, the recent CVE-2021-44228 (Log4j vulnerability) was a widely publicized issue that affected many applications. A vulnerability scanner would help organizations quickly identify if their systems were using vulnerable versions of Log4j.

**Q4. How would you exploit a known vulnerability in a third-party library using a vulnerability scanner?**

To exploit a known vulnerability in a third-party library, you would follow these steps:

1. **Identify the Vulnerable Library**: Use a vulnerability scanner to identify the presence of a known vulnerable library in your codebase. For example, a scanner might flag the presence of a vulnerable version of Apache Struts.

2. **Understand the Vulnerability**: Research the specific details of the vulnerability, such as its Common Vulnerabilities and Exposures (CVE) identifier and the type of attack it enables. For instance, CVE-2017-5638 in Apache Struts 2.3.x allowed remote code execution through a content type misconfiguration.

3. **Craft an Exploit**: Based on the vulnerability details, craft an exploit that targets the specific flaw. For example, if the vulnerability allows remote code execution, you might craft a payload that injects malicious commands into the application.

4. **Test the Exploit**: Use a controlled environment to test the exploit against the vulnerable library. Ensure that you have proper authorization and that your actions comply with legal and ethical guidelines.

Here’s an example of a simple payload that might be used to exploit a vulnerability in a web application:

```python
import requests

url = 'http://target-server/path'
payload = {'vulnerable-param': 'malicious-command'}

response = requests.post(url, data=payload)
print(response.text)
```

**Q5. Why is it important to perform both static and dynamic application security testing?**

Performing both static and dynamic application security testing is crucial because each approach offers unique benefits and addresses different aspects of security:

- **Static Application Security Testing (SAST)** helps identify security flaws early in the development lifecycle, before the code is even executed. This includes issues like hard-coded secrets, improper error handling, and adherence to coding standards. By catching these issues early, developers can fix them before they become part of the deployed application.

- **Dynamic Application Security Testing (DAST)** simulates real-world attacks on the running application, helping to identify issues that may arise during runtime. This includes input validation problems, buffer overflows, and other runtime vulnerabilities. DAST can also help ensure that the application behaves securely under various conditions and user inputs.

By combining both approaches, organizations can achieve a more comprehensive security posture. For example, the Equifax breach in 2017 was partly due to a vulnerability in Apache Struts that could have been detected and mitigated with both SAST and DAST. SAST could have flagged the use of the vulnerable library, while DAST could have simulated attacks to confirm the presence of the vulnerability.

**Q6. How does a container vulnerability scanner work, and why is it important in a DevSecOps pipeline?**

A container vulnerability scanner works by analyzing the contents of Docker images or other container formats to identify known vulnerabilities. Here’s how it typically operates:

1. **Fingerprinting Containers**: The scanner identifies and catalogs the components within the container, such as operating system packages, libraries, and binaries.

2. **Ingesting Vulnerability Lists**: The scanner retrieves lists of known vulnerabilities from trusted sources, similar to how a traditional vulnerability scanner operates.

3. **Comparing Components with Known Vulnerabilities**: The scanner compares the identified components against the list of known vulnerabilities to determine if any matches exist. If a match is found, the scanner reports the vulnerability.

Container vulnerability scanning is crucial in a DevSecOps pipeline because containers are increasingly used to package and deploy applications. Since containers often include third-party libraries and dependencies, they can introduce vulnerabilities if not properly scanned. By integrating container vulnerability scanning into the CI/CD pipeline, organizations can ensure that only secure containers are deployed, reducing the risk of vulnerabilities being introduced into production environments.

For example, the recent CVE-2021-44228 (Log4j vulnerability) highlighted the importance of continuous monitoring and scanning of container images to ensure that they do not contain vulnerable versions of libraries.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/Types of Security Testing/06-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/Types of Security Testing/00-Overview|Overview]]
