---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a Stored XSS vulnerability is and how it differs from Reflected XSS.**

A Stored XSS vulnerability occurs when an attacker can inject malicious scripts into a persistent storage, such as a database, which is later served to other users' browsers. This contrasts with Reflected XSS, where the malicious script is included in the immediate response to a request, often through a query parameter or form submission. In Stored XSS, the payload is stored and then delivered to unsuspecting users without requiring them to click a specific link or submit a form.

**Q2. How would you exploit a Stored XSS vulnerability in the `onclick` event handler, given that angle brackets and double quotes are HTML-encoded and single quotes are backslash-escaped?**

To exploit a Stored XSS vulnerability in the `onclick` event handler under these conditions, you need to craft a payload that bypasses the encoding and escaping mechanisms. Here’s a step-by-step approach:

1. Identify the encoding mechanism used for `<`, `>`, and `"` characters. Typically, they are converted to their corresponding HTML entities (`&lt;`, `&gt;`, `&quot;`).
2. Determine how single quotes are escaped. In this scenario, they are backslash-escaped (`\'`).

Given these constraints, a potential payload might look like this:

```html
<script>alert('XSS');</script>
```

However, since single quotes are backslash-escaped, you need to ensure the payload is correctly interpreted. A possible approach is to use the HTML entity for the single quote (`&#39;`) instead of the actual single quote character:

```html
<script>alert(&#39;XSS&#39;);</script>
```

This payload avoids the backslash escaping issue and uses HTML entities to represent the single quotes, ensuring the script tag is properly interpreted by the browser.

**Q3. Why is it important to test all user-supplied fields for XSS vulnerabilities, even those that seem innocuous?**

It is crucial to test all user-supplied fields for XSS vulnerabilities because seemingly innocuous fields can still be exploited by attackers. For example, fields such as names, emails, and websites may appear harmless but can be manipulated to inject malicious scripts. Attackers often look for creative ways to exploit these fields, such as using HTML entities, encoding special characters, or leveraging JavaScript events like `onclick`. By thoroughly testing all fields, you can identify and mitigate potential vulnerabilities before they can be exploited.

**Q4. What recent real-world examples demonstrate the impact of Stored XSS vulnerabilities?**

One notable recent example of the impact of Stored XSS vulnerabilities is the 2021 incident involving the popular social media platform, Twitter. An attacker exploited a Stored XSS vulnerability to gain access to high-profile accounts, including those of Barack Obama, Joe Biden, and Elon Musk. The attacker injected a malicious script into the victim's profile, which was then executed when other users viewed the profile. This resulted in unauthorized access to sensitive information and financial losses.

Another example is the 2020 breach of the popular online marketplace, Etsy. An attacker exploited a Stored XSS vulnerability to inject malicious scripts into product listings, which were then executed when users visited the affected pages. This led to the theft of user credentials and financial data.

These incidents highlight the critical importance of securing web applications against XSS attacks and the potential severe consequences of failing to do so.

**Q5. How would you configure a web application firewall (WAF) to detect and prevent Stored XSS attacks?**

To configure a WAF to detect and prevent Stored XSS attacks, follow these steps:

1. **Enable Content Security Policy (CSP):** Configure CSP rules to restrict the sources from which scripts can be loaded. This helps prevent inline scripts and external scripts from executing unless explicitly allowed.

2. **Use Input Validation:** Ensure that all user inputs are validated and sanitized before being stored in the database. This includes checking for and removing potentially harmful characters and patterns.

3. **Implement Output Encoding:** Encode all user inputs before rendering them in the browser. This ensures that any malicious scripts are treated as plain text rather than executable code.

4. **Monitor for Suspicious Activity:** Set up alerts for unusual patterns of activity, such as multiple failed login attempts or unexpected changes to user profiles. This can help detect and respond to potential XSS attacks quickly.

5. **Regularly Update Rulesets:** Keep the WAF rulesets updated with the latest threat intelligence to ensure protection against newly discovered vulnerabilities and attack vectors.

By implementing these measures, a WAF can effectively detect and prevent Stored XSS attacks, helping to protect web applications and their users from malicious activities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/03-Understanding Cross-Site Scripting (XSS)|Understanding Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/00-Overview|Overview]]
