---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the reflected XSS vulnerability works in the context of this lab.**

In this lab, the reflected XSS vulnerability occurs when user input is included in a JavaScript string within the response. The input is partially sanitized by encoding angle brackets and double quotes, and escaping single quotes. However, the escaping mechanism for single quotes is imperfect, allowing an attacker to break out of the string context using a backslash followed by a single quote. Once outside the string, the attacker can inject arbitrary JavaScript code, such as an `alert` function, to demonstrate the vulnerability.

**Q2. How would you exploit the reflected XSS vulnerability described in the lab? Provide a specific payload.**

To exploit the reflected XSS vulnerability, you can use the following payload:

```
\'"; alert(1); //
```

Here’s a breakdown of the payload:
- `\'`: Escapes the single quote to break out of the string context.
- `";`: Ends the current JavaScript string and variable assignment.
- `alert(1);`: Injects the `alert` function to demonstrate the vulnerability.
- `//`: Comments out the remaining characters to avoid syntax errors.

When this payload is submitted, it will execute the `alert` function, confirming the presence of the XSS vulnerability.

**Q3. Why are angle brackets and double quotes HTML encoded, while single quotes are only escaped in this lab?**

Angle brackets (`<` and `>`) and double quotes (`"`) are often HTML encoded to prevent common injection attacks like HTML tag injection or attribute value manipulation. Single quotes (`'`), however, are typically escaped to prevent breaking out of string contexts in JavaScript. In this lab, the encoding and escaping mechanisms are designed to illustrate a scenario where the escaping of single quotes is imperfect, allowing an attacker to bypass the protection and inject malicious JavaScript code.

**Q4. What recent real-world examples or CVEs can you cite that involve similar types of XSS vulnerabilities?**

One notable example is CVE-2021-44228, also known as Log4Shell, which affected Apache Log4j. Although primarily a Remote Code Execution (RCE) vulnerability, it also had implications for XSS attacks due to the way logging mechanisms could be manipulated to inject scripts into web pages. Another example is CVE-2021-21972, which involved a stored XSS vulnerability in Microsoft Exchange Server, where untrusted data was improperly handled, leading to potential script injection attacks.

**Q5. How would you configure a web application firewall (WAF) to mitigate the type of XSS vulnerability demonstrated in this lab?**

To mitigate the type of XSS vulnerability demonstrated in this lab, a WAF can be configured with the following rules:
1. **Input Validation**: Ensure that all user inputs are validated against a strict set of allowed characters and patterns.
2. **Encoding Rules**: Apply encoding rules to ensure that special characters like `<`, `>`, `"`, and `'` are properly encoded before being included in the response.
3. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources from which scripts can be loaded, thereby reducing the risk of XSS attacks.
4. **Sanitization Rules**: Use sanitization rules to remove or escape potentially dangerous characters and patterns that could lead to XSS attacks.

Example configuration snippet for a WAF rule:
```json
{
  "rule": {
    "name": "XSS Protection",
    "description": "Protect against reflected XSS attacks",
    "conditions": [
      {
        "input": "request.query.search",
        "operator": "contains",
        "value": ["<", ">", "\"", "'"]
      }
    ],
    "actions": [
      {
        "type": "encode",
        "parameters": {
          "encoding": "html"
        }
      },
      {
        "type": "sanitize",
        "parameters": {
          "allowedTags": [],
          "allowedAttributes": []
        }
      }
    ]
  }
}
```

This configuration ensures that any input containing potentially harmful characters is properly encoded and sanitized before being processed by the application.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/23-Lab 22 Reflected XSS into a JavaScript string with angle brackets and double quotes HTML encoded and single quotes escaped/08-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/23-Lab 22 Reflected XSS into a JavaScript string with angle brackets and double quotes HTML encoded and single quotes escaped/00-Overview|Overview]]
