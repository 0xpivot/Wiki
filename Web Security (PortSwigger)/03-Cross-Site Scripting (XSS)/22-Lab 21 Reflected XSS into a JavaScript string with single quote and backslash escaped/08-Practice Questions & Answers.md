---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a reflected XSS vulnerability is and why it is significant in web security.**

A reflected XSS vulnerability occurs when an attacker can inject malicious scripts into a web page viewed by other users. The injected script comes from the current HTTP request, and it is executed in the context of the user's browser. This type of vulnerability is significant because it can lead to various attacks such as stealing session cookies, redirecting users to malicious sites, or performing actions on behalf of the victim. For example, CVE-2021-44228 (Log4Shell) involved a vulnerability that could be exploited via reflected XSS to execute arbitrary code on the server.

**Q2. How would you exploit a reflected XSS vulnerability in a JavaScript string where single quotes and backslashes are escaped?**

To exploit a reflected XSS vulnerability in a JavaScript string where single quotes and backslashes are escaped, you need to find a way to break out of the string context. One common approach is to use HTML tags like `<script>` to inject your payload. Since the single quotes and backslashes are escaped, you can bypass the escaping mechanism by injecting a closing `</script>` tag followed by a new `<script>` tag. Here’s an example payload:

```html
<script>alert(1)</script>
```

This payload will be interpreted as a new script block, allowing you to execute arbitrary JavaScript code.

**Q3. Why is it important to test both the heading and the script tag for reflected input in a web application?**

It is important to test both the heading and the script tag for reflected input because different parts of the web page may handle input differently. The heading might properly encode special characters to prevent XSS, while the script tag might not. By testing both, you ensure that you identify all potential vulnerabilities. In the lab scenario, the heading encoded the `<` and `>` signs, but the script tag did not, making it vulnerable to XSS.

**Q4. How would you configure a web application firewall (WAF) to mitigate reflected XSS attacks?**

To configure a WAF to mitigate reflected XSS attacks, you would set up rules to detect and block suspicious patterns commonly associated with XSS attacks. These rules can include:

- Blocking requests containing potentially dangerous characters or sequences like `<script>`, `alert()`, etc.
- Ensuring that user inputs are properly sanitized and validated before being used in the response.
- Implementing content security policies (CSP) to restrict the sources from which scripts can be loaded.

Here’s an example of a rule configuration in a WAF:

```json
{
  "rule": {
    "name": "XSS Prevention",
    "description": "Prevent reflected XSS attacks",
    "conditions": [
      { "field": "request.body", "operator": "contains", "value": "<script>" },
      { "field": "request.query", "operator": "contains", "value": "alert(" }
    ],
    "action": "block"
  }
}
```

This rule would block any request containing `<script>` or `alert(` in the body or query parameters.

**Q5. Describe a recent real-world example of a reflected XSS vulnerability and its impact.**

A recent example of a reflected XSS vulnerability is CVE-2021-31974, which affected GitHub. The vulnerability allowed attackers to inject malicious scripts into URLs that were reflected back to users. When a user clicked on a crafted URL, the script would execute in their browser, potentially leading to unauthorized actions such as stealing session tokens or redirecting users to malicious sites. The impact included potential data theft and unauthorized access to user accounts. GitHub quickly patched the vulnerability and advised users to update their browsers and clear their cookies as a precautionary measure.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/07-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/00-Overview|Overview]]
