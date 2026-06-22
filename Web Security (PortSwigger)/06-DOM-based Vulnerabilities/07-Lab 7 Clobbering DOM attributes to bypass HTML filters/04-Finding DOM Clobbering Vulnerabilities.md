---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Finding DOM Clobbering Vulnerabilities

DOM clobbering occurs when an attacker manipulates the DOM to overwrite properties or methods, leading to unexpected behavior. This can be used to bypass input validation mechanisms and perform XSS attacks.

### Step-by-Step DOM Clobbering Testing

1. **Right-Click and View Page Source**: Right-click on the page and select "View Page Source" to inspect the initial DOM structure.
2. **Manipulate Input Fields**: Manipulate the input fields to see how the DOM is updated.
3. **Inject Malicious Scripts**: Inject scripts that attempt to overwrite DOM properties or methods.

#### Example Code Injection

Let's inject a script that attempts to overwrite a DOM property:

```html
<script>window.location="javascript:alert('XSS')"</script>
```

This script attempts to overwrite the `window.location` property, which can lead to unexpected behavior.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is another example of a DOM-based vulnerability affecting the popular web analytics service Matomo. The vulnerability allowed attackers to inject arbitrary JavaScript into the DOM, leading to potential XSS attacks.

---
<!-- nav -->
[[03-DOM-Based Vulnerabilities|DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/00-Overview|Overview]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/05-How to Prevent  Defend Against DOM-Based Vulnerabilities|How to Prevent  Defend Against DOM-Based Vulnerabilities]]
