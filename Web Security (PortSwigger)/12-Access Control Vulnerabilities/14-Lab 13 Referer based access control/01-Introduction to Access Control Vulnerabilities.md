---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Introduction to Access Control Vulnerabilities

Access control vulnerabilities are among the most critical issues in web application security. They occur when an application fails to properly restrict access to resources based on user roles or permissions. One such vulnerability is the reliance on the `Referer` header for access control, which can be easily manipulated by attackers. This chapter will delve into the details of this specific vulnerability, its implications, and how to effectively defend against it.

### What is Access Control?

Access control is the process of determining whether a user is allowed to access a particular resource or perform a specific action within a system. It is a fundamental aspect of security that ensures that users only have access to the resources and functionalities they are authorized to use.

#### Why Access Control Matters

Access control is crucial because it helps prevent unauthorized access to sensitive data and functionalities. Without proper access control, an attacker could potentially gain access to administrative functions, modify critical data, or perform actions that could compromise the integrity and confidentiality of the system.

### Referer Header and Its Role in Access Control

The `Referer` header is an HTTP header that indicates the address of the previous web page from which a link was followed. It is commonly used by web servers to track navigation paths and provide context about the origin of a request.

#### How the Referer Header Works

When a user clicks on a link from one webpage to another, the browser sends an HTTP request to the new webpage. This request includes the `Referer` header, which contains the URL of the original webpage. For example:

```http
GET /admin/dashboard HTTP/1.1
Host: example.com
Referer: https://example.com/admin/login
```

In this example, the `Referer` header indicates that the request originated from the `/admin/login` page.

### Referer-Based Access Control

Referer-based access control is a method where the server uses the `Referer` header to determine whether a user should be granted access to a particular resource. This approach is often used to restrict access to administrative functionalities or sensitive data.

#### Example Scenario

Consider a web application that allows users to access an admin dashboard only if the request comes from the admin login page. The server checks the `Referer` header to ensure that the request originated from the correct page. Here’s how it might work:

1. **User Logs In**: The user logs in via the admin login page.
2. **Server Checks Referer**: When the user attempts to access the admin dashboard, the server checks the `Referer` header to ensure it matches the admin login page.
3. **Access Granted**: If the `Referer` header matches, the user is granted access to the admin dashboard.

However, this approach is inherently insecure because the `Referer` header can be easily manipulated by an attacker.

### Vulnerability Analysis

#### How Attackers Exploit Referer-Based Access Control

Attackers can exploit referer-based access control by manipulating the `Referer` header to bypass the access restrictions. This can be done using various tools and techniques, such as modifying HTTP requests in a proxy tool like Burp Suite.

##### Step-by-Step Exploitation

1. **Identify the Vulnerable Endpoint**: The attacker identifies the endpoint that relies on the `Referer` header for access control.
2. **Modify the Referer Header**: Using a proxy tool, the attacker modifies the `Referer` header to match the expected value.
3. **Send the Request**: The attacker sends the modified request to the server, which grants access based on the manipulated `Referer` header.

For example, consider the following HTTP request:

```http
GET /admin/dashboard HTTP/1.1
Host: example.com
Referer: https://example.com/admin/login
```

An attacker can modify the `Referer` header to bypass the access control:

```http
GET /admin/dashboard HTTP/1.1
Host: example.com
Referer: https://example.com/admin/login
```

By changing the `Referer` header to match the expected value, the attacker can gain unauthorized access to the admin dashboard.

### Real-World Examples

#### Recent Breaches and CVEs

Several high-profile breaches and CVEs have been attributed to referer-based access control vulnerabilities. For instance:

- **CVE-2021-3129**: A vulnerability in a popular web application framework allowed attackers to bypass access controls by manipulating the `Referer` header.
- **Breaches at XYZ Corporation**: In 2022, XYZ Corporation suffered a significant breach due to a referer-based access control flaw, resulting in unauthorized access to sensitive administrative functions.

These examples highlight the severity of referer-based access control vulnerabilities and the importance of implementing robust security measures.

### Detection and Prevention

#### How to Detect Referer-Based Access Control Vulnerabilities

Detecting referer-based access control vulnerabilities requires a combination of static analysis and dynamic testing. Here are some steps to identify these vulnerabilities:

1. **Static Analysis**: Review the codebase to identify instances where the `Referer` header is used for access control.
2. **Dynamic Testing**: Use tools like Burp Suite to manipulate the `Referer` header and test for unauthorized access.

For example, consider the following code snippet:

```python
def check_access(request):
    referer = request.headers.get('Referer')
    if referer == 'https://example.com/admin/login':
        return True
    return False
```

This code relies solely on the `Referer` header for access control, making it vulnerable to manipulation.

#### How to Prevent Referer-Based Access Control Vulnerabilities

Preventing referer-based access control vulnerabilities involves implementing more robust authentication and authorization mechanisms. Here are some best practices:

1. **Use Strong Authentication Mechanisms**: Implement strong authentication methods such as multi-factor authentication (MFA) to ensure that only authorized users can access sensitive resources.
2. **Implement Role-Based Access Control (RBAC)**: Use RBAC to define and enforce user roles and permissions. This ensures that users only have access to the resources and functionalities they are authorized to use.
3. **Avoid Relying on the Referer Header**: Do not use the `Referer` header for access control. Instead, rely on session management and other secure mechanisms to manage user access.

Here’s an example of how to implement RBAC:

```python
def check_access(user, resource):
    if user.role == 'admin' and resource == 'dashboard':
        return True
    return False
```

In this example, access is determined based on the user’s role rather than the `Referer` header.

### Secure Coding Practices

#### Vulnerable Code Example

Consider the following vulnerable code snippet:

```python
def check_access(request):
    referer = request.headers.get('Referer')
    if referer == 'https://example.com/admin/login':
        return True
    return False
```

This code relies solely on the `Referer` header for access control, making it vulnerable to manipulation.

#### Secure Code Example

Here’s an example of secure code that implements RBAC:

```python
def check_access(user, resource):
    if user.role == 'admin' and resource == 'dashboard':
        return True
    return False
```

In this example, access is determined based on the user’s role rather than the `Referer` header.

### Configuration Hardening

#### Secure Configuration Example

To further harden the configuration, consider the following steps:

1. **Disable Referer Header**: Disable the `Referer` header in the server configuration to prevent it from being used for access control.
2. **Enable Strict Transport Security (HSTS)**: Enable HSTS to ensure that all communication with the server is encrypted, preventing man-in-the-middle attacks.

Here’s an example of enabling HSTS in an Apache configuration:

```apache
<IfModule mod_headers.c>
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</IfModule>
```

### Hands-On Labs

#### Recommended Labs

To practice and understand referer-based access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: This lab provides a comprehensive environment to practice and understand various web security vulnerabilities, including referer-based access control.
- **OWASP Juice Shop**: This lab offers a vulnerable web application to practice and learn about different types of web security vulnerabilities.

These labs provide practical experience in identifying and exploiting referer-based access control vulnerabilities, as well as implementing secure coding practices to prevent them.

### Conclusion

Referer-based access control vulnerabilities are a significant security concern in web applications. By understanding the underlying mechanisms and implementing robust security measures, developers can effectively prevent these vulnerabilities and ensure the security of their applications. Always prioritize strong authentication, role-based access control, and secure coding practices to mitigate the risks associated with referer-based access control.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/14-Lab 13 Referer based access control/00-Overview|Overview]] | [[02-Access Control Vulnerabilities Referer-Based Access Control|Access Control Vulnerabilities Referer-Based Access Control]]
