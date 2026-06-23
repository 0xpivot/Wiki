---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples

### Recent CVEs and Breaches

XSS vulnerabilities have been exploited in numerous real-world scenarios. Here are a few recent examples:

1. **CVE-2021-21972**: A stored XSS vulnerability was found in the WordPress plugin "WP GDPR Compliance". An attacker could inject malicious scripts into the plugin settings, affecting all users who visited the site.
   
2. **CVE-2021-33766**: A reflected XSS vulnerability was discovered in the popular web analytics service Matomo. An attacker could inject malicious scripts into the URL parameters, affecting users who clicked on the link.

### Impact of XSS Attacks

XSS attacks can have severe consequences, including:

- **Session Hijacking**: An attacker can steal session cookies and impersonate the victim.
- **Defacement**: An attacker can alter the appearance of a website, causing reputational damage.
- **Phishing**: An attacker can trick users into revealing sensitive information, such as login credentials.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/09-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[11-Understanding the Lab Environment|Understanding the Lab Environment]]
