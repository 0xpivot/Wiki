---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Content Security Policy Cheat Sheet

Before diving into the specifics of the Cross-Site Scripting (XSS) cheat sheet, it's essential to understand the role of Content Security Policy (CSP) in web security. CSP is an added layer of security that helps to detect and mitigate certain types of attacks, including Cross-Site Scripting (XSS) and data injection attacks. It allows web site administrators to inform browsers not to execute scripts that do not originate from trusted sources.

### What is Content Security Policy?

Content Security Policy is a security standard that helps to detect and mitigate certain types of attacks, including Cross-Site Scripting (XSS) and data injection attacks. It allows web site administrators to inform browsers not to execute scripts that do not originate from trusted sources. This is achieved by specifying a set of rules that define which sources of content are allowed to be executed within a web page.

#### How Does CSP Work?

CSP works by defining a set of directives that specify the sources of content that are allowed to be loaded and executed within a web page. These directives are sent to the browser via the `Content-Security-Policy` HTTP header. The browser then enforces these policies by blocking any content that violates the specified rules.

For example, consider the following CSP header:

```http
Content-Security-Policy: default-src 'self'
```

This directive specifies that the default source for all content should be the same origin as the web page itself. This means that any content that is not served from the same origin will be blocked.

### Importance of CSP in Web Security

CSP is crucial in web security because it provides an additional layer of protection against various types of attacks. By limiting the sources of content that can be loaded and executed within a web page, CSP helps to prevent malicious scripts from being executed, thereby reducing the risk of XSS and other data injection attacks.

### Real-World Example: CVE-2021-21972

One real-world example of the importance of CSP is the CVE-2021-21972 vulnerability in the WordPress plugin WPML Multilingual CMS. This vulnerability allowed attackers to inject malicious scripts into the website, leading to a potential XSS attack. However, due to the presence of a properly configured CSP, the attack was mitigated, preventing the execution of the injected script.

### Content Security Policy Cheat Sheet

The Content Security Policy cheat sheet is a valuable resource that provides detailed information on how to configure and implement CSP effectively. It includes a comprehensive list of directives and their usage, along with examples and best practices.

### Cross-Site Scripting Cheat Sheet by PortSwigger

Now, let's move on to the Cross-Site Scripting (XSS) cheat sheet by PortSwigger. This cheat sheet is an invaluable resource for understanding and exploiting XSS vulnerabilities. It provides a detailed list of HTML tags that can be used to perform XSS attacks, along with the events and attributes associated with each tag.

#### What is Cross-Site Scripting (XSS)?

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. XSS enables attackers to inject client-side scripts into web pages viewed by other users. A successful exploitation of an XSS vulnerability can lead to various harmful actions, such as stealing cookies, session tokens, and other sensitive information.

#### Types of XSS Vulnerabilities

There are three main types of XSS vulnerabilities:

1. **Reflected XSS**: In this type of attack, the malicious script comes from the current HTTP request. Reflected XSS is often delivered via phishing emails or malicious links.
   
2. **Stored XSS**: In stored XSS, the malicious script is permanently stored on the target servers, such as in a database, comment field, visitor log, etc. The victim retrieves the malicious script when they access the stored information.
   
3. **DOM-based XSS**: DOM-based XSS occurs when the vulnerability exists in client-side code rather than server-side code. The attacker manipulates the Document Object Model (DOM) to inject malicious scripts.

### HTML Tags and Attributes for XSS

The XSS cheat sheet by PortSwigger provides a comprehensive list of HTML tags and attributes that can be used to perform XSS attacks. Here are some key examples:

#### `<script>` Tag

The `<script>` tag is commonly used to inject JavaScript code into a web page. For example:

```html
<script>alert('XSS');</script>
```

This script will pop up an alert box with the message "XSS".

#### `<img>` Tag

The `<img>` tag can be used to load external images, but it can also be used to trigger JavaScript code. For example:

```html
<img src="x" onerror="alert('XSS')">
```

If the image source (`src`) is invalid, the `onerror` event will trigger the JavaScript code.

#### `<a>` Tag

