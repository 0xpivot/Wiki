---
course: API Security
topic: Broken Object Level Authorization issues
tags: [api-security]
---

## Broken Object Level Authorization (BOLA)

### Introduction

Broken Object Level Authorization (BOLA) is a critical security issue that affects many modern applications, particularly those that rely heavily on APIs. In essence, BOLA occurs when an application fails to properly restrict access to specific objects based on the user's authorization level. This means that an attacker might be able to manipulate object identifiers to gain unauthorized access to sensitive data or perform actions that they shouldn't be allowed to perform.

### Understanding BOLA

#### What is BOLA?

BOLA is a type of vulnerability where an application does not enforce proper authorization checks at the object level. This means that even though a user might be authenticated, they can still access or modify objects that they should not have access to. For instance, consider an API endpoint that allows users to reset their passwords. If the API does not check whether the user attempting to reset the password is the actual owner of the account, an attacker could potentially reset anyone's password simply by manipulating the username parameter.

#### Why Does BOLA Matter?

BOLA is significant because it can lead to severe security breaches. An attacker exploiting a BOLA vulnerability can gain unauthorized access to sensitive data, perform unauthorized actions, and potentially take control of entire systems. This is similar to how SQL Injection attacks were rampant in the past, compromising numerous systems. Today, BOLA represents a new and significant threat to API security.

### How BOLA Works

#### Example Scenario: Password Reset

Let's consider an example where an API endpoint allows users to reset their passwords. The API might look something like this:

```http
POST /api/v2/reset-password HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "john_doe",
  "new_password": "securepassword123"
}
```

In this scenario, if the server does not verify that the user making the request is indeed `john_doe`, an attacker could send a request with any username and reset that user's password. This is a classic case of BOLA.

### Identifying BOLA Vulnerabilities

#### Finding Identifiers in HTTP Bodies and Headers

To identify BOLA vulnerabilities, you need to look for object identifiers in HTTP bodies and headers. These identifiers are often used to reference specific resources or objects within the application. Here’s how you can go about identifying them:

1. **HTTP Body**: Look for parameters in the request body that reference specific objects. For example, in the password reset API, the `username` parameter is a potential identifier.
   
   ```json
   {
     "username": "john_doe",
     "new_password": "securepassword123"
   }
   ```

2. **HTTP Headers**: Sometimes, object identifiers are passed in headers. For example, a custom header might contain a user ID.

   ```http
   POST /api/v2/reset-password HTTP/1.1
   Host: example.com
   Content-Type: application/json
   X-User-ID: 12345

   {
     "new_password": "securepassword123"
   }
   ```

3. **URL Parameters**: While less common for BOLA, URL parameters can also contain object identifiers.

   ```http
   GET /api/v2/user/12345 HTTP/1.1
   Host: example.com
   ```

### Real-World Examples

#### Recent CVEs and Breaches

Several recent CVEs and breaches have been attributed to BOLA vulnerabilities. For example:

- **CVE-2021-3129**: A BOLA vulnerability was found in a popular e-commerce platform, allowing attackers to access and modify orders belonging to other users.
- **Breaches involving financial institutions**: Multiple financial institutions have suffered breaches due to BOLA, where attackers were able to manipulate account identifiers to access sensitive financial data.

### Detection and Exploitation

#### Steps to Detect BOLA

1. **Identify Object Identifiers**: Look for parameters in the request body, headers, or URL that reference specific objects.
2. **Test Access Control**: Attempt to manipulate these identifiers to see if you can access or modify objects that you should not have access to.
3. **Automated Tools**: Use tools like Burp Suite, OWASP ZAP, or custom scripts to automate the process of detecting BOLA vulnerabilities.

#### Example Exploit

Consider the following scenario where an attacker attempts to reset another user's password:

```http
POST /api/v2/reset-password HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "admin",
  "new_password": "hackedpassword123"
}
```

If the server does not properly validate the user's identity, the attacker can successfully reset the admin's password.

### How to Prevent / Defend Against BOLA

#### Secure Coding Practices

1. **Always Validate User Identity**: Ensure that the user making the request is authorized to access or modify the specified object. This can be done using session tokens, OAuth tokens, or other authentication mechanisms.
   
   ```python
   def reset_password(request):
       user = authenticate_user(request)
       if user.username != request.json['username']:
           raise UnauthorizedError("You are not authorized to reset this password.")
       # Proceed with password reset logic
   ```

2. **Use Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users can only access objects that they are authorized to access based on their roles.

   ```python
   def reset_password(request):
       user = authenticate_user(request)
       if not user.has_role('admin'):
           raise UnauthorizedError("You are not authorized to reset this password.")
       # Proceed with password reset logic
   ```

#### Configuration Hardening

1. **API Gateway Policies**: Use API gateways to enforce access control policies. For example, an API gateway can be configured to reject requests that do not meet certain criteria.

   ```yaml
   policies:
     - name: "reset-password-policy"
       description: "Ensure that only the owner can reset their password."
       rules:
         - if: "request.body.username == authenticated_user.username"
           then: "allow"
         - else: "deny"
   ```

2. **Server-Side Validation**: Always validate input on the server side to ensure that it meets the required criteria.

   ```python
   def reset_password(request):
       user = authenticate_user(request)
       if not validate_username(user, request.json['username']):
           raise UnauthorizedError("You are not authorized to reset this password.")
       # Proceed with password reset logic
   ```

### Conclusion

BOLA is a significant security issue that can lead to severe breaches if not properly addressed. By understanding how BOLA works, identifying potential vulnerabilities, and implementing robust security measures, you can protect your applications from these types of attacks.

### Practice Labs

For hands-on experience with BOLA, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers detailed modules on API security, including BOLA.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes BOLA vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Contains various security vulnerabilities, including BOLA.

By engaging with these labs, you can gain practical experience in identifying and mitigating BOLA vulnerabilities.

---
<!-- nav -->
[[API Security/06-Broken Object Level Authorization issues/01-BOLA Concept/02-Introduction to Broken Object-Level Authorization (BOLA)|Introduction to Broken Object-Level Authorization (BOLA)]] | [[API Security/06-Broken Object Level Authorization issues/01-BOLA Concept/00-Overview|Overview]] | [[04-Broken Object-Level Authorization (BOLA)|Broken Object-Level Authorization (BOLA)]]
