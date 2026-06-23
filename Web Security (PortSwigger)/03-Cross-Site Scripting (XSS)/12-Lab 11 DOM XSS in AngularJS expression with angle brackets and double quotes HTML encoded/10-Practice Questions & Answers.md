---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what AngularJS directives are and how they relate to the DOM-based XSS vulnerability in this lab.**

AngularJS directives are special markers placed in the DOM that tell AngularJS's HTML compiler ($compile) to attach a specified behavior to that DOM element or even transform the DOM element and its children. The `ng-app` directive is a specific type of directive that initializes an AngularJS application. In this lab, the presence of `ng-app` indicates that the application is using AngularJS, and any content within this directive can contain AngularJS expressions. This makes it possible to inject malicious code into the DOM, leading to a DOM-based XSS vulnerability.

**Q2. How would you exploit the DOM-based XSS vulnerability in this lab to execute an alert function? Provide the payload used.**

To exploit the DOM-based XSS vulnerability in this lab, you need to craft a payload that uses AngularJS syntax to execute JavaScript code. The payload should be placed in the user-supplied input field, such as the search bar. The payload to execute an alert function would be:

```javascript
{{ $on.constructor('alert')('XSS') }}
```

Here, `$on` is an event handler function in AngularJS, and `.constructor('alert')` creates a new function that calls the `alert` function. The argument `'XSS'` is the message that will be displayed in the alert box.

**Q3. Why is it important to understand the version of AngularJS being used in the application?**

Understanding the version of AngularJS being used in the application is crucial because different versions may have different behaviors, features, and vulnerabilities. For example, older versions of AngularJS might lack certain security enhancements present in newer versions. In this lab, knowing that the application is using AngularJS version 1.7 helps in crafting the appropriate payload since the syntax and available functions can vary between versions.

**Q4. What recent real-world examples or CVEs demonstrate the impact of DOM-based XSS vulnerabilities in applications using AngularJS?**

One notable example is CVE-2019-9978, which affected multiple versions of AngularJS. This vulnerability allowed attackers to inject arbitrary JavaScript code via a crafted input, leading to a DOM-based XSS attack. The impact of such vulnerabilities can be severe, allowing attackers to steal sensitive information, manipulate user sessions, or redirect users to malicious sites. It is essential to keep frameworks like AngularJS updated to mitigate such risks.

**Q5. How does encoding angle brackets and double quotes affect the exploitation of DOM-based XSS in this lab?**

Encoding angle brackets (`<` and `>`) and double quotes (`"`) can prevent traditional XSS attacks by ensuring that these characters are not interpreted as part of the HTML structure or JavaScript code. However, in this lab, the application uses AngularJS, which allows the execution of JavaScript expressions within double curly braces (`{{ }}`). Therefore, even though angle brackets and double quotes are encoded, the AngularJS syntax can still be used to inject and execute JavaScript code, leading to a successful DOM-based XSS attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/00-Overview|Overview]]
