---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples and Recent Breaches

### Recent CVEs and Breaches

One notable example of XSS vulnerabilities is CVE-2021-21972, which affected WordPress plugins. Attackers could inject malicious scripts into comments or posts, leading to potential data theft or site defacement.

#### Example of CVE-2021-21972

```http
POST /wp-admin/admin-ajax.php HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

action=save_comment&comment_content=<script>alert('XSS')</script>
```

### Impact of XSS Attacks

XSS attacks can have severe consequences, including:

- **Session Hijacking**: Stealing session cookies to impersonate the victim.
- **Data Theft**: Extracting sensitive information like passwords or credit card details.
- **Defacement**: Changing the appearance of a website to spread propaganda or misinformation.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/08-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[10-Real-World Examples of XSS Vulnerabilities|Real-World Examples of XSS Vulnerabilities]]
