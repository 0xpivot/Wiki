---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Business Logic Vulnerabilities: Weak Isolation on Dual-Use Endpoint

### Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when the application logic does not correctly enforce business rules or constraints. These vulnerabilities can lead to unintended behavior, such as unauthorized access, data manipulation, or financial loss. In the context of web applications, these vulnerabilities often arise due to weak isolation between different functionalities or endpoints.

### Understanding the Scenario

In the given scenario, we have an application with two functionalities: changing the email address and changing the password. Both functionalities are accessible via a single endpoint, leading to potential vulnerabilities due to weak isolation.

#### Changing Email Address Functionality

The email address change functionality is accessed via a POST request to the `/my_account/change_email` endpoint. The request body contains the new email address.

```http
POST /my_account/change_email HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

email=test@test.c
```

Upon receiving this request, the server updates the user's email address. However, the transcript suggests that this functionality does not appear to be vulnerable.

#### Changing Password Functionality

The password change functionality is accessed via a POST request to the `/my_account/change_password` endpoint. The request body includes several parameters:

- `csrf_token`: A token used to prevent Cross-Site Request Forgery (CSRF) attacks.
- `username`: The username of the user whose password is being changed.
- `current_password`: The current password of the user.
- `new_password`: The new password for the user.
- `confirm_new_password`: Confirmation of the new password.

```http
POST /my_account/change_password HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

csrf_token=abc123&username=peter&current_password=Peter&new_password=test&confirm_new_password=test
```

### Potential Vulnerability Analysis

The key issue in this scenario is the lack of proper isolation between the functionalities. Specifically, the `username` parameter in the password change request can potentially be manipulated to target other users' accounts.

#### Weak Isolation Issue

If the backend logic does not properly validate the `username` parameter against the currently authenticated user, an attacker could exploit this to change the password of any user. This is a classic example of a business logic vulnerability due to weak isolation.

### Real-World Example: CVE-2021-21972

A real-world example of a similar vulnerability is CVE-2021-21972, which affected the WordPress REST API. In this case, an attacker could manipulate the API to change the password of any user, bypassing the intended isolation.

### How to Exploit

To exploit this vulnerability, an attacker would craft a malicious request to the `/my_account/change_password` endpoint, setting the `username` parameter to a target user's username and providing the correct `current_password`.

```http
POST /my_account/change_password HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

csrf_token=abc123&username=admin&current_password=admin123&new_password=hacked&confirm_new_password=hacked
```

### Detection and Prevention

#### Detection

To detect such vulnerabilities, automated tools like Burp Suite, ZAP, or custom scripts can be used to analyze the application's behavior. Additionally, static code analysis tools like SonarQube or Fortify can help identify potential issues in the codebase.

#### Prevention

To prevent this type of vulnerability, the following measures should be taken:

1. **Proper Validation**: Ensure that the `username` parameter in the password change request matches the currently authenticated user.
2. **Session Management**: Use session management techniques to tie the `username` parameter to the session ID.
3. **Input Validation**: Validate all input parameters to ensure they conform to expected formats and values.
4. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activities, such as multiple failed password change attempts.

### Secure Code Fix

Here is an example of how the code should be modified to prevent the vulnerability:

**Vulnerable Code:**

```python
def change_password(request):
    username = request.POST['username']
    current_password = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_new_password = request.POST['confirm_new_password']

    # Change password logic
    user = User.objects.get(username=username)
    if user.check_password(current_password):
        user.set_password(new_password)
        user.save()
```

**Fixed Code:**

```python
def change_password(request):
    username = request.POST['username']
    current_password = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_new_password = request.POST['confirm_new_password']

    # Get the currently authenticated user
    authenticated_user = request.user

    # Validate the username against the authenticated user
    if authenticated_user.username == username:
        user = User.objects.get(username=username)
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
    else:
        raise PermissionDenied("You are not allowed to change this user's password.")
```

### Configuration Hardening

Ensure that the application's configuration files are hardened to prevent unauthorized access. For example, in an Apache configuration, ensure that sensitive directories are restricted:

```apache
<Directory "/var/www/html">
    Order Deny,Allow
    Deny from all
    Allow from 127.0.0.1
</Directory>
```

### Conclusion

Business logic vulnerabilities due to weak isolation can have severe consequences. By understanding the underlying mechanisms and implementing proper validation and session management, developers can significantly reduce the risk of such vulnerabilities. Regular security assessments and code reviews are essential to maintain the security of web applications.

### Practice Labs

For hands-on practice with business logic vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various web security topics, including business logic vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities for educational purposes.

These labs provide practical experience in identifying and mitigating business logic vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/08-Lab 7 Weak isolation on dual use endpoint/01-Introduction to Business Logic Vulnerabilities|Introduction to Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/08-Lab 7 Weak isolation on dual use endpoint/00-Overview|Overview]] | [[03-How to Prevent  Defend Against Business Logic Vulnerabilities|How to Prevent  Defend Against Business Logic Vulnerabilities]]
