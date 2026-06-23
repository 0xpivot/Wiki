---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a reflected XSS vulnerability is and how it differs from stored XSS.**

A reflected XSS vulnerability occurs when an attacker can inject malicious scripts into a web page that is immediately returned to the user by the server. The injected script comes from the current HTTP request and is not stored permanently in the server's database. This contrasts with stored XSS, where the malicious script is saved on the server and served to users over time, affecting multiple users who visit the page.

**Q2. How does HTML encoding affect the exploitation of XSS vulnerabilities?**

HTML encoding converts certain characters into their corresponding HTML entities. For example, `<` becomes `&lt;`, and `>` becomes `&gt;`. This encoding can prevent simple XSS attacks by ensuring that characters like `<` and `>` are not interpreted as part of HTML tags. However, attackers can still exploit XSS vulnerabilities by using alternative methods to bypass encoding, such as injecting payloads into attributes that are not strictly HTML-encoded.

**Q3. Describe how to exploit a reflected XSS vulnerability when angle brackets are HTML encoded.**

To exploit a reflected XSS vulnerability when angle brackets are HTML encoded, you need to focus on injecting your payload into attributes rather than directly into HTML tags. Since the angle brackets are encoded, they won't be interpreted as HTML tags. Instead, you can inject a payload into an attribute like `onmouseover` or `onclick`. For instance, if the input is reflected in an `input` tag’s `value` attribute, you can inject a payload like `" onmouseover="alert(1)"`. This payload will be executed when the user interacts with the element.

**Q4. What is the purpose of the `alert` function in the context of demonstrating an XSS vulnerability?**

The `alert` function is commonly used in XSS demonstrations to show that the injected script has been executed in the context of the victim's browser. When the `alert` function is triggered, it displays a pop-up message to the user, indicating that the script has been executed. This serves as a clear visual confirmation that the XSS attack was successful.

**Q5. How can you ensure that your XSS payload does not break the JavaScript syntax when injected into an attribute?**

To ensure that your XSS payload does not break the JavaScript syntax, you need to carefully craft the payload so that it properly closes any existing quotes and does not introduce syntax errors. For example, if the payload is injected into an attribute that is enclosed in double quotes, you should start your payload with a double quote to close the existing attribute value, followed by your script, and end with another double quote to close the attribute. This ensures that the injected script is syntactically valid and will execute correctly.

**Q6. Provide an example of a recent real-world XSS vulnerability and explain how it was exploited.**

One recent example of an XSS vulnerability is the CVE-2021-21972, which affected the popular WordPress plugin Contact Form 7. The vulnerability allowed attackers to inject malicious scripts into form submissions, which were then reflected back to other users. Attackers could exploit this by crafting a malicious form submission that included a script to steal cookies or redirect users to phishing sites. The exploitation involved injecting a payload into the form fields, which were then processed and reflected back to other users, leading to the execution of the injected script in their browsers.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/13-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]]
