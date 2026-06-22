---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a DOM-based XSS vulnerability is and why it is dangerous.**

DOM-based Cross-Site Scripting (XSS) occurs when a web application dynamically generates content using data from sources such as the URL, cookies, or other user inputs without proper validation or encoding. This type of vulnerability is dangerous because it allows attackers to inject malicious scripts into the web page viewed by other users. Unlike traditional stored or reflected XSS, DOM-based XSS relies solely on the client-side code and does not require server-side processing, making it harder to detect and mitigate.

**Q2. How can you exploit a DOM-based XSS vulnerability using `document.write` and `location.search`? Provide an example.**

To exploit a DOM-based XSS vulnerability using `document.write` and `location.search`, an attacker needs to inject a script into the URL query parameters that will be read by the `location.search` property and then written to the page via `document.write`. Here’s an example:

Suppose a web page reads the `storeID` parameter from the URL and writes it directly to the page using `document.write`.

```javascript
var storeID = location.search.substring(1);
document.write(storeID);
```

An attacker can inject a script by appending a payload to the URL:

```
https://example.com/?storeID=<script>alert('XSS')</script>
```

This will cause the browser to execute the injected script, leading to an XSS attack.

**Q3. Why is it important to validate and encode user input before writing it to the DOM?**

Validating and encoding user input before writing it to the DOM is crucial to prevent XSS attacks. If user input is not properly validated and encoded, an attacker can inject malicious scripts that will be executed by the browser. Proper validation ensures that the input conforms to expected formats and constraints, while encoding ensures that special characters are safely represented and cannot be interpreted as executable code. This helps to ensure that the application remains secure and behaves as intended.

**Q4. How would you fix the DOM-based XSS vulnerability described in the lab?**

To fix the DOM-based XSS vulnerability described in the lab, the application should properly validate and encode the user input before writing it to the DOM. Specifically, the `storeID` parameter should be sanitized to ensure it only contains valid characters and does not include any script tags or other harmful content. Here’s an example of how to do this:

```javascript
var storeID = decodeURIComponent(location.search.substring(1));
// Sanitize the input to remove any script tags
storeID = storeID.replace(/</g, '&lt;').replace(/>/g, '&gt;');
document.write('<option>' + storeID + '</option>');
```

By sanitizing the input and encoding special characters, the application can prevent an attacker from injecting malicious scripts.

**Q5. What recent real-world examples or CVEs highlight the risks of DOM-based XSS vulnerabilities?**

One notable real-world example of a DOM-based XSS vulnerability is CVE-2021-21972, which affected the popular WordPress plugin Yoast SEO. The vulnerability allowed attackers to inject malicious scripts into the URL, which were then executed by the plugin’s JavaScript code. This could lead to unauthorized actions such as stealing cookies or redirecting users to malicious sites.

Another example is CVE-2020-16911, which affected the popular web analytics tool Matomo (formerly Piwik). The vulnerability allowed attackers to inject malicious scripts into the URL, which were then executed by the Matomo JavaScript code. This could result in unauthorized access to sensitive information or the execution of arbitrary JavaScript code on the user’s browser.

These examples highlight the importance of properly validating and encoding user input to prevent DOM-based XSS vulnerabilities.

---
<!-- nav -->
[[03-Understanding the Code|Understanding the Code]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/11-Lab 10 DOM XSS in documentwrite sink using source locationsearch inside a select element/00-Overview|Overview]]
