---
course: API Security
topic: Broken Object Level Authorization issues
tags: [api-security]
---

## Introduction to Broken Object Level Authorization (BOLA)

Broken Object Level Authorization (BOLA) is a critical security issue that arises when an application fails to properly restrict access to sensitive objects based on the user's privileges. This vulnerability allows unauthorized users to access or manipulate data that should be restricted to specific roles or identities. Understanding BOLA is essential for securing APIs and ensuring that sensitive data remains protected.

### What is BOLA?

BOLA occurs when an application does not enforce proper authorization checks at the object level. In other words, the application might allow a user to access or modify an object (such as a resource, record, or entity) that they should not have access to. This can lead to unauthorized access, data breaches, and other security risks.

#### Why Does BOLA Matter?

BOLA is significant because it can expose sensitive data to unauthorized users. For example, consider a web application that allows users to view their own profile information. If the application does not properly check the user's identity before displaying the profile, an attacker could potentially access other users' profiles by manipulating the request parameters.

### How Does BOLA Work?

To understand how BOLA works, let's break down the process:

1. **User Authentication**: The user logs into the application and is authenticated.
2. **Request for Data**: The user makes a request to access a specific object (e.g., a user profile).
3. **Authorization Check**: The application checks whether the user is authorized to access the requested object.
4. **Data Retrieval**: If the authorization check passes, the application retrieves and returns the requested data.

In a BOLA scenario, the authorization check is either missing or improperly implemented, allowing unauthorized access to the object.

### Real-World Example: CVE-2021-21972

One real-world example of BOLA is CVE-2021-21972, which affected the popular open-source project Nextcloud. In this case, the application did not properly enforce authorization checks when accessing shared files. An attacker could exploit this vulnerability to access files that were not intended to be shared with them.

#### Impact of CVE-2021-21972

The impact of this vulnerability was severe, as it allowed unauthorized access to sensitive files. This could result in data breaches, intellectual property theft, and other serious consequences.

### Detailed Explanation of BOLA

Let's delve deeper into the mechanics of BOLA using a hypothetical example.

#### Scenario: User Profile Access

Consider a web application that allows users to view their own profile information. The application uses a simple URL structure to identify the user's profile:

```
https://example.com/profile/<user_id>
```

Here, `<user_id>` is a unique identifier for each user.

#### Vulnerable Code Example

Suppose the application uses the following code to retrieve and display the user's profile:

```python
def get_user_profile(user_id):
    # Fetch the user's profile from the database
    profile = db.query("SELECT * FROM users WHERE id = ?", [user_id])
    
    # Return the profile data
    return profile
```

This code is vulnerable to BOLA because it does not check whether the requesting user is authorized to access the specified `user_id`.

#### Exploiting BOLA

An attacker could exploit this vulnerability by manipulating the `user_id` parameter in the URL. For example, if the attacker knows the `user_id` of another user, they could access that user's profile by simply changing the `user_id` in the URL:

```
https://example.com/profile/12345
```

If the application does not properly enforce authorization checks, the attacker would be able to view the profile of user `12345`, even if they are not authorized to do so.

### Brute Force Attacks

In some cases, attackers may attempt to brute force the `user_id` parameter to gain unauthorized access. This involves systematically trying different `user_id` values until a valid one is found.

#### Example of Brute Force Attack

Consider the following scenario:

1. The attacker starts with `user_id = 1`.
2. They increment the `user_id` value and make a request to the application.
3. If the request returns a valid profile, the attacker has successfully accessed a user's profile.
4. If the request returns an error (e.g., 401 Unauthorized or 403 Forbidden), the attacker continues to increment the `user_id` value.

This brute force approach can be automated using scripts or tools designed for such attacks.

### Error Handling and Responses

When attempting to exploit BOLA, attackers often rely on error messages to determine whether their attempts are successful. The application's error handling and response codes play a crucial role in this process.

#### Common Error Responses

