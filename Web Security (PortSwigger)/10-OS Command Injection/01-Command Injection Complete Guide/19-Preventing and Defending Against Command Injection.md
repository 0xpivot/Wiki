---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Preventing and Defending Against Command Injection

### Secure Coding Practices

The primary defense against command injection is secure coding practices. Ensure that user input is properly sanitized and validated before being used in system commands.

### Sanitizing User Input

Sanitize user input by removing or escaping characters that could be used for command injection. For example, replace semicolons with empty strings or escape them.

### Example of Sanitizing User Input

Here’s an example in Python:

```python
import re

def sanitize_input(user_input):
    # Remove semicolons and other dangerous characters
    sanitized_input = re.sub(r'[;&|`$]', '', user_input)
    return sanitized_input

user_input = "ls ; echo 'Command Injection'"
sanitized_input = sanitize_input(user_input)
print(sanitized_input)  # Output: "ls  echo 'Command Injection'"
```

### Using Safe APIs

Use safe APIs that do not allow direct execution of system commands. For example, instead of using `os.system()`, use higher-level functions like `subprocess.run()` with the `shell=False` option.

### Example of Using Safe APIs

Here’s an example in Python:

```python
import subprocess

def list_files(directory):
    try:
        result = subprocess.run(['ls', directory], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

directory = "/path/to/directory"
list_files(directory)
```

### Detection and Monitoring

Regularly monitor your application for signs of command injection attempts. Use intrusion detection systems (IDS) and security information and event management (SIEM) tools to detect and respond to suspicious activities.

### Example of IDS Configuration

Here’s an example of configuring an IDS rule to detect command injection attempts:

```json
{
  "rule": {
    "id": "command-injection",
    "description": "Detects command injection attempts",
    "condition": "payload contains ';'",
    "action": "alert"
  }
}
```

### Hardening the Environment

Harden the environment by limiting the permissions of the application user. Ensure that the application runs with the least privilege necessary to perform its tasks.

### Example of Limiting Permissions

Here’s an example of setting up a restricted user in Linux:

```bash
sudo useradd -r -s /sbin/nologin -c "Restricted User" restricted_user
sudo chown restricted_user:restricted_user /path/to/application
```

---
<!-- nav -->
[[18-Practical Examples and Scenarios|Practical Examples and Scenarios]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[20-Understanding the Context of OS Command Injection|Understanding the Context of OS Command Injection]]
