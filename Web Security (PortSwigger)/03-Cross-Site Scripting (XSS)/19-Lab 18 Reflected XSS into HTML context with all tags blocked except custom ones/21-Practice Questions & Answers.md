---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the lab environment blocks all HTML tags except custom ones.**

The lab environment is designed to block all standard HTML tags but allows custom tags. This is typically achieved through a web application firewall (WAF) or server-side logic that sanitizes input. The WAF checks the input for known HTML tags and blocks them, while allowing custom tags that are not recognized as standard HTML tags. This setup makes it challenging to perform a typical XSS attack using standard tags like `<script>` or `<img>`.

**Q2. How would you exploit a reflected XSS vulnerability when all standard HTML tags are blocked except for custom ones?**

To exploit a reflected XSS vulnerability when all standard HTML tags are blocked except for custom ones, you would use a custom tag that triggers JavaScript execution. For example, you can use a custom tag like `<xss>` and define it with an event handler that executes JavaScript. Here’s an example payload:

```html
<xss onfocus=alert(document.cookie)>
```

This payload uses the `onfocus` event to execute the `alert(document.cookie)` function. When the custom tag is rendered, the event handler will trigger, leading to the execution of the JavaScript code.

**Q3. Why is the custom tag approach effective in bypassing WAFs that block standard HTML tags?**

The custom tag approach is effective in bypassing WAFs that block standard HTML tags because WAFs typically rely on predefined rules to detect and block malicious inputs. These rules are often based on known HTML tags and common XSS patterns. Custom tags, however, are not part of the standard HTML specification and thus are unlikely to be detected by these rules. As a result, the WAF may allow the custom tag to pass through, enabling the attacker to execute arbitrary JavaScript.

**Q4. How would you configure a WAF to prevent XSS attacks when custom tags are allowed?**

To configure a WAF to prevent XSS attacks when custom tags are allowed, you would need to implement more advanced content security policies (CSP) and heuristic-based detection mechanisms. Here are some steps:

1. **Content Security Policy (CSP):** Implement a strict CSP that restricts the sources from which scripts can be loaded. This helps mitigate the risk of inline scripts executing.

   ```http
   Content-Security-Policy: default-src 'self'; script-src 'none'
   ```

2. **Heuristic Detection:** Use heuristic-based detection to identify suspicious patterns in custom tags. This involves analyzing the structure and behavior of custom tags to determine if they are likely to be used for malicious purposes.

3. **Custom Tag Whitelisting:** Maintain a whitelist of allowed custom tags and their attributes. Any custom tag not on the whitelist should be blocked.

4. **Sanitization:** Implement input sanitization to remove or escape any potentially dangerous characters or patterns within custom tags.

By combining these strategies, you can significantly reduce the risk of XSS attacks even when custom tags are allowed.

**Q5. Reference a recent real-world example where custom tags were exploited in an XSS attack.**

A notable example of custom tags being exploited in an XSS attack is the case of the WhatsApp web interface vulnerability (CVE-2019-15768). In this case, attackers used custom tags to bypass content security policies and execute arbitrary JavaScript. The vulnerability allowed attackers to inject custom tags like `<xss>` with event handlers that triggered JavaScript execution, leading to potential data theft or other malicious activities.

In this attack, the custom tags were used to bypass the CSP restrictions and execute malicious scripts, demonstrating the importance of robust security measures even when custom tags are allowed.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/20-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]]
