---
course: DevSecOps
topic: Understanding What and Where to Test during Automated Security Testing
tags: [devsecops]
---

## Quick Wins in Automated Security Testing

### Identifying Quick Wins

Quick wins are security improvements that can be implemented with minimal effort but yield significant benefits. Here are some examples:

1. **Static Application Security Testing (SAST)**: SAST tools analyze source code to identify security vulnerabilities. Implementing SAST can help catch common coding errors and security issues early in the development cycle.
2. **Dependency Scanning**: Tools like `npm audit` or `pip-audit` can scan project dependencies for known vulnerabilities. This is particularly useful for projects that rely heavily on third-party libraries.
3. **Configuration Management**: Ensuring that configurations are secure can prevent common misconfigurations that lead to security vulnerabilities. Tools like `kube-bench` can help validate Kubernetes cluster configurations.

### Example: Static Application Security Testing (SAST)

#### Background Theory

SAST tools analyze source code to identify potential security vulnerabilities. They work by parsing the code and applying a set of rules to detect patterns that indicate security issues. Common vulnerabilities detected by SAST tools include SQL injection, cross-site scripting (XSS), and buffer overflows.

#### Implementation Steps

1. **Choose a Tool**: Select a SAST tool that supports your programming language and integrates well with your development environment. Popular choices include SonarQube, Fortify, and Checkmarx.
2. **Configure the Tool**: Set up the tool to analyze your codebase. This typically involves specifying the location of your source code and configuring any additional settings.
3. **Run the Analysis**: Execute the SAST analysis. The tool will parse your code and report any identified vulnerabilities.
4. **Review and Fix Issues**: Review the reported issues and address them. This may involve modifying the code to eliminate the security vulnerability.

#### Code Example

```python
# Vulnerable code
def login(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    return result

# Secure code
import sqlite3
from sqlite3 import Error

def login_secure(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result
```

### How to Prevent / Defend

1. **Use Parameterized Queries**: Always use parameterized queries to prevent SQL injection attacks.
2. **Input Validation**: Validate user input to ensure it meets expected criteria.
3. **Secure Coding Practices**: Follow secure coding guidelines to avoid common security pitfalls.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/05-Process vs. Product|Process vs. Product]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/07-Team Support for Automated Security Testing|Team Support for Automated Security Testing]]
