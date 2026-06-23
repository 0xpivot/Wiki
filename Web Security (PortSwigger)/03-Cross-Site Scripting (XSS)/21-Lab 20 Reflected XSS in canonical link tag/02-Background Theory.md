---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Background Theory

### What is a Canonical Link?

A canonical link is an HTML element that helps webmasters manage duplicate content issues. It specifies the preferred version of a webpage to be indexed by search engines. The canonical link is defined using the `<link>` tag with the `rel="canonical"` attribute.

```html
<link rel="canonical" href="https://example.com/page">
```

### Why is Canonical Link Important?

Canonical links help search engines understand which version of a page should be considered the primary one. This prevents issues like duplicate content penalties and ensures that the correct page is indexed.

### How Does Reflected XSS Work?

Reflected XSS occurs when user-supplied data is included in the response sent back to the user without proper validation or sanitization. An attacker can craft a URL that includes malicious JavaScript, which is then executed by the victim's browser.

### Key Concepts in XSS

- **Injection Point**: The location in the application where user input is inserted.
- **Execution Context**: The environment in which the injected script runs.
- **Payload**: The malicious code that the attacker injects.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/03-Common Pitfalls and Mistakes|Common Pitfalls and Mistakes]]
