---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## What is Cross-Site Scripting (XSS)?

Cross-Site Scripting (XSS) is a type of security vulnerability that occurs when an attacker manages to inject malicious scripts into a trusted website. These scripts are then executed in the victim's browser, leading to potential security risks such as data theft, session hijacking, and more. Unlike server-side vulnerabilities like SQL Injection, XSS is a client-side issue, meaning the malicious script runs on the user's browser rather than the server.

### Why Does XSS Matter?

XSS is significant because it can compromise user data and privacy. Attackers can use XSS to steal cookies, session tokens, and other sensitive information. This can lead to unauthorized access to user accounts, financial losses, and reputational damage. For instance, a recent breach involving XSS was reported in the CVE-2021-39225, where a vulnerability in the WordPress plugin "WPML Multilingual CMS" allowed attackers to inject malicious scripts into the site, potentially compromising user data.

### How Does XSS Work Under the Hood?

To understand XSS, it's essential to grasp the basics of how web applications work. A typical web interaction involves:

1. **User Request**: The user sends a request to the server.
2. **Server Response**: The server processes the request and sends back a response, often containing HTML, CSS, and JavaScript.
3. **Browser Execution**: The user's browser parses the response and executes any embedded scripts.

In an XSS scenario, the attacker injects malicious scripts into the server's response. When the victim's browser renders the page, it executes the injected script, leading to potential security issues.

#### Example of an XSS Attack

Consider a simple search feature on a website. The search query is reflected back in the response. An attacker could inject a script like this:

```html
<script>alert('XSS')</script>
```

If the website does not properly sanitize the input, the script will be executed in the victim's browser, displaying an alert box.

### Types of XSS Vulnerabilities

There are three main types of XSS vulnerabilities:

1. **Reflected XSS**
2. **Stored XSS**
3. **DOM-Based XSS**

#### Reflected XSS

**Definition**: Reflected XSS occurs when the malicious script comes from the current HTTP request. The attacker tricks the victim into clicking a malicious link or submitting a form that contains the script.

**Example**: Consider a search feature where the query is reflected in the URL. An attacker could craft a URL like this:

```
http://example.com/search?q=<script>alert('XSS')</script>
```

When the victim clicks this link, the script is executed in their browser.

**Detection**: Reflected XSS can be detected using automated tools like Burp Suite or OWASP ZAP. These tools can simulate user interactions and check for script execution.

**Prevention**: To prevent reflected XSS, ensure that all user inputs are properly sanitized and validated. Use Content Security Policy (CSP) to restrict the sources of executable scripts.

#### Stored XSS

**Definition**: Stored XSS occurs when the malicious script is permanently stored on the server, such as in a database, and served to users over time.

**Example**: Consider a comment section where users can post comments. An attacker could post a comment with a script like this:

```html
<script>alert('XSS')</script>
```

Whenever a user views the comment, the script is executed in their browser.

**Detection**: Stored XSS can be detected by reviewing the application's storage mechanisms and checking for unsanitized user inputs. Automated tools like Burp Suite can also help identify stored XSS vulnerabilities.

**Prevention**: To prevent stored XSS, ensure that all user inputs are properly sanitized and validated before storing them. Use output encoding to escape special characters in user inputs.

#### DOM-Based XSS

**Definition**: DOM-based XSS occurs when the vulnerability exists in the client-side code rather than the server-side code. The script is executed based on the Document Object Model (DOM).

**Example**: Consider a JavaScript function that sets the innerHTML of an element based on a URL parameter:

```javascript
function displayMessage() {
    var param = window.location.href.split('=')[1];
    document.getElementById('message').innerHTML = param;
}
```

An attacker could craft a URL like this:

```
http://example.com/page.html?msg=<script>alert('XSS')</script>
```

When the victim visits this URL, the script is executed in their browser.

**Detection**: DOM-based XSS can be detected by reviewing the client-side code and identifying areas where user inputs are used to modify the DOM. Automated tools like DOMinator can help identify DOM-based XSS vulnerabilities.

