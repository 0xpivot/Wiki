---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is a reflected DOM-based XSS vulnerability?**

A reflected DOM-based XSS vulnerability occurs when user-supplied input is echoed back in the response and subsequently processed by a script on the page in an unsafe manner. This can lead to the execution of arbitrary JavaScript code within the context of the victim's browser. The key aspect of reflected DOM-based XSS is that the malicious payload is typically injected via a URL parameter and then executed in the DOM rather than directly in the HTML response.

**Q2. How does the `eval` function contribute to DOM-based XSS vulnerabilities?**

The `eval` function in JavaScript is extremely powerful as it evaluates a string as JavaScript code. When combined with user input, it can execute arbitrary code, leading to security vulnerabilities. In the context of DOM-based XSS, if a script uses `eval` to process data derived from user input (such as URL parameters), an attacker can inject malicious JavaScript code that will be executed by the `eval` function. This can result in actions such as stealing cookies, redirecting the user to a malicious site, or performing other harmful actions.

**Q3. Explain how you would exploit a reflected DOM-based XSS vulnerability using the `eval` function.**

To exploit a reflected DOM-based XSS vulnerability using the `eval` function, follow these steps:

1. Identify the vulnerable script that processes user input and passes it to `eval`.
2. Craft a payload that breaks out of the expected string context and injects additional JavaScript code.
3. Ensure the payload is properly URL-encoded to avoid issues with special characters.
4. Inject the payload into the URL parameter that is reflected in the DOM and processed by the script.
5. Trigger the payload by navigating to the crafted URL.

For example, if the script processes a URL parameter `search` and passes its value to `eval`, a payload like `";alert(1);/*` can be used to inject an `alert` function call. The payload should be URL-encoded appropriately to ensure it is interpreted correctly by the browser.

**Q4. How would you mitigate a reflected DOM-based XSS vulnerability?**

To mitigate a reflected DOM-based XSS vulnerability, consider the following strategies:

1. **Input Validation and Sanitization**: Validate and sanitize all user inputs to ensure they conform to expected formats and do not contain malicious code.
2. **Use Contextual Escaping**: Ensure that user inputs are properly escaped before being inserted into the DOM. Different contexts (HTML, CSS, JavaScript, etc.) require different escaping techniques.
3. **Avoid Using `eval`**: Avoid using the `eval` function with user-supplied data. Instead, use safer alternatives like JSON.parse for parsing JSON strings.
4. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded, thereby reducing the risk of XSS attacks.
5. **HTTPOnly Cookies**: Set the HTTPOnly flag on cookies to prevent them from being accessed via JavaScript, mitigating the impact of XSS attacks.

**Q5. Reference a recent real-world example of a reflected DOM-based XSS vulnerability.**

One recent example of a reflected DOM-based XSS vulnerability is CVE-2021-21972, which affected the popular web analytics tool Matomo (formerly Piwik). The vulnerability allowed attackers to inject malicious JavaScript code through the `urlReferrer` parameter, which was then processed by the Matomo script using `eval`. This could lead to the execution of arbitrary JavaScript code in the context of the victim's browser, potentially allowing attackers to steal sensitive information or perform other malicious actions.

To exploit this vulnerability, an attacker could craft a URL with a malicious payload in the `urlReferrer` parameter, such as:

```
https://example.com/index.php?urlReferrer=");alert(1);//
```

This payload would break out of the expected string context and execute the `alert` function, demonstrating the vulnerability. Proper input validation and sanitization, along with avoiding the use of `eval`, could have prevented this issue.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/06-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/00-Overview|Overview]]
