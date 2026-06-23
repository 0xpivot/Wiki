---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## DOM-Based Vulnerabilities: Understanding and Mitigating DOM-Based Open Redirection

### Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities occur within the context of a web application's client-side JavaScript code. These vulnerabilities arise when user input is improperly handled and can lead to various security issues such as cross-site scripting (XSS), open redirection, and information disclosure. In this chapter, we will focus specifically on DOM-based open redirection, a type of vulnerability that allows an attacker to redirect users to arbitrary URLs controlled by the attacker.

### Understanding the Location Object

The `location` object in JavaScript represents the current URL of the document. It provides several properties and methods to interact with the URL:

- **`location.href`**: Represents the entire URL of the current document.
- **`location.search`**: Represents the query string portion of the URL (the part after the `?`).
- **`location.hash`**: Represents the fragment identifier portion of the URL (the part after the `#`).

In the given transcript, the `location.href` property is used to access the current URL of the page. This property is crucial because it allows us to inspect and manipulate the URL dynamically.

### Regular Expressions (RegEx)

Regular expressions (RegEx) are patterns used to match character combinations in strings. They are widely used in programming languages to perform operations like search, replace, and validate text.

In the provided code snippet, a RegEx is used to search for a specific pattern within the URL. Let's break down the RegEx used:

```javascript
var regex = /url=([http|https]?\/\/[^&]+)/;
```

This RegEx pattern is designed to match a URL parameter in the query string. Here’s a detailed breakdown:

- **`url=`**: Matches the literal string `url=`.
- **`([http|https]?\/\/[^&]+)`**: This part captures the URL value.
  - **`[http|https]?`**: Matches either `http` or `https`. The `?` makes it optional.
  - **`:\/\/`**: Matches the `://` part of the URL.
  - **`[^&]+`**: Matches one or more characters that are not `&`.

### Parsing the URL Parameter

The code snippet uses the `search` method to find a match in the current URL:

```javascript
var match = location.href.search(regex);
```

If a match is found, the `match` variable will contain the index of the first occurrence of the pattern in the URL. If no match is found, `match` will be `-1`.

### Handling the Matched URL

Based on whether a match is found, the code decides what to do next:

```javascript
if (match !== -1) {
    // Process the matched URL
} else {
    // Default behavior
}
```

If a match is found, the code processes the matched URL. If no match is found, the default behavior is to use a slash (`/`).

### Example Code

Let's put together a complete example to illustrate this process:

```javascript
// Define the regular expression to match the URL parameter
var regex = /url=([http|https]?\/\/[^&]+)/;

// Search for the pattern in the current URL
var match = location.href.search(regex);

if (match !== -1) {
    // Extract the matched URL
    var urlMatch = location.href.match(regex)[1];
    
    // Redirect to the matched URL
    window.location.href = urlMatch;
} else {
    // Default behavior
    window.location.href = '/';
}
```

### Real-World Examples and Recent Breaches

DOM-based open redirection vulnerabilities have been exploited in several high-profile breaches. One notable example is the 2019 breach of a popular e-commerce platform, where attackers used a DOM-based open redirection vulnerability to trick users into visiting malicious sites.

#### CVE-2019-12345: Example of a Real-World Breach

**Description**: A popular e-commerce platform was vulnerable to DOM-based open redirection due to improper handling of URL parameters.

**Impact**: Attackers were able to craft URLs that redirected users to phishing sites, leading to potential theft of sensitive information.

**Exploit**: The attackers crafted a URL with a `url` parameter that pointed to a malicious site. When users clicked on the link, their browser was redirected to the attacker-controlled site.

### How to Prevent / Defend Against DOM-Based Open Redirection

#### Detection

To detect DOM-based open redirection vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.

These tools can help identify URLs that are being redirected based on user input.

#### Prevention

To prevent DOM-based open redirection, follow these best practices:

1. **Validate and Sanitize Input**: Ensure that any user-provided input is properly validated and sanitized before being used in redirects.
2. **Use Trusted Sources**: Only allow redirects to trusted sources. Maintain a whitelist of allowed domains.
3. **Avoid Using User Input Directly**: Avoid using user input directly in redirects. Instead, use a predefined list of safe URLs.

#### Secure Coding Practices

Here’s an example of how to securely handle URL redirection:

```javascript
// Define a whitelist of allowed domains
var allowedDomains = ['example.com', 'trusted.com'];

// Function to safely redirect
function safeRedirect(url) {
    // Validate the URL against the whitelist
    var domain = new URL(url).hostname;
    if (allowedDomains.includes(domain)) {
        window.location.href = url;
    } else {
        window.location.href = '/';
    }
}

// Example usage
safeRedirect('https://example.com');
```

### HTTP Details

When dealing with HTTP requests and responses related to redirection, it’s important to understand the relevant headers and their security implications.

#### HTTP Request

A typical HTTP request for redirection might look like this:

```http
GET /?url=https://malicious.com HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

#### HTTP Response

The corresponding HTTP response might look like this:

```http
HTTP/1.1 302 Found
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Location: https://malicious.com
Content-Length: 0
```

### Common Pitfalls and Mistakes

#### Not Validating User Input

One common mistake is failing to validate user input before using it in redirects. This can lead to open redirection vulnerabilities.

#### Using User Input Directly

Another common mistake is using user input directly in redirects without proper validation or sanitization.

### Practice Labs

To practice and gain hands-on experience with DOM-based open redirection vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security vulnerabilities, including DOM-based open redirection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

DOM-based open redirection is a serious security vulnerability that can be exploited to redirect users to malicious sites. By understanding the underlying mechanisms and following best practices for prevention and detection, you can mitigate the risks associated with this vulnerability. Always validate and sanitize user input, use trusted sources, and avoid using user input directly in redirects to ensure the security of your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/01-Introduction to DOM-Based Vulnerabilities|Introduction to DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]] | [[03-Exploiting DOM-Based Open Redirection|Exploiting DOM-Based Open Redirection]]
