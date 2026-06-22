---
course: DevSecOps
topic: Understanding Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of test-driven security and how it compares to test-driven development.**

Test-driven security is a methodology where security requirements are defined first, followed by the creation of tests for those requirements. Initially, these tests fail because the security controls or mitigations are not yet implemented. Once the controls are implemented, the tests are run again to ensure they pass. This process continues until all security requirements are met. This approach is similar to test-driven development (TDD), where tests are written before the actual code to ensure that the code meets the specified requirements. Both methodologies aim to ensure that the system behaves as expected from the outset, promoting better design and fewer bugs.

**Q2. What are the differences between positive testing (happy path) and negative testing (sad path)? Provide examples of each.**

Positive testing, also known as happy path testing, involves verifying that the system produces the expected output when given a specific input. For example, entering a valid username and password and ensuring that the user can successfully log in. Negative testing, or sad path testing, involves testing scenarios where the system is expected to handle unexpected or invalid inputs gracefully. For instance, entering an incorrect password and verifying that the system returns an appropriate error message or blocks the login attempt.

**Q3. Describe the two main methods of security testing mentioned in the lecture: static testing and dynamic testing. Provide examples of each.**

Static testing involves analyzing the application without executing it. Examples include reviewing the source code for potential security flaws or checking the configuration settings of a web server to ensure compliance with security policies. Dynamic testing, on the other hand, involves running the application and interacting with it to identify security issues. Examples include using dynamic application security testing (DAST) tools to simulate attacks against a running application or conducting network vulnerability scans to detect weaknesses in the network configuration.

**Q4. What are the three broad categories of security testing mentioned in the lecture?**

The three broad categories of security testing mentioned are:
1. Static Application Security Testing (SAST): Analyzing the source code for security vulnerabilities without executing the application.
2. Dynamic Application Security Testing (DAST): Testing the application while it is running to identify security issues.
3. Vulnerability Scanning: Using automated tools to scan networks, systems, or applications for known vulnerabilities.

**Q5. Why is it important to use different types of testing in security testing?**

It is important to use different types of testing in security testing because relying solely on one type, such as test-driven security (which focuses on positive testing), may not uncover all potential security issues. Positive testing ensures that the system works correctly under expected conditions, but it does not account for unexpected or malicious inputs. Negative testing helps identify how the system handles unexpected situations, while static and dynamic testing provide a comprehensive view of both the code and runtime behavior. Combining these approaches ensures a more robust and secure system.

**Q6. How does negative testing differ from positive testing in terms of difficulty and expected outcomes?**

Negative testing is generally more challenging than positive testing because it involves identifying and testing a wide range of unexpected or malicious inputs. Unlike positive testing, where the expected outcome is clear (e.g., successful login), negative testing often lacks a definitive expected outcome. The goal is to ensure that the system handles unexpected inputs safely and securely, which can be difficult to verify without extensive knowledge of the system's intended behavior. Additionally, negative testing may not always produce obvious errors, making it harder to determine if the system is behaving correctly.

---
<!-- nav -->
[[02-Understanding Automated Security Testing|Understanding Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/01-What Is Automated Security Testing/00-Overview|Overview]]
