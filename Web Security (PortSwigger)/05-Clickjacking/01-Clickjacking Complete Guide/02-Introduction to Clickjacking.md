---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Introduction to Clickjacking

Clickjacking, also known as UI redressing, is a sophisticated web-based attack that tricks users into performing unintended actions on a webpage. This type of attack exploits the way browsers render web pages and the trust users place in familiar interfaces. By manipulating the visual layer of a web page, attackers can overlay hidden elements over legitimate ones, leading users to interact with the malicious interface instead of the intended one.

### What is Clickjacking?

At its core, clickjacking involves embedding a transparent or opaque iframe within a seemingly benign web page. This iframe contains the actual target of the user’s interaction, which is typically a sensitive action like deleting an account or submitting personal information. Users are unaware of the hidden iframe and believe they are interacting with the visible elements of the page.

### Why Does Clickjacking Matter?

Clickjacking poses significant risks because it can lead to unauthorized actions being performed by unsuspecting users. These actions can range from financial losses due to fraudulent transactions to data breaches involving sensitive personal information. The attack leverages the trust users have in familiar interfaces, making it particularly effective.

### How Does Clickjacking Work?

To understand clickjacking, let's break down the process:

1. **Attacker Registers a Malicious Domain**: The attacker creates a domain, such as `capsite.com`, which will serve as the platform for the attack.
2. **Embedding the Target Website**: Using HTML `<iframe>` tags, the attacker embeds the target website (e.g., a banking application) within the malicious domain.
3. **Overlaying Hidden Elements**: The attacker overlays hidden elements (such as buttons or links) over the embedded iframe. These elements are designed to look like legitimate parts of the webpage.
4. **User Interaction**: When a user interacts with what they believe to be a legitimate element, they are actually clicking on the hidden element, which triggers the malicious action.

### Real-World Example: Recent Breaches

One notable example of clickjacking occurred in 2019 when a phishing campaign targeted users of a popular social media platform. Attackers created a fake login page that overlaid the real login form, tricking users into entering their credentials into the malicious form. This resulted in thousands of accounts being compromised.

### Background Theory

To fully grasp clickjacking, it's essential to understand the underlying principles of web page rendering and user interaction.

#### Web Page Rendering

Web browsers render pages using a combination of HTML, CSS, and JavaScript. Each element on a page is positioned using CSS properties like `position`, `top`, `left`, etc. Frames and iframes allow web developers to embed content from other sources within a webpage.

#### User Interaction

Users interact with web pages through mouse clicks, keyboard inputs, and touch gestures. Browsers interpret these interactions and trigger corresponding events, such as `click` or `submit`.

### Detailed Example: Banking Application Attack

Let's delve deeper into the example provided in the lecture transcript.

#### Scenario Setup

Imagine a user has logged into their banking application. On the "My Accounts" page, there are two buttons:

1. **View Profile Button**: Displays the user's profile information.
2. **Delete Account Button**: Permanently deletes the user's account.

The banking application is vulnerable to clickjacking attacks.

#### Attacker's Steps

