---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples of XSS Vulnerabilities

### Recent CVEs and Breaches

#### CVE-2021-44228 (Log4Shell)

Although Log4Shell is primarily a Remote Code Execution (RCE) vulnerability, it can also be exploited to deliver XSS payloads. Attackers can inject malicious JavaScript into log messages, which are then rendered in web interfaces.

#### CVE-2022-22965 (Drupal RCE)

Drupal had a critical RCE vulnerability that could be leveraged to inject XSS payloads. By exploiting this vulnerability, attackers could execute arbitrary JavaScript on the affected site.

### Example Exploits

Consider a scenario where a web application reflects user input in a canonical link tag. An attacker might inject a script that triggers an `alert` function when certain key combinations are pressed.

```html
<link rel="canonical" href="https://example.com/page?callback=<script>alert('XSS');</script>">
```

When the victim visits the crafted URL, the injected script is executed, leading to an `alert` box appearing on the screen.

---
<!-- nav -->
[[09-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/11-Understanding the Vulnerability|Understanding the Vulnerability]]
