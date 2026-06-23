---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Crafting Command Injection Payloads

### Common Shell Meta Characters

When crafting command injection payloads, several shell meta characters are commonly used:

- **`;` (Semicolon)**: Used to separate commands in Unix-based systems.
- **`&` (Ampersand)**: Used to run commands in the background in Unix-based systems.
- **`|` (Pipe)**: Used to pass the output of one command as input to another command.
- **`&&` (Double Ampersand)**: Used to run the second command only if the first command succeeds.
- **`||` (Double Pipe)**: Used to run the second command only if the first command fails.
- **`\n` (New Line)**: Used to separate commands in Windows systems.
- **`` ` `` (Backtick)**: Used for inline execution of commands in Unix-based systems.
- **`$()` (Dollar Parentheses)**: Used for inline execution of commands in Unix-based systems.

### Example Payloads

Here are some example payloads that demonstrate the use of these meta characters:

- **Using Semicolon (`;`)**:
  ```bash
  ls ; echo "Command Injection Successful"
  ```
- **Using Ampersand (`&`)**:
  ```bash
  ls & echo "Command Injection Successful"
  ```
- **Using Pipe (`|`)**:
  ```bash
  ls | grep "injection"
  ```
- **Using Double Ampersand (`&&`)**:
  ```bash
  ls && echo "Command Injection Successful"
  ```
- **Using Double Pipe (`||`)**:
  ```bash
  ls || echo "Command Injection Failed"
  ```
- **Using New Line (`\n`)**:
  ```bash
  ls\necho "Command Injection Successful"
  ```
- **Using Backtick (` `)**:
  ```bash
  ls `echo "injection"`
  ```
- **Using Dollar Parentheses ($())**:
  ```bash
  ls $(echo "injection")
  ```

### Real-World Examples

#### CVE-2021-21972

In 2021, a command injection vulnerability was discovered in the Jenkins plugin for GitLab. The vulnerability allowed attackers to inject arbitrary commands into the Jenkins environment. The payload used a semicolon to chain commands:

```bash
gitlab-ci-token; echo "Command Injection Successful"
```

This resulted in unauthorized access to the Jenkins environment and potential data theft.

#### CVE-2020-14882

Another example is the command injection vulnerability in the Apache Struts framework. Attackers could inject commands using the `#` character to bypass input validation:

```bash
${#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Test', 'Command Injection')}
```

This led to unauthorized access and potential remote code execution.

---
<!-- nav -->
[[08-Blacklist vs. Whitelist Validation|Blacklist vs. Whitelist Validation]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[10-Detailed Example Vulnerable vs. Secure Code|Detailed Example Vulnerable vs. Secure Code]]
