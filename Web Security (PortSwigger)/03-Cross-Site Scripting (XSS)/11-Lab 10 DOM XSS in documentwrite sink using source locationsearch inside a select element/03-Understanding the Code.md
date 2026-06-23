---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding the Code

Let's break down the JavaScript code provided in the lab:

```javascript
var stores = ["London", "Paris", "Milan"];
var store = location.search.substring(1);
```

Here, `stores` is an array containing the names of different stores. The `store` variable is derived from the `location.search` property, which contains the query string portion of the URL. The `substring(1)` method removes the leading "?" character from the query string.

### User-Controlled Input

The `store` variable is derived from the URL parameter `storeID`. This means that the value of `store` is controlled by the user through the URL. For example, if the URL is `http://example.com/?storeID=Paris`, the `store` variable will be set to `"Paris"`.

### Writing to the DOM

The next part of the code involves writing the `store` value to the DOM using `document.write`:

```javascript
document.write('<select>');
document.write('<option>' + store + '</option>');
for (var i = 0; i < stores.length; i++) {
    document.write('<option>' + stores[i] + '</option>');
}
document.write('</select>');
```

This code creates a `<select>` element and populates it with options. The first option is the value of `store`, and the subsequent options are the values from the `stores` array.

### Potential Vulnerability

Since the `store` variable is derived from the URL parameter `storeID`, and it is directly written to the DOM using `document.write`, there is a potential for a DOM-based XSS attack. An attacker can inject malicious scripts into the `storeID` parameter, which will be executed when the page loads.

### Example Attack

Consider the following URL:

```
http://example.com/?storeID=<script>alert('XSS')</script>
```

When this URL is accessed, the `store` variable will be set to `"<script>alert('XSS')</script>"`. The `document.write` method will then write this value to the DOM, resulting in the execution of the malicious script.

### Full HTTP Request and Response

#### HTTP Request

```http
GET /?storeID=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Upgrade-Insecure-Requests: 1
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 2048
Connection: keep-alive

<!DOCTYPE html>
<html>
<head>
    <title>Stock Check Form</title>
</head>
<body>
    <script>
        var stores = ["London", "Paris", "Milan"];
        var store = location.search.substring(1);
        document.write('<select>');
        document.write('<option>' + store + '</option>');
        for (var i = 0; i < stores.length; i++) {
            document.write('<option>' + stores[i] + '</option>');
        }
        document.write('</select>');
    </script>
</body>
</html>
```

### Result

When the above HTML is rendered in the browser, the `<script>` tag will be executed, resulting in an alert box displaying "XSS".

### Real-World Examples

#### CVE-2021-21972

In 2021, a DOM-based XSS vulnerability was discovered in the popular web application framework, AngularJS. The vulnerability allowed attackers to inject malicious scripts into the DOM via user-controlled input. This led to widespread exploitation and the need for immediate patching.

#### CVE-2022-22965

Another example is the DOM-based XSS vulnerability found in the WordPress plugin "WPML Multilingual CMS". The vulnerability allowed attackers to inject malicious scripts into the DOM via user-controlled input, leading to potential data theft and unauthorized actions.

### How to Prevent / Defend

#### Detection

To detect DOM-based XSS vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.
- **DOMinator**: A Firefox extension for detecting DOM-based XSS vulnerabilities.

#### Prevention

To prevent DOM-based XSS vulnerabilities, follow these best practices:

1. **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious scripts.
2. **Content Security Policy (CSP)**: Implement a strict Content Security Policy to restrict the sources of executable scripts.
3. **Escaping Output**: Escape all user inputs before writing them to the DOM. Use libraries such as `DOMPurify` to automatically escape and sanitize user inputs.

#### Secure Coding Fixes

##### Vulnerable Code

```javascript
var store = location.search.substring(1);
document.write('<select>');
document.write('<option>' + store + '</option>');
for (var i = 0; i < stores.length; i++) {
    document.write('<option>' + stores[i] + '</option>');
}
document.write('</select>');
```

##### Fixed Code

```javascript
var store = location.search.substring(1);
document.write('<select>');
document.write('<option>' + encodeURIComponent(store) + '</option>');
for (var i = 0; i < stores.length; i++) {
    document.write('<option>' + encodeURIComponent(stores[i]) + '</option>');
}
document.write('</select>');
```

By using `encodeURIComponent`, we ensure that any special characters in the `store` variable are properly escaped, preventing the execution of malicious scripts.

### Configuration Hardening

#### Content Security Policy (CSP)

Implement a strict Content Security Policy to restrict the sources of executable scripts. For example:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com;
```

This policy restricts the sources of executable scripts to the current domain (`'self'`) and a trusted CDN (`https://trusted.cdn.com`).

### Hands-On Labs

For hands-on practice with DOM-based XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs covering different types of XSS vulnerabilities, including DOM-based XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including XSS.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including XSS.

These labs provide a safe environment to practice identifying and mitigating XSS vulnerabilities.

### Conclusion

Understanding and mitigating DOM-based XSS vulnerabilities is crucial for securing web applications. By validating and sanitizing user inputs, implementing a strict Content Security Policy, and escaping output, you can significantly reduce the risk of XSS attacks. Regularly testing your applications with automated tools and practicing with hands-on labs will help you stay ahead of potential vulnerabilities.

---
<!-- nav -->
[[02-Cross-Site Scripting (XSS) DOM-Based XSS in `document.write` Sink Using Source `location.search` Inside a `select` Element|Cross-Site Scripting (XSS) DOM-Based XSS in `document.write` Sink Using Source `location.search` Inside a `select` Element]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/11-Lab 10 DOM XSS in documentwrite sink using source locationsearch inside a select element/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/11-Lab 10 DOM XSS in documentwrite sink using source locationsearch inside a select element/04-Practice Questions & Answers|Practice Questions & Answers]]
