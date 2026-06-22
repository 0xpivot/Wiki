---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples

### Recent Breaches and CVEs

Several high-profile breaches and CVEs have been associated with XSS vulnerabilities. Here are a few recent examples:

1. **CVE-2021-21972**: A reflected XSS vulnerability was found in the WordPress plugin "WP GDPR Compliance". Attackers could inject malicious scripts into the plugin's settings page, potentially compromising user sessions.
   
2. **CVE-2020-14182**: A stored XSS vulnerability was discovered in the Atlassian Jira software. Attackers could inject malicious scripts into comments, affecting all users who viewed the comments.

### Impact of XSS Attacks

XSS attacks can have severe consequences, including:

- **Session Hijacking**: Stealing session cookies to gain unauthorized access to user accounts.
- **Defacement**: Modifying the appearance of a website to display malicious content.
- **Phishing**: Redirecting users to phishing sites to steal sensitive information.
- **Data Theft**: Extracting sensitive data from the user's browser, such as login credentials.

---
<!-- nav -->
[[06-Lab Setup|Lab Setup]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/08-Understanding the Vulnerability|Understanding the Vulnerability]]
