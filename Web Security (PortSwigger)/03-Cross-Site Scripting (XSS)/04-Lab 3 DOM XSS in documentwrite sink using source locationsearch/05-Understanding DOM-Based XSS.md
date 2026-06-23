---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding DOM-Based XSS

DOM-based XSS occurs when a web application uses untrusted input to construct a DOM node or attribute value without proper sanitization. This can lead to the execution of arbitrary JavaScript code within the context of the victim's browser.

### Example Scenario

Let's consider the scenario described in the lecture:

1. A user enters a search query, e.g., "one two three four five six".
2. The search query is reflected back to the user in the HTML.
3. The search query is also included in the URL, specifically in the `location.search` parameter.

To understand this better, let's break down the components involved:

- **`location.search`**: This property returns the query string part of the URL, including the question mark (`?`). For example, if the URL is `https://example.com/search?q=one+two+three+four+five+six`, `location.search` would return `"?q=one+two+three+four+five+six"`.

- **`document.write`**: This method writes content directly into the HTML document. If the content includes untrusted input, it can lead to XSS vulnerabilities.

### Vulnerable Code Example

Consider the following JavaScript code snippet:

```javascript
// Vulnerable code
var searchTerm = location.search.substring(1); // Extract the query string
document.write('<img src="resources/images/tracker.gif" alt="' + searchTerm + '">');
```

This code takes the query string from the URL and writes it directly into the HTML document. If an attacker can inject malicious JavaScript into the query string, it can be executed in the context of the victim's browser.

### Real-World Example

A real-world example of DOM-based XSS can be seen in the case of a popular social media platform that was vulnerable to this type of attack. In 2019, a researcher discovered that the platform's search functionality was vulnerable to DOM-based XSS due to improper handling of user input. The researcher was able to inject a script that would steal the victim's session cookies, allowing the attacker to impersonate the victim.

---
<!-- nav -->
[[04-Understanding Cross-Site Scripting (XSS)|Understanding Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/06-Conclusion|Conclusion]]
