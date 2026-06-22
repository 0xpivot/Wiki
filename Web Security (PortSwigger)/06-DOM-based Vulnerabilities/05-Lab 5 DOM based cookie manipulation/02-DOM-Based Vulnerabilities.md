---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## DOM-Based Vulnerabilities

### Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities occur when a web application processes user input in the browser's Document Object Model (DOM) without proper validation or sanitization. These vulnerabilities can lead to various attacks such as Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), and information leakage. In this section, we will focus on DOM-based XSS vulnerabilities, specifically how attackers can manipulate cookies through URL parameters.

### Understanding the DOM

The Document Object Model (DOM) is a programming interface for web documents. It represents the document as a tree structure, where each node is an object representing parts of the document. This allows scripts to dynamically access and modify the content, structure, and style of a document.

#### Key Concepts in the DOM

- **Nodes**: Each piece of the document is represented as a node. Nodes can be elements, attributes, text, comments, etc.
- **Element Nodes**: Represent HTML tags and their contents.
- **Attribute Nodes**: Represent attributes of an element.
- **Text Nodes**: Represent text inside elements.

### DOM-Based XSS Overview

DOM-based XSS occurs when an attacker manipulates the DOM to inject malicious scripts into a web page. Unlike traditional XSS, where the server is responsible for injecting the script, DOM-based XSS relies on client-side JavaScript to execute the malicious code.

#### How DOM-Based XSS Works

1. **User Input**: An attacker injects malicious data into a URL parameter.
2. **DOM Manipulation**: The web application reads the URL parameter and uses it to modify the DOM.
3. **Execution**: The modified DOM executes the injected script, leading to potential security issues.

### Example: DOM-Based Cookie Manipulation

Let's consider a scenario where an attacker manipulates the URL to inject a malicious script into a cookie. The web application reads the URL parameter and saves it in a cookie, which is then used to render the page.

#### Step-by-Step Explanation

1. **URL Parameter Injection**:
    - The attacker modifies the URL to include a malicious script.
    - Example URL: `http://example.com/product?lastViewedProduct=<script>alert('XSS')</script>`

2. **Reading the URL Parameter**:
    - The web application reads the `lastViewedProduct` parameter from the URL.
    - Example JavaScript:
      ```javascript
      var lastViewedProduct = window.location.search.split('lastViewedProduct=')[1];
      ```

3. **Saving the Parameter in a Cookie**:
    - The web application saves the `lastViewedProduct` value in a cookie.
    - Example JavaScript:
      ```javascript
      document.cookie = "lastViewedProduct=" + lastViewedProduct;
      ```

4. **Rendering the Page**:
    - The web application reads the cookie and renders the page.
    - Example JavaScript:
      ```javascript
      var cookieValue = document.cookie.split(';').find(c => c.trim().startsWith('lastViewedProduct=')).split('=')[1];
      document.getElementById('productInfo').innerHTML = cookieValue;
      ```

### Exploiting the Vulnerability

To exploit this vulnerability, an attacker can use an `<iframe>` to load the application multiple times with different URL parameters. This allows the attacker to inject a malicious script into the cookie and have it executed when the page is rendered.

#### Example Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>DOM-Based XSS Exploit</title>
</head>
<body>
    <iframe id="exploitFrame" src="http://example.com/product?lastViewedProduct=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E"></iframe>
    <script>
        var iframe = document.getElementById('exploitFrame');
        iframe.onload = function() {
            // Unload the iframe to reset the state
            iframe.src = "http://example.com";
        };
    </script>
</body>
</html>
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A DOM-based XSS vulnerability was found in the WordPress plugin "WP GDPR Compliance." Attackers could inject malicious scripts into the plugin settings, leading to potential data theft.
- **CVE-2022-22965**: A DOM-based XSS vulnerability was discovered in the popular web application framework Django. Attackers could inject malicious scripts into URL parameters, leading to unauthorized access and data theft.

### How to Prevent / Defend Against DOM-Based XSS

#### Detection

