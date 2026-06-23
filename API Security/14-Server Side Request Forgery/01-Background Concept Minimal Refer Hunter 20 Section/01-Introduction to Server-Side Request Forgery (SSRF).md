---
course: API Security
topic: Server Side Request Forgery
tags: [api-security]
---

## Introduction to Server-Side Request Forgery (SSRF)

Server-Side Request Forgery (SSRF) is a type of web application vulnerability that allows an attacker to induce the server-side application to make HTTP requests to an arbitrary domain of the attacker’s choosing. This can lead to unauthorized access to internal systems, sensitive data exposure, and even remote code execution. In essence, SSRF vulnerabilities arise when an application uses user-supplied input to construct URLs or other network requests without proper validation or sanitization.

### What is SSRF?

SSRF occurs when an application takes user input and uses it to make a request to an external resource, such as a URL or IP address. The vulnerability arises because the application does not properly validate or sanitize the input, allowing an attacker to manipulate the request to target internal resources or other unintended targets.

#### Why Does SSRF Matter?

SSRF can have severe consequences, including:

- **Data Exposure**: An attacker can use SSRF to access internal services that are not exposed to the internet, potentially leading to the exposure of sensitive data.
- **Internal Network Reconnaissance**: By using SSRF, an attacker can map out internal networks, identify open ports, and discover services that may be vulnerable to further attacks.
- **Remote Code Execution**: In some cases, SSRF can be used to exploit other vulnerabilities, such as deserialization flaws, leading to remote code execution.

### How SSRF Works Under the Hood

To understand SSRF, let's break down the typical scenario where this vulnerability can occur:

1. **User Input**: The application accepts user input, often through a form field or query parameter.
2. **URL Construction**: The application uses this input to construct a URL or other network request.
3. **Request Execution**: The application makes the network request using the constructed URL.
4. **Response Handling**: The application processes the response from the network request.

If the application does not properly validate or sanitize the user input, an attacker can manipulate the URL to target internal resources or other unintended targets.

#### Example Scenario

Consider an application that allows users to fetch images from a specified URL:

```python
def fetch_image(url):
    response = requests.get(url)
    return response.content
```

An attacker could supply a URL like `http://localhost/admin` to attempt to access internal administrative interfaces. If the application does not validate the URL, the server will make a request to `http://localhost/admin`, potentially exposing sensitive information.

### Real-World Examples

Several high-profile breaches and vulnerabilities have been attributed to SSRF. Here are a few recent examples:

1. **CVE-2021-21974**: A vulnerability in the Jenkins plugin allowed attackers to perform SSRF attacks, leading to unauthorized access to internal systems.
2. **CVE-2020-14882**: A vulnerability in the Kubernetes API server allowed attackers to perform SSRF attacks, leading to unauthorized access to internal services and potential privilege escalation.

### Detection and Prevention

#### How to Detect SSRF

Detecting SSRF vulnerabilities requires a combination of static analysis, dynamic testing, and manual review. Here are some steps to detect SSRF:

1. **Static Analysis**: Use tools like SonarQube, Fortify, or Veracode to scan your codebase for potential SSRF vulnerabilities.
2. **Dynamic Testing**: Use tools like Burp Suite, ZAP, or OWASP ZAP to test your application for SSRF vulnerabilities.
3. **Manual Review**: Manually review code that constructs URLs or makes network requests to ensure proper validation and sanitization.

#### How to Prevent SSRF

Preventing SSRF requires a multi-layered approach, including secure coding practices, proper validation, and network segmentation.

##### Secure Coding Practices

1. **Input Validation**: Always validate and sanitize user input before using it to construct URLs or make network requests.
2. **Whitelist URLs**: Use a whitelist of allowed domains and IP addresses to restrict the destinations of network requests.
3. **Use Safe Libraries**: Use libraries that provide built-in protection against SSRF, such as `requests` with `proxies` configured.

##### Example of Secure Coding

Here is an example of how to securely handle user input to prevent SSRF:

```python
import re

def fetch_image(url):
    # Validate the URL
    if not re.match(r'^https://example\.com/', url):
        raise ValueError("Invalid URL")
    
    # Make the request
    response = requests.get(url)
    return response.content
```

In this example, we use a regular expression to validate the URL, ensuring that it only points to a specific domain (`example.com`). This prevents an attacker from supplying a URL that targets internal resources.

##### Network Segmentation

1. **Firewall Rules**: Implement firewall rules to restrict outbound traffic from your application servers to only trusted destinations.
2. **Network Isolation**: Use network isolation techniques, such as VLANs or network segments, to isolate your application servers from internal services.

### Common Mistakes and Pitfalls

When dealing with SSRF, there are several common mistakes and pitfalls to avoid:

1. **Assuming Internal Networks are Secure**: Just because a service is not exposed to the internet does not mean it is secure. Internal networks can be vulnerable to SSRF attacks.
2. **Relying Solely on Whitelisting**: While whitelisting is a good practice, it should be combined with other security measures, such as input validation and network segmentation.
3. **Ignoring DNS Rebinding**: DNS rebinding attacks can bypass whitelisting by dynamically changing the IP address associated with a domain name.

### Hands-On Practice

For hands-on practice with SSRF, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive SSRF module with interactive challenges and detailed explanations.
- **OWASP Juice Shop**: Contains several SSRF vulnerabilities that can be exploited and fixed.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of SSRF vulnerabilities that can be tested and mitigated.

By practicing in these environments, you can gain a deeper understanding of how SSRF works and how to effectively defend against it.

### Conclusion

Server-Side Request Forgery (SSRF) is a serious vulnerability that can have significant consequences if left unmitigated. By understanding the underlying mechanisms, detecting potential vulnerabilities, and implementing robust preventive measures, you can protect your applications from SSRF attacks. Always remember to validate and sanitize user input, use safe libraries, and implement network segmentation to minimize the risk of SSRF vulnerabilities.

---
<!-- nav -->
[[API Security/14-Server Side Request Forgery/01-Background Concept Minimal Refer Hunter 20 Section/00-Overview|Overview]] | [[API Security/14-Server Side Request Forgery/01-Background Concept Minimal Refer Hunter 20 Section/02-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]]