1. **Register Malicious Domain**: The attacker registers a domain, `capsite.com`.
2. **Create Malicious Page**: The attacker creates a webpage on `capsite.com` that includes an iframe pointing to the banking application.
3. **Overlay Hidden Elements**: The attacker overlays a hidden button over the "Delete Account" button within the iframe.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Malicious Site</title>
    <style>
        iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
        }
        .hidden-button {
            position: absolute;
            top: 100px; /* Adjust based on the actual position */
            left: 200px; /* Adjust based on the actual position */
            width: 100px;
            height: 50px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <iframe src="https://bankingapp.com/myaccounts"></iframe>
    <button class="hidden-button">Hidden Delete Button</button>
</body>
</html>
```

#### User Interaction

When the user visits `capsite.com`, they see what appears to be a normal webpage. However, when they click on what they believe to be a legitimate button, they are actually clicking on the hidden button, which triggers the deletion of their account.

### How to Prevent / Defend Against Clickjacking

Defending against clickjacking requires a multi-layered approach, including both server-side and client-side measures.

#### Server-Side Measures

1. **X-Frame-Options Header**: This HTTP header instructs browsers not to allow a page to be rendered within a frame. There are three possible values:
   - `DENY`: The page cannot be displayed in a frame.
   - `SAMEORIGIN`: The page can only be displayed in a frame on the same origin as the page itself.
   - `ALLOW-FROM uri`: The page can only be displayed in a frame on the specified URI.

   ```http
   HTTP/1.1 200 OK
   Content-Type: text/html
   X-Frame-Options: SAMEORIGIN
   ```

2. **Content Security Policy (CSP)**: CSP provides a mechanism to define which sources of content are allowed to be loaded on a web page. This can help prevent clickjacking by restricting the ability to load iframes from untrusted sources.

   ```http
   HTTP/1.1 200 OK
   Content-Type: text/html
   Content-Security-Policy: frame-ancestors 'self'
   ```

#### Client-Side Measures

1. **JavaScript Detection**: Implement JavaScript to detect if the page is being framed and redirect the user if it is.

   ```javascript
   if (window.self !== window.top) {
       window.location = "https://safe-site.com";
   }
   ```

2. **User Education**: Educate users about the risks of clickjacking and encourage them to verify the URL and context of the page they are interacting with.

### Secure Coding Practices

To prevent clickjacking, developers should follow secure coding practices:

1. **Use X-Frame-Options**: Ensure that the `X-Frame-Options` header is set appropriately for all pages.
2. **Implement CSP**: Use Content Security Policy to restrict the sources of content that can be loaded on a page.
3. **Avoid Unnecessary Iframes**: Minimize the use of iframes unless absolutely necessary and ensure they are properly secured.

### Vulnerable vs. Secure Code Examples

#### Vulnerable Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>Banking App</title>
</head>
<body>
    <h1>My Accounts</h1>
    <button onclick="viewProfile()">View Profile</button>
    <button onclick="deleteAccount()">Delete Account</button>
</body>
</html>
```

#### Secure Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>Banking App</title>
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
    <script>
        if (window.self !== window.top) {
            window.location = "https://safe-site.com";
        }
    </script>
</head>
<body>
    <h1>My Accounts</h1>
    <button onclick="viewProfile()">View Profile</button>
    <button onclick="deleteAccount()">Delete Account</button>
</body>
</html>
```

### Detection and Prevention Tools

Several tools and techniques can help detect and prevent clickjacking:

1. **Browser Extensions**: Use browser extensions that warn users when they are visiting a potentially dangerous site.
2. **Security Scanners**: Use automated security scanners to identify potential clickjacking vulnerabilities in web applications.
3. **Penetration Testing**: Regularly perform penetration testing to identify and mitigate clickjacking risks.

### Practice Labs

For hands-on practice with clickjacking, consider the following real-world labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

By understanding the mechanics of clickjacking and implementing robust defense mechanisms, organizations can significantly reduce the risk of this type of attack.

### Conclusion

Clickjacking is a sophisticated attack that exploits the trust users have in familiar interfaces. By embedding hidden elements within iframes, attackers can trick users into performing unintended actions. To defend against clickjacking, it is crucial to implement server-side and client-side measures, such as using the `X-Frame-Options` header and Content Security Policy. Additionally, educating users and following secure coding practices can further mitigate the risks associated with this type of attack.

### Further Reading

For a deeper dive into web security and clickjacking, consider the following resources:

- **OWASP Top Ten Project**: Provides detailed information on the most critical web application security risks.
- **PortSwigger Web Security Academy**: Offers comprehensive guides and interactive labs on various web security topics.
- **NIST Cybersecurity Framework**: Provides guidelines for managing cybersecurity risks.

By staying informed and proactive, organizations can protect themselves and their users from the dangers of clickjacking.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/01-Clickjacking A Comprehensive Guide|Clickjacking A Comprehensive Guide]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[03-What is Clickjacking|What is Clickjacking]]