The `<a>` tag can be used to create hyperlinks. However, it can also be used to trigger JavaScript code. For example:

```html
<a href="javascript:alert('XSS')">Click Me</a>
```

When the link is clicked, the JavaScript code will be executed.

### Events and Attributes

Each HTML tag can have various events and attributes that can be exploited for XSS attacks. For example:

- **`onclick`**: Triggers when the user clicks on an element.
- **`onmouseover`**: Triggers when the mouse pointer moves over an element.
- **`onload`**: Triggers when the document finishes loading.

### Real-World Example: CVE-2021-21972

Continuing with the example of CVE-2021-21972, the vulnerability in the WPML Multilingual CMS plugin allowed attackers to inject malicious scripts into the website. The attacker could exploit this vulnerability by injecting a script like the following:

```html
<script>alert('XSS');</script>
```

However, due to the presence of a properly configured CSP, the attack was mitigated, preventing the execution of the injected script.

### How to Prevent / Defend Against XSS

Preventing XSS attacks involves both server-side and client-side measures. Here are some key strategies:

#### Server-Side Prevention

1. **Input Validation**: Validate all user inputs to ensure they do not contain malicious scripts.
2. **Output Encoding**: Encode all user inputs before displaying them on the web page. This ensures that any potentially malicious scripts are rendered harmless.
3. **Content Security Policy (CSP)**: Implement a strong CSP to restrict the sources of content that can be loaded and executed within a web page.

#### Client-Side Prevention

1. **JavaScript Libraries**: Use libraries like DOMPurify to sanitize user inputs and prevent XSS attacks.
2. **Browser Features**: Utilize browser features like the `Content-Security-Policy` header to enforce strict security policies.

### Secure Coding Practices

Here are some secure coding practices to prevent XSS attacks:

#### Vulnerable Code Example

```php
<?php
$user_input = $_GET['input'];
echo "<div>$user_input</div>";
?>
```

In this example, the user input is directly echoed into the HTML, making it susceptible to XSS attacks.

#### Secure Code Example

```php
<?php
$user_input = $_GET['input'];
$sanitized_input = htmlspecialchars($user_input, ENT_QUOTES, 'UTF-8');
echo "<div>$sanitized_input</div>";
?>
```

In this example, the `htmlspecialchars` function is used to encode the user input, ensuring that any potentially malicious scripts are rendered harmless.

### Configuration Hardening

To further harden your web application against XSS attacks, consider implementing the following configurations:

#### Content Security Policy (CSP)

Configure the `Content-Security-Policy` header to restrict the sources of content that can be loaded and executed within a web page. For example:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-source.com
```

This directive specifies that the default source for all content should be the same origin as the web page itself, and that scripts can only be loaded from the same origin or from a trusted source.

### Detection and Mitigation

Detecting and mitigating XSS attacks involves both proactive and reactive measures. Here are some key strategies:

#### Proactive Measures

1. **Code Reviews**: Regularly review code for potential XSS vulnerabilities.
2. **Automated Tools**: Use automated tools like static code analyzers and dynamic analysis tools to identify potential XSS vulnerabilities.

#### Reactive Measures

1. **Logging and Monitoring**: Monitor web application logs for signs of suspicious activity.
2. **Incident Response**: Have a well-defined incident response plan in place to quickly address any detected XSS attacks.

### Hands-On Labs

To gain practical experience with XSS vulnerabilities, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs to practice and learn about XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application designed to teach web application security.

By practicing in these environments, you can gain a deeper understanding of how to identify, exploit, and prevent XSS vulnerabilities.

### Conclusion

Understanding and preventing Cross-Site Scripting (XSS) vulnerabilities is crucial for maintaining the security of web applications. By leveraging resources like the Content Security Policy cheat sheet and the Cross-Site Scripting cheat sheet by PortSwigger, you can gain a comprehensive understanding of how to identify and exploit XSS vulnerabilities. Additionally, by implementing secure coding practices, configuring strong security policies, and regularly monitoring for suspicious activity, you can effectively mitigate the risks associated with XSS attacks.

---
<!-- nav -->
[[03-Bypassing XSS Filters|Bypassing XSS Filters]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[05-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]]
