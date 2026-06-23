---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding Reflected XSS

### What is Reflected XSS?

Reflected XSS occurs when the web application reflects user-supplied data back in the HTTP response without proper validation or sanitization. An attacker can craft a malicious URL that, when visited by a user, injects a script into the page.

### Why Does Reflected XSS Matter?

Reflected XSS is particularly dangerous because it can be used to trick users into executing arbitrary JavaScript code. This can lead to various attacks, including:

- **Stealing Cookies and Session Tokens**: Attackers can steal session cookies and hijack user sessions.
- **Phishing Attacks**: Malicious scripts can redirect users to fake login pages to capture their credentials.
- **Defacement**: Attackers can modify the appearance of the web page to display misleading information.

### How Does Reflected XSS Work?

Consider the following scenario:

1. A user visits a web page with a search field.
2. The user enters a search query, which is reflected back in the response.
3. An attacker crafts a malicious URL that includes a script tag.
4. The user clicks on the malicious URL, and the script is executed in their browser.

### Example of Reflected XSS

Let's take a look at a simple example:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Page</title>
</head>
<body>
    <form action="/search" method="GET">
        <input type="text" name="query" value="">
        <button type="submit">Search</button>
    </form>
    <div id="results">
        <?php echo htmlspecialchars($_GET['query']); ?>
    </div>
</body>
</html>
```

If the `htmlspecialchars` function is not used, an attacker could inject a script like this:

```
<script>alert('XSS');</script>
```

When the user submits this query, the script would be executed, displaying an alert box.

### Real-World Examples

Recent real-world examples of Reflected XSS include:

- **CVE-2021-21972**: A Reflected XSS vulnerability was found in the WordPress REST API, allowing attackers to inject malicious scripts into comments.
- **CVE-2022-22965**: A Reflected XSS vulnerability was discovered in the Drupal CMS, affecting versions prior to 9.3.10 and 8.9.20.

These vulnerabilities highlight the importance of proper input validation and output encoding to prevent XSS attacks.

---
<!-- nav -->
[[07-Setting Up the Lab Environment|Setting Up the Lab Environment]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/09-Practice Questions & Answers|Practice Questions & Answers]]
