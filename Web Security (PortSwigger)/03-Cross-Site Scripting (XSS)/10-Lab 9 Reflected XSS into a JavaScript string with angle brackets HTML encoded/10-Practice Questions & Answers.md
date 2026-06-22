---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why angle brackets are typically HTML encoded in web applications.**

Angle brackets are typically HTML encoded in web applications to prevent cross-site scripting (XSS) attacks. Angle brackets are used to denote HTML tags, and if they are not properly encoded, an attacker could inject malicious scripts into the page. By encoding these characters, the application ensures that they are treated as plain text rather than executable code, thereby mitigating the risk of XSS attacks.

**Q2. How would you exploit a reflected XSS vulnerability where angle brackets are HTML encoded but the input is reflected within a JavaScript string?**

To exploit a reflected XSS vulnerability where angle brackets are HTML encoded but the input is reflected within a JavaScript string, you can break out of the string context without using angle brackets. For example, if the input is reflected like `var searchTerms = 'INPUT';`, you can break out of the string by closing the existing single quote and injecting JavaScript code:

```javascript
' + alert('XSS') +
```

This payload closes the original string, injects the `alert` function, and then reopens a new string to avoid syntax errors. When the injected code is executed, it triggers the `alert` function, demonstrating successful exploitation of the XSS vulnerability.

**Q3. Why is it important to ensure proper encoding of user inputs in both HTML and JavaScript contexts?**

Proper encoding of user inputs in both HTML and JavaScript contexts is crucial to prevent various types of injection attacks, including XSS. In HTML, encoding prevents the execution of arbitrary HTML tags, while in JavaScript, encoding prevents the execution of arbitrary JavaScript code. Failing to encode inputs appropriately can lead to security vulnerabilities where attackers can inject malicious content, potentially leading to unauthorized actions, data theft, or other harmful outcomes.

**Q4. Describe a recent real-world example of an XSS vulnerability and explain how it was exploited.**

A notable recent example of an XSS vulnerability is the one found in the popular social media platform Twitter in 2021 (CVE-2021-29443). The vulnerability allowed attackers to inject malicious JavaScript code into tweets, which would then be executed by other users who viewed the tweet. The exploit involved crafting a tweet containing a specially crafted URL that, when clicked, would execute arbitrary JavaScript in the context of the victim's session. This could result in stealing cookies, taking over accounts, or performing other malicious actions.

**Q5. What is the significance of the `NaN` value in the context of exploiting XSS vulnerabilities in JavaScript strings?**

In the context of exploiting XSS vulnerabilities in JavaScript strings, the `NaN` (Not-a-Number) value can be significant because it allows for breaking out of the string context and executing JavaScript code without needing to close the string explicitly. For instance, if the input is reflected as `var searchTerms = 'INPUT';`, you can inject `-alert('XSS')` to cause the JavaScript interpreter to treat the rest of the string as a subtraction operation, resulting in `NaN`. However, the `alert` function gets executed before the subtraction, effectively triggering the XSS payload. This technique is useful when direct string closure is not possible due to encoding restrictions.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/00-Overview|Overview]]
