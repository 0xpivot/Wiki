---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## OS Command Injection with Time Delays

### Introduction to OS Command Injection

OS Command Injection is a type of security vulnerability that occurs when an application executes operating system commands that include untrusted input from users. This can lead to unauthorized access, data theft, or even complete system compromise. The core issue arises when user input is not properly sanitized or validated before being used in a command execution context.

#### Why Does OS Command Injection Matter?

Command injection vulnerabilities are critical because they allow attackers to execute arbitrary commands on the server. This can result in severe consequences such as:

- **Data Theft**: Accessing sensitive information stored on the server.
- **System Compromise**: Gaining full control over the server, leading to further attacks.
- **Denial of Service (DoS)**: Disrupting the normal operation of the server.

### Understanding the `sleep` Command

The `sleep` command is a simple yet powerful tool used in command injection attacks. It pauses the execution of a command for a specified duration, typically measured in seconds. This delay can be used to determine whether a command injection vulnerability exists.

#### Syntax of the `sleep` Command

```bash
sleep <duration>
```

Where `<duration>` is the number of seconds to wait before proceeding with the next command.

#### Example Usage

If you run the following command:

```bash
sleep 10; echo "Hello, World!"
```

The system will pause for 10 seconds before printing "Hello, World!" to the console.

### Using `sleep` for Blind Command Injection Detection

Blind OS command injection refers to scenarios where the attacker does not receive direct feedback from the injected command. Instead, they rely on indirect indicators, such as time delays, to infer the success of their attack.

#### Steps to Detect Vulnerability

1. **Identify Input Fields**: Determine which fields in the application accept user input.
2. **Inject `sleep` Command**: Insert a `sleep` command into the input field to introduce a delay.
3. **Observe Response Time**: Check if the response time increases significantly, indicating that the `sleep` command was executed.

### Example Scenario

Consider an application that allows users to submit a form with fields like `name` and `email`. The application might construct a command using these inputs.

#### Vulnerable Code Example

```python
import subprocess

def process_form(name, email):
    command = f"echo {name} | mail -s 'New Submission' {email}"
    subprocess.run(command, shell=True)
```

#### Injecting the `sleep` Command

To test for command injection, inject the `sleep` command into the `name` field:

```bash
name="sleep 10; "
```

This would result in the following command:

```bash
echo sleep 10; | mail -s 'New Submission' user@example.com
```

If the application is vulnerable, the `sleep 10;` command will be executed, causing a 10-second delay before sending the email.

### Testing the `name` Field

1. **Input the Payload**:
   ```bash
   name="sleep 10; "
   ```

2. **URL Encode the Payload**:
   ```bash
   name=%22sleep+10%3B+%22
   ```

3. **Send the Request**:
   ```http
   POST /submit-form HTTP/1.1
   Host: example.com
   Content-Type: application/x-www-form-urlencoded

   name=%22sleep+10%3B+%22&email=user@example.com
   ```

4. **Observe the Response**:
   - If the response is immediate, the `name` field is not vulnerable.
   - If there is a significant delay, the `name` field is likely vulnerable.

### Testing the `email` Field

Repeat the same steps for the `email` field:

1. **Input the Payload**:
   ```bash
   email="sleep 10; "
   ```

2. **URL Encode the Payload**:
   ```bash
   email=%22sleep+10%3B+%22
   ```

3. **Send the Request**:
   ```http
   POST /submit-form HTTP/1.1
   Host: example.com
   Content-Type: application/x-www-form-urlencoded

   name=JohnDoe&email=%22sleep+10%3B+%22
   ```

4. **Observe the Response**:
   - If there is a significant delay, the `email` field is vulnerable.

### Real-World Examples

#### CVE-2021-21972: Apache Struts Command Injection

In 2021, a critical vulnerability was discovered in Apache Struts, allowing remote code execution through command injection. Attackers could inject malicious commands into input fields, leading to full system compromise.

#### CVE-2022-22965: Spring Framework RCE

Another notable example is the Spring Framework vulnerability, where attackers could inject commands into input parameters, leading to remote code execution.

### How to Prevent / Defend Against OS Command Injection

#### Secure Coding Practices

1. **Avoid Shell Execution**: Use safer alternatives like subprocess modules that do not invoke the shell.
2. **Sanitize Inputs**: Validate and sanitize all user inputs to ensure they do not contain malicious characters.
3. **Use Parameterized Queries**: Where possible, use parameterized queries or prepared statements to avoid direct command execution.

#### Example of Secure Code

```python
import subprocess

def process_form(name, email):
    try:
        subprocess.run(["mail", "-s", "New Submission", email], check=True, input=name.encode())
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
```

#### Hardening Measures

1. **Least Privilege Principle**: Run applications with the least privileges necessary.
2. **Input Validation**: Implement robust input validation to filter out potentially harmful characters.
3. **Monitoring and Logging**: Regularly monitor and log application activities to detect unusual behavior.

### Conclusion

OS Command Injection is a serious security threat that can have severe consequences if not properly mitigated. By understanding the mechanisms behind command injection and implementing secure coding practices, developers can significantly reduce the risk of such vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various web security topics, including command injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including command injection, for educational purposes.

By thoroughly understanding and practicing these concepts, you can become proficient in detecting and preventing OS command injection vulnerabilities.

---
<!-- nav -->
[[05-Implementing Time-Based OS Command Injection|Implementing Time-Based OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/00-Overview|Overview]] | [[07-Understanding Time-Based OS Command Injection|Understanding Time-Based OS Command Injection]]
