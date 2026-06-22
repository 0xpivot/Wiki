---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Introduction to Access Control Vulnerabilities

Access control vulnerabilities are among the most critical issues in web application security. They occur when an application fails to properly restrict access to resources based on user roles or permissions. One specific type of access control vulnerability is when sensitive information is leaked through the manipulation of request parameters, particularly in the context of redirects. This chapter will delve deep into the concept of access control vulnerabilities, focusing on the scenario where the User ID is controlled by a request parameter, leading to data leakage and insecure redirects.

### Background Theory

Access control is a fundamental aspect of web application security. It ensures that users can only access resources and perform actions that they are authorized to do. Access control mechanisms typically involve authentication (verifying the identity of a user) and authorization (granting or denying access based on the user’s role).

In a typical web application, access control is implemented using various methods such as session management, role-based access control (RBAC), and attribute-based access control (ABAC). However, if these mechanisms are not properly enforced, attackers can exploit vulnerabilities to gain unauthorized access to sensitive information.

### Real-World Examples

Recent real-world examples of access control vulnerabilities include:

1. **CVE-2021-21972**: A vulnerability in Microsoft Exchange Server allowed attackers to bypass access controls and execute arbitrary code. This led to widespread exploitation and significant damage.
   
2. **CVE-2020-14882**: A vulnerability in the Atlassian Jira software allowed attackers to bypass access controls and view sensitive data. This was due to improper validation of user input.

These examples highlight the importance of robust access control mechanisms and the severe consequences of their failure.

### Lab Setup

To understand and practice the concepts discussed in this chapter, we will use the Web Security Academy provided by PortSwigger. The lab titled "User ID controlled by request parameter with data leakage in redirect" is designed to demonstrate a specific access control vulnerability.

#### Accessing the Lab

1. Visit the URL: `https://portswigger.net/web-security`.
2. Click on the "Sign Up" button to create an account.
3. Once logged in, navigate to the "Academy".
4. Select the "Learning Path" and choose the "Access Control" module.
5. Find and open "Lab Number Nine".

### Understanding the Vulnerability

The vulnerability in this lab involves an access control issue where sensitive information is leaked through the manipulation of a request parameter used in a redirect. Specifically, the User ID is controlled by a request parameter, and this parameter can be manipulated to leak sensitive data.

#### Scenario Overview

The goal of the lab is to obtain the API key for the user "Carlos". This is achieved by exploiting the access control vulnerability to manipulate the User ID parameter and trigger a redirect that leaks sensitive information.

### Detailed Explanation

#### Step-by-Step Mechanics

1. **Identify the Vulnerable Parameter**:
   - The first step is to identify the parameter that controls the User ID. This is typically done by analyzing the HTTP requests and responses.
   - Example HTTP request:
     ```http
     GET /profile?userId=123 HTTP/1.1
     Host: vulnerable-app.com
     ```

2. **Manipulate the Parameter**:
   - By changing the value of the `userId` parameter, you can attempt to access different user profiles.
   - Example HTTP request with manipulated parameter:
     ```http
     GET /profile?userId=456 HTTP/1.1
     Host: vulnerable-app.com
     ```

3. **Trigger the Redirect**:
   - The application may respond with a redirect to another page, which could contain sensitive information.
   - Example HTTP response:
     ```http
     HTTP/1.1 302 Found
     Location: /api?key=abc123
     ```

4. **Extract the Sensitive Information**:
   - The redirect URL may contain sensitive information such as an API key.
   - Example extracted information:
     ```plaintext
     API Key: abc123
     ```

### Real-World Example: Data Leakage via Redirect

A real-world example of this vulnerability occurred in a popular e-commerce platform. Attackers discovered that by manipulating the `userId` parameter in a redirect request, they could access other users' order details. This led to a significant data breach.

#### HTTP Request and Response

Here is a detailed example of the HTTP request and response involved in this vulnerability:

```http
GET /profile?userId=456 HTTP/1.1
Host: vulnerable-app.com
Cookie: session_id=abc123

HTTP/1.1 302 Found
Location: /api?key=def456
```

In this example, the attacker manipulates the `userId` parameter to `456`, triggering a redirect that includes the API key in the URL.

### How to Prevent / Defend

#### Detection

To detect access control vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.

These tools can help identify patterns in HTTP requests and responses that indicate potential access control issues.

#### Prevention

To prevent access control vulnerabilities, follow these best practices:

1. **Proper Input Validation**:
   - Ensure that all input parameters are validated and sanitized to prevent manipulation.
   - Example secure code:
     ```python
     def get_user_profile(user_id):
         if not isinstance(user_id, int):
             raise ValueError("Invalid user ID")
         # Fetch user profile from database
     ```

2. **Role-Based Access Control (RBAC)**:
   - Implement RBAC to ensure that users can only access resources based on their roles.
   - Example secure code:
     ```python
     def check_access(user_id, required_role):
         user = get_user(user_id)
         if user.role != required_role:
             raise PermissionError("Insufficient privileges")
         return True
     ```

3. **Secure Redirects**:
   - Avoid including sensitive information in redirect URLs.
   - Example secure code:
     ```python
     def redirect_to_api(user_id):
         if not check_access(user_id, "admin"):
             raise PermissionError("Insufficient privileges")
         api_key = get_api_key(user_id)
         return f"/api?key={api_key}"
     ```

### Secure Coding Fixes

Here is a comparison between the vulnerable and secure versions of the code:

#### Vulnerable Code

```python
def get_user_profile(user_id):
    user = get_user(user_id)
    return f"/profile?userId={user.id}"

def redirect_to_api(user_id):
    api_key = get_api_key(user_id)
    return f"/api?key={api_key}"
```

#### Secure Code

```python
def get_user_profile(user_id):
    if not isinstance(user_id, int):
        raise ValueError("Invalid user ID")
    user = get_user(user_id)
    return f"/profile?userId={user.id}"

def redirect_to_api(user_id):
    if not check_access(user_id, "admin"):
        raise PermissionError("Insufficient privileges")
    api_key = get_api_key(user_id)
    return f"/api?key={api_key}"
```

### Configuration Hardening

To further harden the application against access control vulnerabilities, consider the following configuration changes:

1. **Session Management**:
   - Ensure that sessions are securely managed and invalidated after a certain period of inactivity.
   - Example configuration:
     ```nginx
     http {
         ...
         session_timeout 30m;
         ...
     }
     ```

2. **Input Filtering**:
   - Configure web servers and application frameworks to filter out potentially malicious input.
   - Example configuration:
     ```nginx
     http {
         ...
         set $valid_user_id 0;
         if ($arg_userId ~ ^[0-9]+$) {
             set $valid_user_id 1;
         }
         ...
     }
     ```

### Common Pitfalls

When dealing with access control vulnerabilities, some common pitfalls to avoid include:

1. **Overlooking Input Validation**:
   - Always validate and sanitize input parameters to prevent manipulation.
   
2. **Improper Role-Based Access Control**:
   - Ensure that RBAC is correctly implemented and enforced across all parts of the application.
   
3. **Sensitive Information in Redirects**:
   - Avoid including sensitive information in redirect URLs to prevent data leakage.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs, including the one discussed in this chapter.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another popular choice for practicing web application security.

By thoroughly understanding and practicing the concepts discussed in this chapter, you will be better equipped to identify and mitigate access control vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/10-Lab 9 User ID controlled by request parameter with data leakage in redirect/00-Overview|Overview]] | [[02-Access Control Vulnerabilities User ID Controlled by Request Parameter with Data Leakage in Redirect|Access Control Vulnerabilities User ID Controlled by Request Parameter with Data Leakage in Redirect]]
