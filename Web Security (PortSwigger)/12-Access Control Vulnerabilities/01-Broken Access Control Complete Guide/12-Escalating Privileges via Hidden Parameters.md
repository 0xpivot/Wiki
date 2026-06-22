---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Escalating Privileges via Hidden Parameters

### What are Hidden Parameters?

Hidden parameters are input fields in HTML forms that are not visible to the user but are submitted along with the form data. These parameters can contain important information such as user IDs, session tokens, or other sensitive data.

### Why Are Hidden Parameters Vulnerable?

Hidden parameters can be easily modified by attackers using browser developer tools or automated tools. If the application relies solely on these hidden parameters for authorization, an attacker can manipulate them to escalate their privileges.

### Example: Hidden Parameter Manipulation

Consider a web application that uses hidden parameters to store the user's role and ID. The form might look like this:

```html
<form action="/submit" method="POST">
    <input type="hidden" name="role" value="user">
    <input type="hidden" name="id" value="123">
    <!-- Other form fields -->
</form>
```

An attacker can modify the `role` and `id` parameters to escalate their privileges. For example:

```html
<input type="hidden" name="role" value="admin">
<input type="hidden" name="id" value="456">
```

### Real-World Example: CVE-2-2022-23305

In 2022, a vulnerability was discovered in a popular e-commerce platform where hidden parameters were used to store user roles. An attacker could modify these parameters to gain administrative privileges and access sensitive data.

### How to Exploit

To exploit this vulnerability, an attacker would use browser developer tools to modify the hidden parameters before submitting the form. For example:

```html
<form action="/submit" method="POST">
    <input type="hidden" name="role" value="admin">
    <input type="hidden" name="id" value="456">
    <!-- Other form fields -->
</form>
```

### How to Prevent / Defend

#### Detection

Automated tools like Burp Suite or OWASP ZAP can help detect hidden parameter manipulation vulnerabilities by analyzing form submissions and observing changes in the application's behavior.

#### Prevention

1. **Server-Side Validation**: Always validate the user's permissions on the server side before processing any form data.
2. **Use Secure Tokens**: Instead of relying on hidden parameters, use secure tokens that are validated on the server side.
3. **Secure Coding Practices**: Ensure that all input parameters are validated and sanitized.

#### Secure Code Fix

**Vulnerable Code:**

```php
<?php
$role = $_POST['role'];
$id = $_POST['id'];
// Process form data
?>
```

**Fixed Code:**

```php
<?php
$role = $_POST['role'];
$id = $_POST['id'];
$current_user_role = get_current_user_role();
$current_user_id = get_current_user_id();

if ($current_user_role == 'admin' || ($current_user_role == 'user' && $current_user_id == $id)) {
    // Process form data
} else {
    echo "Access Denied";
}
?>
```

### Summary

Escalating privileges via hidden parameter manipulation is a common vulnerability that can be exploited to gain unauthorized access. Proper validation and enforcement of access control mechanisms can prevent such attacks.

---

---
<!-- nav -->
[[11-Denied by Default Design|Denied by Default Design]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[13-Exploiting CORS Misconfigurations|Exploiting CORS Misconfigurations]]
