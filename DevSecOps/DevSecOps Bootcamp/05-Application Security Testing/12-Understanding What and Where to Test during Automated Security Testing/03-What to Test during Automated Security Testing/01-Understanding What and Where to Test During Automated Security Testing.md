---
course: DevSecOps
topic: Understanding What and Where to Test during Automated Security Testing
tags: [devsecops]
---

## Understanding What and Where to Test During Automated Security Testing

### Introduction

Automated security testing is an essential component of modern DevSecOps practices. It ensures that applications are secure throughout their development lifecycle, from initial design to final deployment. To effectively implement automated security testing, it is crucial to understand what aspects of an application can and should be tested. This chapter will delve into the details of testing various components of a generic web application, including code, containers, and infrastructure.

### Generic Web Application Lifecycle

To illustrate the process, let's consider a typical web application lifecycle using a hypothetical company called Global Mantix. The developers at Global Mantix work with a version control system called MAVE. Here’s a breakdown of the steps involved:

1. **Code Development**: Developers write code and push it to a repository.
2. **Build Process**: A build server pulls the code from the repository and builds artifacts, such as binaries or container images.
3. **Deployment**: These artifacts are then deployed to the production environment via a network.

This process can be visualized using a `mermaid` diagram:

```mermaid
graph TD
    A[Developer Writes Code] --> B[Pushes Code to Repository]
    B --> C[Build Server Pulls Code]
    C --> D[Build Artifacts (Binaries/Containers)]
    D --> E[Deploy Artifacts to Production Environment]
```

### Partitioning for Testing

The lifecycle can be partitioned into three main areas for testing:

1. **Code**: The source code in the repository.
2. **Containers**: The build artifacts, such as container images.
3. **Infrastructure**: The deployment environment where the application runs.

Each of these areas presents unique opportunities and challenges for security testing.

### Testing the Code

#### Importance of Readability

One of the first aspects to test in the code is readability. While it may seem counterintuitive, code readability is closely tied to security. Here’s why:

- **Maintainability**: Code that is difficult to read is harder to maintain. This increases the likelihood of introducing security vulnerabilities during maintenance.
- **Collaboration**: In a team setting, other developers need to understand the code. Poorly written code can lead to misunderstandings and errors, potentially introducing security flaws.
- **Auditing**: Security audits require comprehensible code. If the code is unreadable, auditors may miss critical vulnerabilities.

#### Example of Unreadable Code

Consider the following Python code snippet:

```python
def process_data(data):
    if data['status'] == 'active':
        return True
    else:
        return False
```

This code is straightforward but can be improved for readability and maintainability:

```python
def is_active(data):
    return data.get('status') == 'active'
```

#### Tools for Code Readability

Several tools can help ensure code readability:

- **Linters**: Tools like ESLint for JavaScript or PyLint for Python can enforce coding standards.
- **Static Analysis Tools**: Tools like SonarQube can analyze code for maintainability and security issues.

#### How to Prevent / Defend

**Detection**:
- Use static analysis tools to identify poorly written code.
- Conduct regular code reviews to catch readability issues.

**Prevention**:
- Implement coding standards and guidelines.
- Use linters and static analysis tools as part of the CI/CD pipeline.

**Secure Coding Fix**:

**Vulnerable Code**:
```python
def process_data(data):
    if data['status'] == 'active':
        return True
    else:
        return False
```

**Fixed Code**:
```python
def is_active(data):
    return data.get('status') == 'active'
```

### Testing Maintainability and Clarity

#### Importance of Maintainability

Maintainability is another critical aspect of code testing. Code that is easy to maintain is less likely to introduce security vulnerabilities. Here’s why:

- **Error Reduction**: Maintainable code reduces the likelihood of errors during updates and bug fixes.
- **Security Audits**: Maintainable code is easier to audit, making it simpler to identify and fix security issues.

#### Example of Maintainable Code

Consider the following Java code snippet:

```java
public class User {
    private String username;
    private String password;

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public boolean authenticate(String inputPassword) {
        return password.equals(inputPassword);
    }
}
```

This code can be improved for maintainability:

```java
public class User {
    private String username;
    private String hashedPassword;

    public User(String username, String password) {
        this.username = username;
        this.hashedPassword = hashPassword(password);
    }

    public boolean authenticate(String inputPassword) {
        return hashedPassword.equals(hashPassword(inputPassword));
    }

    private String hashPassword(String password) {
        // Implementation of a secure hashing algorithm
        return new BCryptPasswordEncoder().encode(password);
    }
}
```

#### Tools for Maintainability

Several tools can help ensure code maintainability:

- **Refactoring Tools**: Tools like IntelliJ IDEA or Eclipse can assist in refactoring code.
- **Dependency Management**: Tools like Maven or Gradle can manage dependencies and ensure consistent versions.

#### How to Prevent / Defend

**Detection**:
- Use static analysis tools to identify maintainability issues.
- Conduct regular code reviews to catch maintainability issues.

**Prevention**:
- Implement coding standards and guidelines.
- Use refactoring tools and dependency management tools as part of the CI/CD pipeline.

**Secure Coding Fix**:

**Vulnerable Code**:
```java
public class User {
    private String username;
    private String password;

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public boolean authenticate(String inputPassword) {
        return password.equals(inputPassword);
    }
}
```

**Fixed Code**:
```java
public class User {
    private String username;
    private String hashedPassword;

    public User(String username, String password) {
        this.username = username;
        this.hashedPassword = hashPassword(password);
    }

    public boolean authenticate(String inputPassword) {
        return hashedPassword.equals(hashPassword(inputPassword));
    }

    private String hashPassword(String password) {
        // Implementation of a secure hashing algorithm
        return new BCryptPasswordEncoder().encode(password);
    }
}
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-44228 (Log4Shell)**: This vulnerability in Apache Log4j was caused by poorly written code that allowed remote code execution. Ensuring code readability and maintainability could have helped prevent this issue.
- **Equifax Data Breach (2017)**: This breach was partly due to outdated software and poorly maintained code. Regular code reviews and maintainability checks could have helped mitigate this risk.

### Conclusion

Testing the code for readability, maintainability, and clarity is a fundamental aspect of automated security testing. By ensuring that code is well-written and maintainable, developers can reduce the likelihood of introducing security vulnerabilities. Tools and practices such as linters, static analysis, and regular code reviews are essential for maintaining high-quality code.

### Practice Labs

For hands-on experience with automated security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning security testing techniques.

These labs provide practical experience in identifying and fixing security vulnerabilities in code, containers, and infrastructure.

### Next Steps

In the next section, we will explore testing containers and infrastructure for security vulnerabilities. Stay tuned for a comprehensive guide on how to effectively test these components in a DevSecOps environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/03-What to Test during Automated Security Testing/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/03-What to Test during Automated Security Testing/02-Practice Questions & Answers|Practice Questions & Answers]]
