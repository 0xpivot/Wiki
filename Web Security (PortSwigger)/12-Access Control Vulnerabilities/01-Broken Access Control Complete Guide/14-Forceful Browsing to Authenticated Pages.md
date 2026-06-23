---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Forceful Browsing to Authenticated Pages

### What is Forceful Browsing?

Forceful browsing is a technique where an attacker attempts to access authenticated pages without proper authorization. This can be done by guessing URLs or using automated tools to discover and access sensitive resources.

### Why Is Forceful Browsing Vulnerable?

Forceful browsing can be exploited to gain unauthorized access to sensitive resources. If an attacker can guess or discover the URLs of authenticated pages, they can access those pages without proper authorization.

### Example: Forceful Browsing

Consider a web application that allows users to view their account details. The application might have an endpoint like `/account` that displays the user's account information. If the application does not properly enforce access control, an attacker could access the `/account` endpoint without proper authorization.

For example, the following URL might be vulnerable:

```plaintext
https://example.com/account
```

If the application does not check whether the user is authenticated before displaying the account information, an attacker could access the `/account` endpoint without proper authorization.

### Real-World Example: CVE-2021-23290

In 2021, a vulnerability was discovered in a popular web application framework where forceful browsing was not properly prevented. An attacker could access authenticated pages without proper authorization and gain unauthorized access to sensitive resources.

### How to Exploit

To exploit this vulnerability, an attacker would attempt to access the authenticated pages without proper authorization. For example:

```plaintext
https://example.com/account
```

### How to Prevent / Defend

#### Detection

Automated tools like Burp Suite or OWASP ZAP can help detect forceful browsing vulnerabilities by analyzing URLs and observing changes in the application's behavior.

#### Prevention

1. **Enforce Access Control**: Ensure that access control is properly enforced on all authenticated pages.
2. **Use Secure Tokens**: Use secure tokens that are validated on the server side to ensure that users are properly authenticated.
3. **Secure Coding Practices**: Ensure that all input parameters are validated and sanitized.

#### Secure Code Fix

**Vulnerable Code:**

```php
<?php
if (isset($_GET['page'])) {
    $page = $_GET['page'];
    include "$page.php";
}
?>
```

**Fixed Code:**

```php
<?php
if (isset($_GET['page']) && is_authenticated()) {
    $page = $_GET['page'];
    include "$page.php";
} else {
    echo "Access Denied";
}
?>
```

### Summary

Forceful browsing is a common vulnerability that can be exploited to gain unauthorized access to sensitive resources. Proper enforcement of access control mechanisms can prevent such attacks.

---

---
<!-- nav -->
[[13-Exploiting CORS Misconfigurations|Exploiting CORS Misconfigurations]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[15-Hands-On Practice Labs|Hands-On Practice Labs]]
