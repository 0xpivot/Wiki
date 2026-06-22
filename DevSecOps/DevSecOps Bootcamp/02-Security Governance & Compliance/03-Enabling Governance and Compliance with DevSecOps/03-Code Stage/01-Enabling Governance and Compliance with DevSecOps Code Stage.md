---
course: DevSecOps
topic: Enabling Governance and Compliance with DevSecOps
tags: [devsecops]
---

## Enabling Governance and Compliance with DevSecOps: Code Stage

### Introduction to Static Application Security Testing (SAST)

Static Application Security Testing (SAST) is a crucial component of the DevSecOps pipeline, particularly during the code stage. SAST tools analyze the source code of an application to identify potential security vulnerabilities and coding errors before the application is compiled or deployed. This proactive approach helps in minimizing the cost and significantly increasing the speed at which issues can be resolved.

#### What is SAST?

SAST, also known as white-box testing, involves analyzing the source code of an application to identify security vulnerabilities. Unlike black-box testing, which tests the application from the outside without access to the source code, SAST uses the internal structure of the application to find weaknesses. This makes it particularly effective in identifying issues that might not be apparent through external testing alone.

#### Why Use SAST?

The primary reason for using SAST is to catch security vulnerabilities early in the development process. This is important because:

1. **Cost Reduction**: Fixing bugs and vulnerabilities early in the development cycle is significantly less expensive than fixing them after deployment.
2. **Speed of Resolution**: With SAST, developers can quickly identify and fix issues, reducing the time required for debugging and testing.
3. **Compliance**: Many regulatory frameworks require organizations to implement security controls throughout the development lifecycle. SAST helps ensure compliance by identifying and addressing security issues proactively.

### How SAST Works

SAST tools work by parsing the source code and applying a set of rules or heuristics to identify potential security vulnerabilities. These rules are based on common coding patterns that have been associated with security issues in the past. Here’s a high-level overview of the process:

1. **Code Parsing**: The tool reads the source code and parses it into an abstract syntax tree (AST).
2. **Rule Application**: The tool applies a set of predefined rules to the AST to identify potential security issues.
3. **Vulnerability Reporting**: The tool generates a report detailing the identified vulnerabilities, including their location in the code and a description of the issue.

#### Example of SAST in Action

Consider a simple example where a developer writes a function that takes user input and stores it in a database. A SAST tool might flag this code as potentially vulnerable to SQL injection if the input is not properly sanitized.

```python
def store_user_input(user_input):
    query = f"INSERT INTO users (input) VALUES ('{user_input}')"
    execute_query(query)
```

A SAST tool would likely flag the `query` construction as risky due to the direct inclusion of user input without proper sanitization. The tool might generate a report indicating that this code could be vulnerable to SQL injection attacks.

### Popular SAST Tools

There are numerous SAST tools available on the market, both free and commercial. Some of the most well-known tools include:

1. **SonarQube**
2. **Checkmarx**
3. **Fortify**
4. **Veracode**
5. **OWASP Dependency-Check**

#### SonarQube

SonarQube is one of the most widely used SAST tools. It supports multiple programming languages and integrates seamlessly with various development environments. SonarQube provides a comprehensive suite of features, including:

- **Code Quality Analysis**: Identifies code smells, bugs, and vulnerabilities.
- **Security Analysis**: Detects security vulnerabilities based on OWASP Top Ten and other security standards.
- **Continuous Integration**: Integrates with CI/CD pipelines to provide real-time feedback on code quality and security.

Here’s an example of how SonarQube can be integrated into a project:

1. **Installation**: Install SonarQube on your server or use a cloud-based instance.
2. **Configuration**: Configure SonarQube to scan your codebase. This typically involves setting up a `sonar-project.properties` file.

```properties
# sonar-project.properties
sonar.projectKey=my_project_key
sonar.sources=src
sonar.language=java
```

3. **Scanning**: Run the SonarQube scanner as part of your build process.

```bash
sonar-scanner
```

4. **Review Results**: Review the results in the SonarQube dashboard.

#### Checkmarx

Checkmarx is another popular SAST tool, particularly known for its deep static analysis capabilities. It supports multiple languages and frameworks and provides detailed reports on security vulnerabilities.

Here’s an example of how Checkmarx can be integrated into a project:

