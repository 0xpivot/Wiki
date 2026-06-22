---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding the Lab Scenario

In this lab, we will focus on a specific type of Reflected XSS where the input is reflected back into an HTML attribute and the angle brackets are HTML-encoded. This scenario is particularly interesting because it requires careful handling of input encoding to prevent the execution of malicious scripts.

### Scenario Breakdown

1. **Input Reflection**: The input provided by the user is reflected back in the `h1` element and the `value` attribute of an input element.
2. **HTML Encoding**: The angle brackets (`<` and `>`) are URL-encoded (`%3C` and `%3E`), which prevents the immediate execution of the script but does not necessarily protect against all forms of XSS.

### Example Input

Let's consider the following input:

```plaintext
test<script>alert('XSS')</script>
```

When this input is submitted, the server reflects it back in the following manner:

```html
<h1>Search Results for: test&lt;script&gt;alert('XSS')&lt;/script&gt;</h1>
<input type="text" value="test&lt;script&gt;alert('XSS')&lt;/script&gt;">
```

Notice how the angle brackets are HTML-encoded (`&lt;` and `&gt;`). This encoding prevents the script from being executed immediately, but it does not guarantee safety from XSS attacks.

---
<!-- nav -->
[[11-Understanding the Lab Environment|Understanding the Lab Environment]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/13-Conclusion|Conclusion]]
