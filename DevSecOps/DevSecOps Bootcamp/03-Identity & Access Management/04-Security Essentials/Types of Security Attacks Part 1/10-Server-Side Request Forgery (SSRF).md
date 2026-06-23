---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Server-Side Request Forgery (SSRF)

### Introduction

Server-Side Request Forgery (SSRF) is a type of attack where an attacker tricks a server into making unintended requests to other services or resources on behalf of the attacker. This can lead to unauthorized access to sensitive data, internal network scanning, and even remote code execution. SSRF attacks exploit vulnerabilities in the server-side logic, often due to insufficient input validation or improper handling of user-supplied data.

### Understanding the Attack Vector

In a typical scenario, a server communicates with various backend services such as databases, storage systems, and other web servers. These services might be running on the same machine or on different machines within the same network. When an attacker gains control over the server's identity, they can impersonate the server and make requests to these backend services. This allows the attacker to access sensitive resources that are typically restricted to the server itself.

#### Example Scenario

Consider a web application that allows users to fetch images from external URLs. The server takes the URL provided by the user and makes an HTTP request to that URL to retrieve the image. If the server does not properly validate the URL, an attacker could provide a URL that points to an internal resource, such as `http://localhost:8080/admin`. The server would then make a request to this internal URL, potentially exposing sensitive information.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of an SSRF attack is the CVE-2021-21972 vulnerability in VMware vCenter Server. This vulnerability allowed attackers to perform SSRF attacks, leading to unauthorized access to internal network resources. Another example is the CVE-2020-14882 vulnerability in Jenkins, which allowed attackers to perform SSRF attacks and potentially execute arbitrary commands on the server.

### Detailed Mechanics

To understand how SSRF attacks work, let's break down the process step-by-step:

1. **User Input**: The attacker provides a malicious URL to the server.
2. **Server Processing**: The server processes the URL and makes an HTTP request to the specified location.
3. **Resource Access**: Depending on the URL, the server might access internal resources, such as `http://localhost`, `http://internal-service`, or `http://127.0.0.1`.

#### Example Code

Here is a simplified example of a vulnerable code snippet:

```python
import requests

def fetch_image(url):
    response = requests.get(url)
    return response.content

# Vulnerable usage
user_input_url = "http://localhost:8080/admin"
image_data = fetch_image(user_input_url)
```

In this example, the `fetch_image` function takes a URL as input and makes an HTTP GET request to that URL. If the user provides a URL pointing to an internal resource, the server will make a request to that resource, potentially exposing sensitive information.

### How SSRF Works Under the Hood

When a server makes an HTTP request, it sends a series of headers and a request body to the target server. The target server then responds with a status code, headers, and a response body. In the case of SSRF, the attacker manipulates the server to make requests to unintended targets, often internal resources.

#### Full HTTP Request and Response

Here is an example of a full HTTP request and response:

```http
GET /admin HTTP/1.1
Host: localhost:8080
User-Agent: Python-urllib/3.8
Accept-Encoding: gzip, deflate
Connection: close

HTTP/1.1 200 OK
Date: Mon, 27 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
<title>Admin Page</title>
</head>
<body>
<h1>Welcome to the Admin Page</h1>
<p>This page contains sensitive information.</p>
</body>
</html>
```

In this example, the server makes a request to `http://localhost:8080/admin`, and the response contains sensitive information that should not be accessible to the attacker.

### Common Pitfalls

There are several common pitfalls that can lead to SSRF vulnerabilities:

1. **Insufficient Input Validation**: Failing to validate user-supplied URLs can allow attackers to craft malicious requests.
2. **Improper Handling of Internal Resources**: Allowing the server to access internal resources based on user input can expose sensitive information.
3. **Lack of Network Segmentation**: Not properly segmenting the network can allow attackers to scan and access internal resources.

### How to Prevent / Defend

To prevent SSRF attacks, it is essential to implement proper input validation, restrict access to internal resources, and monitor network traffic. Here are some specific steps:

1. **Input Validation**: Validate user-supplied URLs to ensure they point to trusted external resources.
2. **Restrict Access**: Restrict the server's ability to access internal resources based on user input.
3. **Network Segmentation**: Properly segment the network to limit the scope of potential attacks.
4. **Monitoring and Logging**: Monitor network traffic and log suspicious activity to detect potential SSRF attacks.

#### Secure Code Fix

Here is an example of a secure code fix:

```python
import requests
from urllib.parse import urlparse

def fetch_image(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https'] or parsed_url.hostname == 'localhost':
        raise ValueError("Invalid URL")
    response = requests.get(url)
    return response.content

# Secure usage
user_input_url = "http://example.com/image.jpg"
try:
    image_data = fetch_image(user_input_url)
except ValueError as e:
    print(e)
```

In this example, the `fetch_image` function validates the URL to ensure it points to a trusted external resource. If the URL is invalid, the function raises an error.

### Detection and Prevention

To detect and prevent SSRF attacks, you can use various tools and techniques:

1. **Static Analysis Tools**: Use static analysis tools to identify potential SSRF vulnerabilities in your codebase.
2. **Dynamic Analysis Tools**: Use dynamic analysis tools to simulate SSRF attacks and identify potential vulnerabilities.
3. **Network Monitoring Tools**: Use network monitoring tools to detect suspicious activity and potential SSRF attacks.

#### Example Tools

- **Static Analysis Tools**: SonarQube, Fortify
- **Dynamic Analysis Tools**: Burp Suite, OWASP ZAP
- **Network Monitoring Tools**: Wireshark, Splunk

### Hands-On Labs

To practice and understand SSRF attacks, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive SSRF module with interactive challenges.
- **OWASP Juice Shop**: Contains SSRF vulnerabilities that you can exploit and learn from.
- **DVWA**: Provides a vulnerable web application with SSRF vulnerabilities that you can test and fix.

By practicing in these environments, you can gain a deeper understanding of SSRF attacks and how to defend against them.

### Conclusion

Server-Side Request Forgery (SSRF) is a serious security threat that can lead to unauthorized access to sensitive resources. By understanding the mechanics of SSRF attacks, implementing proper input validation, restricting access to internal resources, and using monitoring tools, you can effectively prevent and detect SSRF attacks.

---
<!-- nav -->
[[09-Server Request Forgery (SRF)|Server Request Forgery (SRF)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[11-Session ID and Token Revocation|Session ID and Token Revocation]]
