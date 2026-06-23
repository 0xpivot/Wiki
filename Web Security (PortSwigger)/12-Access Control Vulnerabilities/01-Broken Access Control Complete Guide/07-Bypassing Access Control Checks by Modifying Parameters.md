---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Bypassing Access Control Checks by Modifying Parameters

### What is Access Control?

Access control is a fundamental security mechanism that ensures users can only access resources and perform actions that they are authorized to do. This is typically enforced through authentication and authorization mechanisms. Authentication verifies the identity of a user, while authorization determines what actions that user is allowed to perform based on their role or permissions.

### Why is Access Control Important?

Access control is crucial because it prevents unauthorized access to sensitive data and functionality. Without proper access control, malicious actors could gain access to confidential information or perform actions that they should not be able to, leading to data breaches, financial losses, and reputational damage.

### How Does Access Control Work?

Access control typically involves several components:

1. **Authentication**: Verifies the identity of the user.
2. **Authorization**: Determines what actions the authenticated user is allowed to perform.
3. **Resource Access**: Ensures that only authorized users can access specific resources.

### Example: Bypassing Access Control via URL Parameters

Consider a web application that allows users to view their profile information. The URL might look like this:

```
https://example.com/profile?id=123
```

Here, `id` is a parameter that specifies which user's profile to display. If the application does not properly enforce access control, an attacker could simply change the `id` parameter to view other users' profiles.

#### Real-World Example: CVE-2021-21972

In 2021, a vulnerability was discovered in the WordPress plugin "WP User Frontend Pro." The plugin allowed users to edit their own posts, but due to a lack of proper access control, an attacker could modify the `post_id` parameter in the URL to edit any post on the site. This led to unauthorized access and potential data manipulation.

### How to Exploit

To exploit this vulnerability, an attacker would modify the `id` parameter in the URL to a value corresponding to another user's profile. For example:

```plaintext
https://example.com/profile?id=456
```

If the application does not check whether the current user is authorized to view this profile, the attacker will be able to see the profile information.

### How to Prevent / Defend

#### Detection

To detect such vulnerabilities, you can use automated tools like Burp Suite or OWASP ZAP to scan for URL parameter modifications and observe the application's behavior.

#### Prevention

1. **Server-Side Validation**: Always validate the user's permissions on the server side before allowing access to any resource.
2. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users can only access resources appropriate to their roles.
3. **Secure Coding Practices**: Ensure that all input parameters are validated and sanitized.

#### Secure Code Fix

**Vulnerable Code:**

```php
<?php
$user_id = $_GET['id'];
$profile = get_user_profile($user_id);
echo $profile;
?>
```

**Fixed Code:**

```php
<?php
$user_id = $_GET['id'];
$current_user_id = get_current_user_id();
if ($current_user_id == $user_id || is_admin($current_user_id)) {
    $profile = get_user_profile($user_id);
    echo $profile;
} else {
    echo "Access Denied";
}
?>
```

### Summary

Bypassing access control via URL parameters is a common vulnerability that can lead to unauthorized access to sensitive information. Proper validation and enforcement of access control mechanisms can prevent such attacks.

---

---
<!-- nav -->
[[06-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[08-Centralized Access Control Engine|Centralized Access Control Engine]]
