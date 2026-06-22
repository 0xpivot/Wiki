---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Testing for Cross-Site Scripting (XSS)

### Step-by-Step XSS Testing

1. **Identify Input Fields**: Locate the input fields that reflect user input in the DOM.
2. **Inject Test Payloads**: Inject payloads such as `<script>alert('XSS')</script>` into these fields.
3. **Inspect DOM Manipulation**: Use the browser's developer tools to inspect how the input is reflected in the DOM.

#### Example Code Injection

Let's inject a simple script tag into the comment field:

```html
<script>alert('XSS')</script>
```

If the application is vulnerable, this script will execute in the context of the victim's browser.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is another example of a DOM-based vulnerability affecting the popular web analytics service Matomo. The vulnerability allowed attackers to inject arbitrary JavaScript into the DOM, leading to potential XSS attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/05-How to Prevent  Defend Against DOM-Based Vulnerabilities|How to Prevent  Defend Against DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/00-Overview|Overview]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/07-Understanding DOM-Based Vulnerabilities|Understanding DOM-Based Vulnerabilities]]
