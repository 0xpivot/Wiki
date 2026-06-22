---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Background Theory

### Understanding JavaScript Strings

JavaScript strings are sequences of characters enclosed in either single quotes (`'`) or double quotes (`"`). When a string is used in a JavaScript context, it can be manipulated and executed as part of the script.

#### Example of a JavaScript String

```javascript
var message = "Hello, World!";
```

### HTML Encoding

HTML encoding is a method of converting special characters into their corresponding HTML entities. This is done to ensure that characters like `<`, `>`, and `&` are interpreted correctly by the browser and not as part of HTML tags.

#### Common HTML Entities

- `<` is encoded as `&lt;`
- `>` is encoded as `&gt;`
- `&` is encoded as `&amp;`

### Reflected XSS Vulnerability

A reflected XSS vulnerability occurs when user input is included in the response sent back to the user without proper validation or encoding. This can happen in various contexts, such as search queries, error messages, or form submissions.

#### Example of Reflected XSS

Consider a web application that displays a search query in the response:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for: <?php echo $_GET['query']; ?></h1>
</body>
</html>
```

If an attacker injects a script tag into the query parameter, it can be executed by the browser:

```http
GET /search.php?query=<script>alert('XSS')</script>
```

The response would look like this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for: <script>alert('XSS')</script></h1>
</body>
</html>
```

This would cause the `alert` function to be executed in the user's browser.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/03-Exploiting the Vulnerability|Exploiting the Vulnerability]]
