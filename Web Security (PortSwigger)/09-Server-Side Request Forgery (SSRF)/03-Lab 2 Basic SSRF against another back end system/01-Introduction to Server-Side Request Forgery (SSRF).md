---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Introduction to Server-Side Request Forgery (SSRF)

Server-Side Request Forgery (SSRF) is a type of web security vulnerability that allows an attacker to induce the server-side application to make HTTP requests to an arbitrary domain of the attacker’s choosing. This can lead to unauthorized access to internal systems, sensitive data exposure, and even remote code execution. SSRF vulnerabilities arise due to improper validation and sanitization of user input used in server-side requests.

### What is SSRF?

SSRF occurs when an application takes user input and uses it as part of a server-side HTTP request. If the input is not properly validated, an attacker can manipulate the request to target internal systems or other external resources. This can result in unauthorized access to internal networks, sensitive data exposure, and even remote code execution.

### Why Does SSRF Matter?

SSRF is significant because it can bypass network segmentation and firewalls, allowing attackers to access internal systems that are not directly exposed to the internet. This can lead to severe consequences such as data exfiltration, service disruption, and even full compromise of internal systems.

### How Does SSRF Work Under the Hood?

When an application accepts user input and uses it to construct an HTTP request, it typically follows these steps:

1. **User Input**: The attacker provides input that will be used in the HTTP request.
2. **Request Construction**: The application constructs the HTTP request using the provided input.
3. **Request Execution**: The server executes the HTTP request, potentially targeting internal systems or other resources.

If the input is not properly validated, the attacker can manipulate the request to target internal systems or other external resources.

### Real-World Example: CVE-2021-21972

A notable example of SSRF is CVE-2021-21972, which affected the Jenkins Continuous Integration server. The vulnerability allowed attackers to perform SSRF attacks by manipulating the `Jenkins.instance.getComputer("master").call()` method. This could be exploited to read arbitrary files from the server, leading to potential data exfiltration and further exploitation.

### Common Pitfalls Without Proper Validation

Without proper validation and sanitization, SSRF can lead to several issues:

- **Data Exfiltration**: Attackers can read sensitive data from internal systems.
- **Service Disruption**: Internal services can be disrupted by unauthorized requests.
- **Remote Code Execution**: In some cases, SSRF can be chained with other vulnerabilities to achieve remote code execution.

### How to Prevent / Defend Against SSRF

To prevent SSRF, it is crucial to implement proper validation and sanitization of user input used in server-side requests. Here are some key strategies:

1. **Input Validation**: Ensure that user input is strictly validated to only allow expected formats and values.
2. **Whitelisting**: Use whitelisting to restrict the domains that can be targeted by server-side requests.
3. **Network Segmentation**: Implement network segmentation to limit the scope of internal systems that can be accessed.
4. **Monitoring and Logging**: Monitor and log server-side requests to detect and respond to suspicious activity.

### Complete Example: Basic SSRF Lab

Let's walk through a complete example of a basic SSRF lab, similar to the one described in the transcript chunk.

#### Lab Setup

The lab environment includes a web application with a stock check feature that fetches data from an internal system. The goal is to use the stock check functionality to scan the internal IP range for an admin interface on port 8080 and then delete the user Carlos.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path for SSRF.
6. Choose the lab titled "Basic SSRF against another backend system."

#### Vulnerable Feature Analysis

The vulnerable feature in this lab is the stock check functionality. The application takes user input to construct an HTTP request to an internal system. If the input is not properly validated, an attacker can manipulate the request to target internal systems.

#### Step-by-Step Exploitation

1. **Identify the Vulnerable Parameter**:
   - Use Burp Suite to intercept the HTTP request sent by the stock check functionality.
   - Identify the parameter that is used to construct the HTTP request.

2. **Craft the Malicious Request**:
   - Modify the intercepted request to target the internal IP range.
   - Set the target IP to `192.168.0.1` and the port to `8080`.

```http
POST /stock-check HTTP/1.1
Host: vulnerable-app.example.com
Content-Type: application/x-www-form-urlencoded

stockId=192.168.0.1:8080
```

3. **Scan the Internal IP Range**:
   - Send the modified request to scan the internal IP range.
   - Observe the responses to identify the admin interface.

4. **Exploit the Admin Interface**:
   - Once the admin interface is identified, use it to delete the user Carlos.
   - Craft the necessary request to interact with the admin interface.

```http
POST /admin/delete-user HTTP/1.1
Host: 192.168.0.1:8080
Content-Type: application/x-www-form-urlencoded

username=Carlos
```

#### Full HTTP Request and Response

Here is the complete HTTP request and response for the stock check functionality:

```http
POST /stock-check HTTP/1.1
Host: vulnerable-app.example.com
Content-Type: application/x-www-form-urlencoded

stockId=192.168.0.1:8080

HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 102

{
  "status": "success",
  "message": "Stock check successful"
}
```

#### Secure Coding Fix

To prevent SSRF, the application should validate and sanitize the user input used in server-side requests. Here is an example of a secure coding fix:

```python
import re

def stock_check(stock_id):
    # Validate the input to ensure it only contains valid characters
    if not re.match(r'^[a-zA-Z0-9.-]+$', stock_id):
        return "Invalid input"

    # Construct the HTTP request with the validated input
    url = f"http://{stock_id}/stock-check"
    response = requests.get(url)

    return response.json()
```

#### Detection and Prevention

To detect and prevent SSRF, implement the following measures:

1. **Input Validation**: Validate user input to ensure it only contains expected characters and formats.
2. **Whitelisting**: Restrict the domains that can be targeted by server-side requests.
3. **Network Segmentation**: Implement network segmentation to limit the scope of internal systems that can be accessed.
4. **Monitoring and Logging**: Monitor and log server-side requests to detect and respond to suspicious activity.

### Conclusion

Server-Side Request Forgery (SSRF) is a critical web security vulnerability that can lead to severe consequences if not properly mitigated. By understanding the underlying mechanisms, implementing proper validation and sanitization, and following best practices for detection and prevention, organizations can effectively defend against SSRF attacks.

### Hands-On Practice

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for practicing SSRF and other web security vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.

These labs provide real-world scenarios and challenges to help you master the concepts and techniques discussed in this chapter.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/03-Lab 2 Basic SSRF against another back end system/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/03-Lab 2 Basic SSRF against another back end system/02-Practice Questions & Answers|Practice Questions & Answers]]