- **Static Analysis Tools**: Use tools like ESLint, SonarQube, and Bandit to scan your code for potential DOM-based XSS vulnerabilities.
- **Dynamic Analysis Tools**: Use tools like Burp Suite, ZAP, and OWASP ZAP to test your application for runtime vulnerabilities.

#### Prevention

- **Input Validation**: Validate and sanitize all user inputs before using them in the DOM.
- **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources of executable scripts.
- **HTTP Headers**: Use HTTP headers like `X-XSS-Protection` and `Content-Security-Policy` to mitigate XSS attacks.

#### Secure Coding Practices

- **Use Template Literals Safely**: Avoid directly inserting user input into template literals.
  ```javascript
  // Vulnerable code
  document.getElementById('productInfo').innerHTML = `${userInput}`;

  // Secure code
  document.getElementById('productInfo').textContent = userInput;
  ```

- **Escape User Input**: Escape user input before rendering it in the DOM.
  ```javascript
  function escapeHtml(unsafe) {
      return unsafe
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
  }

  document.getElementById('productInfo').innerHTML = escapeHtml(userInput);
  ```

### Complete Example with Raw HTTP Messages

#### Vulnerable Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Application</title>
</head>
<body>
    <div id="productInfo"></div>
    <script>
        var lastViewedProduct = window.location.search.split('lastViewedProduct=')[1];
        document.cookie = "lastViewedProduct=" + lastViewedProduct;
        var cookieValue = document.cookie.split(';').find(c => c.trim().startsWith('lastViewedProduct=')).split('=')[1];
        document.getElementById('productInfo').innerHTML = cookieValue;
    </script>
</body>
</html>
```

#### Secure Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>Secure Application</title>
</head>
<body>
    <div id="productInfo"></div>
    <script>
        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        var lastViewedProduct = window.location.search.split('lastViewedProduct=')[1];
        document.cookie = "lastViewedProduct=" + escapeHtml(lastView_iewedProduct);
        var cookieValue = document.cookie.split(';').find(c => c.trim().startsWith('lastViewedProduct=')).split('=')[1];
        document.getElementById('productInfo').textContent = escapeHtml(cookieValue);
    </script>
</body>
</html>
```

### HTTP Requests and Responses

#### Vulnerable Request

```http
GET /product?lastViewedProduct=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

#### Vulnerable Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Application</title>
</head>
<body>
    <div id="productInfo"><script>alert('XSS')</script></div>
    <script>
        var lastViewedProduct = window.location.search.split('lastViewedProduct=')[1];
        document.cookie = "lastViewedProduct=" + lastViewedProduct;
        var cookieValue = document.cookie.split(';').find(c => c.trim().startsWith('lastViewedProduct=')).split('=')[1];
        document.getElementById('productInfo').innerHTML = cookieValue;
    </script>
</body>
</html>
```

#### Secure Request

```http
GET /product?lastViewedProduct=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E HTTP/1.1
Host: example.com
```

#### Secure Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Secure Application</title>
</head>
<body>
    <div id="productInfo">&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;</div>
    <script>
        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        var lastViewedProduct = window.location.search.split('lastViewedProduct=')[1];
        document.cookie = "lastViewedProduct=" + escapeHtml(lastViewedProduct);
        var cookieValue = document.cookie.split(';').find(c => c.trim().startsWith('lastViewedProduct=')).split('=')[1];
        document.getElementById('productInfo').textContent = escapeHtml(cookieValue);
    </script>
</body>
</html>
```

### Practice Labs

For hands-on practice with DOM-based vulnerabilities, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various types of XSS vulnerabilities, including DOM-based XSS.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several DOM-based XSS challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including DOM-based XSS, for educational purposes.

By thoroughly understanding and practicing the concepts covered in this chapter, you will be better equipped to identify, exploit, and defend against DOM-based vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/01-Introduction to DOM-Based Vulnerabilities|Introduction to DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/00-Overview|Overview]] | [[03-How to Prevent  Defend Against DOM-Based Vulnerabilities|How to Prevent  Defend Against DOM-Based Vulnerabilities]]
