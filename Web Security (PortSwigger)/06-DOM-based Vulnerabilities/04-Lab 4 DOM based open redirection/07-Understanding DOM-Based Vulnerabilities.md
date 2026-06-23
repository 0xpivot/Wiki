---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Understanding DOM-Based Vulnerabilities

DOM-based vulnerabilities occur when a web application uses untrusted input to manipulate the Document Object Model (DOM) in a way that can lead to security issues. These vulnerabilities are often overlooked because they do not involve server-side processing; instead, they rely on client-side JavaScript to execute malicious actions. One common type of DOM-based vulnerability is DOM-based open redirection, where an attacker can trick users into visiting a malicious site through a crafted URL.

### What is DOM-Based Open Redirection?

DOM-based open redirection occurs when a web application uses a URL parameter to redirect the user to another page. If the URL parameter is not properly validated, an attacker can inject a malicious URL, causing the browser to redirect the user to a potentially harmful site.

#### Example Scenario

Consider a web application that uses a URL parameter to redirect users back to the main blog page. The URL might look like this:

```
https://example.com/blog?redirect=https://test.ca
```

The application takes the `redirect` parameter and uses it to redirect the user. If the parameter is not validated, an attacker could craft a URL like this:

```
https://example.com/blog?redirect=https://malicious-site.com
```

When the user clicks on this link, the browser will redirect them to the malicious site.

### Background Theory

To understand how DOM-based open redirection works, we need to delve into how the DOM is manipulated by JavaScript. The DOM is a tree-like structure that represents the HTML document. JavaScript can interact with the DOM to modify its contents, including changing the location of the current page.

#### How the DOM is Manipulated

JavaScript can access and modify the DOM using various methods. For example, the `window.location` object provides properties and methods to get and set the current URL. An attacker can exploit this by injecting a malicious URL into the `window.location.href` property.

### Real-World Examples

Recent real-world examples of DOM-based open redirection include several high-profile breaches. For instance, a vulnerability was found in a popular blogging platform where an attacker could craft a URL to redirect users to a phishing site. This led to widespread phishing attacks targeting users of the platform.

Another example is a vulnerability found in a financial institution's website, where an attacker could redirect users to a fake login page, stealing their credentials.

### Detailed Example

Let's take a detailed look at the example provided in the lecture transcript. We'll break down the steps and explain the underlying mechanisms.

#### Initial Setup

The initial URL is:

```
https://example.com/blog?redirect=https://test.ca
```

When the user visits this URL, the browser sends a request to the server:

```http
GET /blog?redirect=https://test.ca HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
```

The server responds with the HTML content of the page:

```http
HTTP/1.1 200 OK
Date: Mon, 14 Jun 2021 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Blog</title>
</head>
<body>
    <script>
        // JavaScript code to handle the redirection
        var url = new URL(window.location.href);
        var redirectUrl = url.searchParams.get('redirect');
        if (redirectUrl) {
            window.location.href = redirectUrl;
        }
    </script>
    <a href="#" onclick="window.location.href = 'https://example.com/blog';">Back to Blog</a>
</body>
</html>
```

#### JavaScript Execution

The JavaScript code in the `<script>` tag executes when the page loads. It parses the URL to extract the `redirect` parameter and redirects the user to the specified URL.

```javascript
var url = new URL(window.location.href);
var redirectUrl = url.searchParams.get('redirect');
if (redirectUrl) {
    window.location.href = redirectUrl;
}
```

If the `redirect` parameter is present, the user is redirected to the specified URL. In this case, the user is redirected to `https://test.ca`.

### Pitfalls and Common Mistakes

One common mistake is not validating the `redirect` parameter before using it. This allows an attacker to inject a malicious URL. Another pitfall is relying solely on client-side validation, as an attacker can bypass it by manipulating the DOM directly.

### How to Prevent / Defend

To prevent DOM-based open redirection, follow these steps:

1. **Validate Input**: Ensure that the `redirect` parameter is validated before using it. Only allow trusted URLs.
2. **Use Whitelisting**: Maintain a list of allowed domains and only redirect to URLs within those domains.
3. **Secure Coding Practices**: Implement secure coding practices to avoid client-side vulnerabilities.
4. **Detection**: Use tools like static analysis and dynamic analysis to detect potential vulnerabilities.
5. **Configuration Hardening**: Harden the server configuration to prevent unauthorized access.

#### Secure Code Example

Here is an example of how to securely handle the `redirect` parameter:

```javascript
var url = new URL(window.location.href);
var redirectUrl = url.searchParams.get('redirect');
var allowedDomains = ['example.com', 'trusteddomain.com'];

if (redirectUrl && allowedDomains.includes(new URL(redirectUrl).hostname)) {
    window.location.href = redirectUrl;
} else {
    window.location.href = 'https://example.com/blog';
}
```

In this example, the `redirectUrl` is checked against a list of allowed domains before being used. If the domain is not in the list, the user is redirected to a safe URL.

### Conclusion

DOM-based open redirection is a serious vulnerability that can be exploited to redirect users to malicious sites. By understanding the underlying mechanisms and implementing proper validation and secure coding practices, you can prevent such attacks. Always validate input, use whitelisting, and implement secure coding practices to ensure the safety of your web applications.

### Practice Labs

For hands-on practice with DOM-based vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including DOM-based vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide real-world scenarios and challenges to help you master the concepts and techniques discussed in this chapter.

---
<!-- nav -->
[[06-Understanding DOM-Based Open Redirection|Understanding DOM-Based Open Redirection]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/08-Practice Questions & Answers|Practice Questions & Answers]]
