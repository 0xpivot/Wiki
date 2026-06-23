---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Background Theory

To understand XSS, it's essential to know how browsers handle JavaScript and how web applications process user input. Browsers execute JavaScript within the context of a web page, and if an attacker can inject malicious JavaScript into a page, it will run with the privileges of that page.

### How XSS Works

1. **User Input**: A user inputs data into a form or URL parameter.
2. **Server Processing**: The server processes this input and includes it in the response.
3. **Browser Execution**: The browser executes the response, including any injected scripts.

### Example Scenario

Consider a search feature on a website where the search query is included in the response:

```plaintext
http://example.com/search?q=<script>alert('XSS')</script>
```

If the server does not sanitize the input, the response might look like this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for "<script>alert('XSS')</script>"</h1>
</body>
</html>
```

When the browser renders this HTML, it will execute the `<script>` tag, displaying an alert box.

### Real-World Examples

#### CVE-2021-21972

In 2021, a reflected XSS vulnerability was discovered in the WordPress REST API. Attackers could inject malicious scripts into comments, leading to unauthorized access and data theft.

#### CVE-2022-22965

Another example is the reflected XSS vulnerability found in the Atlassian Jira software. Attackers could inject scripts into URLs, compromising user sessions and stealing sensitive information.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/03-Exploiting the Vulnerability|Exploiting the Vulnerability]]
