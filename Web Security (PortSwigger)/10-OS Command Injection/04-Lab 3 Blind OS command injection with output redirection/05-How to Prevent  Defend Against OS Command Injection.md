---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## How to Prevent / Defend Against OS Command Injection

### Secure Coding Practices

To prevent OS command injection, it is crucial to follow secure coding practices. This includes validating and sanitizing user input before passing it to the operating system.

#### Example of Secure Code

```python
import requests
import shlex

def safe_execute_command(command):
    safe_command = shlex.split(command)
    return safe_command

url = "http://example.com/feedback"
data = {
    "email": "test@example.com",
    "message": "Test message"
}

safe_command = safe_execute_command(data["email"])
response = requests.post(url, data=safe_command)
print(response.text)
```

### Input Validation

Input validation is essential to ensure that user input does not contain malicious commands. This can be achieved by using regular expressions or other validation techniques.

#### Example of Input Validation

```python
import re

def validate_input(input):
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", input):
        return True
    return False

url = "http://example.

---
<!-- nav -->
[[04-Finding the Output Location|Finding the Output Location]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/00-Overview|Overview]] | [[06-Lab Setup Blind OS Command Injection with Output Redirection|Lab Setup Blind OS Command Injection with Output Redirection]]
