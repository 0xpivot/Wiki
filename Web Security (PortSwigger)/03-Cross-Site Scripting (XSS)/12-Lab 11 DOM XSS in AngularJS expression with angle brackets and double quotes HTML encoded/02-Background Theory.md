---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Background Theory

### What is AngularJS?

AngularJS is a JavaScript framework developed by Google for building dynamic web applications. It extends HTML with new attributes called directives, which allow developers to create custom HTML elements and bind data to the DOM. AngularJS uses two-way data binding, meaning changes in the model automatically update the view, and vice versa.

### How AngularJS Handles User Input

When user input is processed by AngularJS, it is typically rendered within the DOM using expressions enclosed in double curly braces (`{{ }}`). If this input is not properly sanitized or encoded, it can lead to XSS vulnerabilities. For instance, if an attacker injects a script tag (`<script>`) into the input, it could be executed by the browser.

### Encoding Angle Brackets and Double Quotes

To mitigate XSS attacks, web applications often encode special characters like angle brackets (`<`, `>`) and double quotes (`"`). However, this encoding can sometimes be bypassed, especially in frameworks like AngularJS that process user input dynamically.

### Example of DOM-Based XSS in AngularJS

Consider the following AngularJS template:

```html
<div ng-app>
  <input type="text" ng-model="searchTerm">
  <div>{{ searchTerm }}</div>
</div>
```

If an attacker inputs `<script>alert('XSS')</script>` into the `searchTerm` field, AngularJS will render this input within the DOM. Since the input is not properly sanitized, the script will be executed, leading to an XSS attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/03-Common Pitfalls and Detection|Common Pitfalls and Detection]]