1. **Installation**: Install Checkmarx on your server or use a cloud-based instance.
2. **Configuration**: Configure Checkmarx to scan your codebase. This typically involves setting up a `checkmarx.properties` file.

```properties
# checkmarx.properties
projectName=my_project_name
sourcePath=src
language=java
```

3. **Scanning**: Run the Checkmarx scanner as part of your build process.

```bash
checkmarx-scan
```

4. **Review Results**: Review the results in the Checkmarx dashboard.

### Real-World Examples and Case Studies

#### Recent CVEs and Breaches

SAST tools have played a significant role in identifying and mitigating security vulnerabilities in real-world applications. Here are a few recent examples:

1. **CVE-2021-21972**: This vulnerability was found in the Apache Log4j library, which is widely used in Java applications. SAST tools were able to identify the vulnerability by analyzing the code and flagging the insecure logging mechanism.

2. **SolarWinds Supply Chain Attack**: In this attack, malicious code was injected into SolarWinds software updates. SAST tools could have helped identify the malicious code by analyzing the source code and flagging suspicious patterns.

### Common Pitfalls and Best Practices

While SAST tools are powerful, they are not without their limitations. Here are some common pitfalls and best practices to keep in mind:

#### Pitfalls

1. **False Positives**: SAST tools can sometimes generate false positives, where the tool flags code as vulnerable even though it is not. This can lead to wasted time and effort in investigating non-issues.
2. **False Negatives**: Conversely, SAST tools can also miss vulnerabilities, especially if the code is complex or obfuscated.
3. **Tool Configuration**: Improper configuration of SAST tools can lead to incomplete or inaccurate results.

#### Best Practices

1. **Regular Updates**: Keep your SAST tools updated to ensure they are using the latest rules and heuristics.
2. **Custom Rules**: Customize the rules used by your SAST tool to better match the specific needs of your project.
3. **Integrate with CI/CD**: Integrate SAST tools into your CI/CD pipeline to ensure that code is scanned automatically and continuously.
4. **Review Results**: Regularly review the results generated by SAST tools and address any identified vulnerabilities promptly.

### How to Prevent / Defend

#### Detection

To effectively detect security vulnerabilities using SAST tools, follow these steps:

1. **Select the Right Tool**: Choose a SAST tool that supports the programming languages and frameworks used in your project.
2. **Configure Properly**: Configure the tool to scan your entire codebase and customize the rules to match your specific needs.
3. **Run Regular Scans**: Integrate SAST scans into your CI/CD pipeline to ensure that code is scanned regularly.

#### Prevention

To prevent security vulnerabilities, follow these best practices:

1. **Secure Coding Practices**: Follow secure coding practices, such as input validation, output encoding, and least privilege principles.
2. **Code Reviews**: Conduct regular code reviews to catch security issues early.
3. **Training and Awareness**: Train developers on security best practices and raise awareness about common security vulnerabilities.

#### Secure-Coding Fixes

Here’s an example of how to fix a SQL injection vulnerability using secure coding practices:

**Vulnerable Code:**

```python
def store_user_input(user_input):
    query = f"INSERT INTO users (input) VALUES ('{user_input}')"
    execute_query(query)
```

**Fixed Code:**

```python
import sqlite3

def store_user_input(user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (input) VALUES (?)", (user_input,))
    conn.commit()
    conn.close()
```

In the fixed code, parameterized queries are used to prevent SQL injection attacks.

### Conclusion

Static Application Security Testing (SAST) is a critical component of the DevSecOps pipeline, enabling organizations to identify and mitigate security vulnerabilities early in the development process. By integrating SAST tools into your CI/CD pipeline, you can ensure that your code is secure and compliant with regulatory requirements. Remember to follow best practices and regularly review the results generated by SAST tools to stay ahead of potential security threats.

### Practice Labs

For hands-on experience with SAST tools, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various security topics, including SAST.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **SonarQube Community Edition**: Provides a free version of SonarQube for learning and experimenting with SAST.

By leveraging these resources, you can gain practical experience with SAST tools and improve your ability to identify and mitigate security vulnerabilities in your code.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/03-Enabling Governance and Compliance with DevSecOps/03-Code Stage/00-Overview|Overview]] | [[02-Implementing Security Compliance and Governance in the Coding Stage|Implementing Security Compliance and Governance in the Coding Stage]]
