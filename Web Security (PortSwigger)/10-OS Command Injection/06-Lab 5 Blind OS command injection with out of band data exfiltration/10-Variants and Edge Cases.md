---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Variants and Edge Cases

### Different Command Injection Techniques

There are several ways to perform command injection, including:

1. **Using Backticks (`)**: This method involves enclosing the command within backticks.
    ```plaintext
    `whoami`
    ```

2. **Using Dollar Sign ($)**: Another method involves using the dollar sign followed by parentheses.
    ```plaintext
    $(whoami)
    ```

### Edge Case: Deprecated Methods

While both methods are valid, the dollar sign method is considered deprecated in some contexts. This is because it can sometimes lead to unexpected behavior or conflicts with shell syntax.

### Real-World Example: CVE-2022-22965

CVE-2022-22965 affected the GitLab container registry, allowing attackers to inject commands and gain unauthorized access. This highlights the importance of proper input validation and sanitization.

---
<!-- nav -->
[[09-Understanding the Vulnerability|Understanding the Vulnerability]] | [[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/00-Overview|Overview]] | [[Web Security (PortSwigger)/10-OS Command Injection/06-Lab 5 Blind OS command injection with out of band data exfiltration/11-Conclusion|Conclusion]]
