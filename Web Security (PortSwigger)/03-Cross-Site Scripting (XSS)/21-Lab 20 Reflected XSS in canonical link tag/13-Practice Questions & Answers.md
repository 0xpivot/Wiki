---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the canonical link tag can be exploited for a reflected XSS attack.**

The canonical link tag is used to specify the preferred version of a webpage when multiple versions exist. If the value of the `href` attribute in the canonical link tag is derived from user input and not properly sanitized, it can lead to a reflected XSS attack. An attacker can inject malicious JavaScript code into the `href` attribute, which will be executed when the page is loaded. For example, if the canonical link tag is constructed using unfiltered user input, an attacker might inject an `onclick` event handler that triggers JavaScript execution.

**Q2. How does URL encoding affect the exploitation of XSS vulnerabilities?**

URL encoding can complicate the exploitation of XSS vulnerabilities because certain characters, such as spaces, are encoded into their respective URL-encoded representations (e.g., `%20` for a space). This can disrupt the syntax of injected JavaScript code. For instance, if an attacker tries to inject an `onclick` attribute with a space between the attribute name and the value, the space might be URL-encoded, breaking the script. To bypass this, attackers can use alternative encodings, such as `%09` for a tab, which can serve as a space in some contexts.

**Q3. How would you exploit a reflected XSS vulnerability in a canonical link tag using the given key combinations?**

To exploit a reflected XSS vulnerability in a canonical link tag, you would need to inject a script that triggers when a specific key combination is pressed. Here’s how:

1. Identify the canonical link tag and determine if it reflects user input.
2. Inject an `onclick` event handler into the `href` attribute of the canonical link tag.
3. Use an `accesskey` attribute to bind the script to a specific key combination. For example, if the key combination is `alt+x`, the payload might look like this:

```html
<link rel="canonical" href="javascript:void(0)" onclick="alert('XSS')" accesskey="x">
```

4. Ensure that the payload is correctly URL-encoded to avoid breaking the script due to special characters.

**Q4. Why is the Chrome browser specifically mentioned as necessary for this lab?**

Chrome browser is specifically mentioned because it may handle certain aspects of the exploit differently compared to other browsers. For example, the way Chrome processes URL-encoded characters or the handling of `accesskey` attributes might differ from other browsers. Additionally, some browser-specific features or security settings might influence the success of the exploit. Therefore, ensuring the exploit works in Chrome guarantees compatibility with a widely-used browser.

**Q5. What recent real-world examples demonstrate the impact of XSS vulnerabilities in canonical link tags?**

Recent real-world examples include various web applications where canonical link tags were improperly sanitized, leading to XSS vulnerabilities. For instance, a CMS system might reflect user input in the canonical link tag without proper validation, allowing attackers to inject malicious scripts. A notable example is the discovery of XSS vulnerabilities in popular blogging platforms, where attackers could inject scripts via canonical links, potentially stealing session cookies or redirecting users to malicious sites. Such vulnerabilities often arise from insufficient input validation and sanitization practices.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/12-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]]