1. **401 Unauthorized**: Indicates that the user is not authenticated.
2. **403 Forbidden**: Indicates that the user is authenticated but not authorized to access the requested resource.
3. **404 Not Found**: Indicates that the requested resource does not exist.

#### Example of Error Response

Consider the following HTTP request and response:

```http
POST /profile HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "user_id": "12345"
}
```

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "Forbidden",
  "message": "You are not authorized to access this user profile."
}
```

In this example, the application returns a 403 Forbidden response, indicating that the user is not authorized to access the specified `user_id`.

### Bypassing Authorization Checks

Attackers may attempt to bypass authorization checks by manipulating the request parameters or using alternative methods to access the data.

#### Wrapping with Arrays

One technique used to bypass authorization checks is wrapping the `user_id` parameter with an array. This can sometimes trick the application into processing the request differently.

##### Example of Wrapping with Arrays

Consider the following HTTP request:

```http
POST /profile HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "user_id": ["12345"]
}
```

In this example, the `user_id` parameter is wrapped in an array. Depending on how the application processes the request, this might bypass the authorization check.

### How to Prevent / Defend Against BOLA

Preventing BOLA requires implementing robust authorization checks at the object level. Here are some best practices to ensure proper authorization:

#### Implement Proper Authorization Checks

1. **Check User Identity**: Ensure that the requesting user is authenticated and has the necessary privileges to access the requested object.
2. **Enforce Role-Based Access Control (RBAC)**: Use RBAC to define and enforce access rules based on user roles.
3. **Use Least Privilege Principle**: Grant users the minimum level of access required to perform their tasks.

#### Secure Coding Practices

1. **Validate Input**: Always validate input parameters to ensure they meet expected criteria.
2. **Sanitize Output**: Sanitize output data to prevent injection attacks.
3. **Use Parameterized Queries**: Use parameterized queries to prevent SQL injection attacks.

#### Example of Secure Code

Here is an example of secure code that properly enforces authorization checks:

```python
def get_user_profile(user_id, current_user):
    # Check if the current user is authorized to access the specified user_id
    if current_user.id != user_id:
        raise UnauthorizedError("You are not authorized to access this user profile.")
    
    # Fetch the user's profile from the database
    profile = db.query("SELECT * FROM users WHERE id = ?", [user_id])
    
    # Return the profile data
    return profile
```

In this example, the `current_user` object is used to verify that the requesting user is authorized to access the specified `user_id`.

### Detection and Monitoring

Detecting BOLA requires monitoring and logging access attempts to sensitive objects. Here are some strategies for detecting and responding to BOLA:

#### Logging and Monitoring

1. **Log Access Attempts**: Log all access attempts to sensitive objects, including the user ID and timestamp.
2. **Monitor for Suspicious Activity**: Monitor access logs for suspicious activity, such as repeated failed attempts to access unauthorized resources.
3. **Alert on Unauthorized Access**: Set up alerts to notify administrators when unauthorized access attempts are detected.

#### Example of Access Logs

Here is an example of access logs:

```json
{
  "timestamp": "2023-10-01T12:00:00Z",
  "user_id": "12345",
  "request_url": "/profile",
  "status_code": 403,
  "message": "You are not authorized to access this user profile."
}
```

In this example, the log entry indicates that a user attempted to access a profile they were not authorized to view.

### Conclusion

BOLA is a critical security issue that can expose sensitive data to unauthorized users. By understanding the mechanics of BOLA and implementing proper authorization checks, developers can mitigate this risk and ensure the security of their applications.

### Practice Labs

For hands-on practice with BOLA, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on broken object-level authorization.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security vulnerabilities, including BOLA.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing and security assessments.

By engaging with these labs, you can gain practical experience in identifying and mitigating BOLA vulnerabilities.

---
<!-- nav -->
[[API Security/06-Broken Object Level Authorization issues/01-BOLA Concept/00-Overview|Overview]] | [[API Security/06-Broken Object Level Authorization issues/01-BOLA Concept/02-Introduction to Broken Object-Level Authorization (BOLA)|Introduction to Broken Object-Level Authorization (BOLA)]]