**Prevention**: To prevent DOM-based XSS, ensure that all user inputs are properly sanitized and validated before being used to modify the DOM. Use Content Security Policy (CSP) to restrict the sources of executable scripts.

### Real-World Examples of XSS Attacks

#### CVE-2021-39225: WPML Multilingual CMS

In 2021, a vulnerability was discovered in the WPML Multilingual CMS plugin for WordPress. The vulnerability allowed attackers to inject malicious scripts into the site, potentially compromising user data. This is an example of a stored XSS vulnerability.

#### CVE-2020-14182: Shopify

In 2020, a vulnerability was discovered in Shopify, allowing attackers to inject malicious scripts into the site. This is an example of a reflected XSS vulnerability.

### How to Find and Exploit XSS Vulnerabilities

To find and exploit XSS vulnerabilities, you need to understand how to test web applications for these vulnerabilities. Here are some steps to follow:

1. **Identify User Inputs**: Look for places where user inputs are accepted, such as forms, URLs, and cookies.
2. **Inject Test Scripts**: Inject test scripts like `<script>alert('XSS')</script>` to see if they are executed.
3. **Use Automated Tools**: Use tools like Burp Suite and OWASP ZAP to automate the process of finding and exploiting XSS vulnerabilities.
4. **Review Client-Side Code**: Review the client-side code to identify areas where user inputs are used to modify the DOM.

#### Example of Finding and Exploiting XSS

Consider a search feature where the query is reflected in the URL. You can use Burp Suite to intercept the request and inject a test script:

```http
GET /search?q=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

If the script is executed in the browser, you have found a reflected XSS vulnerability.

### Bypassing Defenses

Developers often implement various defenses to prevent XSS attacks. However, attackers can sometimes bypass these defenses. Here are some common defenses and how to bypass them:

#### Content Security Policy (CSP)

**Defense**: CSP restricts the sources of executable scripts. For example:

```http
Content-Security-Policy: script-src 'self'
```

**Bypass**: Attackers can sometimes bypass CSP by using inline scripts or by exploiting other vulnerabilities to inject scripts from allowed sources.

#### Output Encoding

**Defense**: Output encoding ensures that special characters in user inputs are escaped. For example:

```javascript
document.getElementById('message').innerHTML = encodeURI(param);
```

**Bypass**: Attackers can sometimes bypass output encoding by using alternative encoding methods or by exploiting other vulnerabilities to inject scripts.

### How to Prevent / Defend Against XSS

To prevent XSS attacks, you need to implement a combination of defensive measures. Here are some steps to follow:

1. **Sanitize User Inputs**: Ensure that all user inputs are properly sanitized and validated before being used in the application.
2. **Use Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.
3. **Output Encoding**: Use output encoding to escape special characters in user inputs.
4. **Automated Testing**: Use automated tools like Burp Suite and OWASP ZAP to test for XSS vulnerabilities.
5. **Code Reviews**: Conduct regular code reviews to identify and fix XSS vulnerabilities.

#### Example of Secure Coding Practices

Consider a search feature where the query is reflected in the URL. Here is an example of how to securely handle user inputs:

```javascript
// Vulnerable code
function displaySearchResults(query) {
    document.getElementById('results').innerHTML = query;
}

// Secure code
function displaySearchResults(query) {
    document.getElementById('results').textContent = query;
}
```

In the secure code, `textContent` is used instead of `innerHTML`, preventing the execution of any scripts.

### Conclusion

Cross-Site Scripting (XSS) is a significant security vulnerability that can compromise user data and privacy. Understanding the different types of XSS vulnerabilities, how to find and exploit them, and how to prevent them is crucial for securing web applications. By implementing proper defensive measures and conducting regular testing, you can significantly reduce the risk of XSS attacks.

### Practice Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and practice XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for learning web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application to teach web security.

These labs provide a safe environment to practice and learn about XSS vulnerabilities and how to defend against them.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[03-Bypassing XSS Filters|Bypassing XSS Filters]]
