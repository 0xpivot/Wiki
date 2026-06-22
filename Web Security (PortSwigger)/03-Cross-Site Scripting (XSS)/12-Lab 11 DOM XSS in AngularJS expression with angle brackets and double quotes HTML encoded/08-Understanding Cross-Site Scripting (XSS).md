---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker can inject malicious scripts into a webpage viewed by other users. These scripts can perform actions such as stealing cookies, session tokens, and other sensitive information. There are three main types of XSS vulnerabilities:

1. **Stored XSS**: Malicious scripts are stored on the server and served to users.
2. **Reflected XSS**: Malicious scripts are reflected off the server in response to user input.
3. **DOM-Based XSS**: Malicious scripts are executed within the browser due to the way the application manipulates the Document Object Model (DOM).

### DOM-Based XSS in AngularJS

In the context of AngularJS, DOM-based XSS can occur when user input is used to manipulate the DOM in a way that allows script execution. This often happens when user input is inserted into the DOM without proper sanitization.

#### Example Scenario

Consider a web application using AngularJS where user input is used to set the value of an HTML element. If the input is not properly sanitized, an attacker could inject a script tag that would execute in the context of the victim's browser.

```html
<div ng-app>
  <input type="text" ng-model="message">
  <div>{{message}}</div>
</div>
```

If an attacker inputs `"><script>alert('XSS')</script>`, the resulting DOM might look like this:

```html
<div ng-app>
  <input type="text" ng-model="message">
  <div">><script>alert('XSS')</script></div>
</div>
```

This would cause the script to execute, potentially leading to an XSS attack.

### Lab Exercise: DOM XSS in AngularJS Expression

In the lab exercise, you were tasked with exploiting a DOM-based XSS vulnerability in an AngularJS application. Let's break down the steps involved:

1. **Identify the Vulnerable Input**:
   - Look for user inputs that are directly inserted into the DOM.
   - In this case, the input field was used to set the value of an HTML element.

2. **Craft the Exploit**:
   - Inject a script tag into the input field.
   - Ensure the script tag is properly formatted to bypass any basic sanitization.

3. **Trigger the Exploit**:
   - Submit the input and observe the behavior.
   - If successful, the injected script will execute, leading to the exploitation of the vulnerability.

#### Complete Example

Here is a more detailed example of the lab exercise:

```html
<!DOCTYPE html>
<html ng-app>
<head>
  <title>AngularJS DOM XSS Lab</title>
  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.2/angular.min.js"></script>
</head>
<body>
  <div ng-controller="MyController">
    <input type="text" ng-model="message">
    <div>{{message}}</div>
  </div>

  <script>
    angular.module('myApp', [])
      .controller('MyController', function($scope) {
        $scope.message = '';
      });
  </script>
</body>
</html>
```

To exploit this, an attacker could input the following into the text field:

```html
"><script>alert('XSS')</script>
```

The resulting DOM would look like this:

```html
<div ng-app>
  <div ng-controller="MyController">
    <input type="text" ng-model="message">
    <div">><script>alert('XSS')</script></div>
  </div>
</div>
```

This would cause the `alert('XSS')` script to execute.

### Real-World Examples

Recent real-world examples of DOM-based XSS vulnerabilities include:

- **CVE-2021-21972**: A DOM-based XSS vulnerability in the WordPress plugin "WP GDPR Compliance". An attacker could inject a script tag into the URL, which would then execute in the context of the victim's browser.
- **CVE-2020-14182**: A DOM-based XSS vulnerability in the "WordPress Gutenberg" editor. An attacker could inject a script tag into the post content, which would execute when the post is viewed.

These examples highlight the importance of proper input sanitization and validation in web applications.

### How to Prevent / Defend Against DOM-Based XSS

#### Detection

- **Static Analysis Tools**: Use tools like ESLint, SonarQube, or Bandit to scan your codebase for potential XSS vulnerabilities.
- **Dynamic Analysis Tools**: Use tools like Burp Suite, OWASP ZAP, or Acunetix to test your application for runtime vulnerabilities.

#### Prevention

1. **Input Sanitization**:
   - Always sanitize user input before inserting it into the DOM.
   - Use libraries like DOMPurify to sanitize HTML content.

2. **Content Security Policy (CSP)**:
   - Implement a strict Content Security Policy to restrict the sources from which scripts can be loaded.
   - Example CSP header:

   ```http
   Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
   ```

3. **Secure Coding Practices**:
   - Avoid using `innerHTML` or similar methods that directly insert untrusted data into the DOM.
   - Use safer methods like `textContent` or template literals.

#### Secure Code Fix

Here is an example of how to securely handle user input in AngularJS:

```html
<!DOCTYPE html>
<html ng-app="myApp">
<head>
  <title>AngularJS DOM XSS Lab</title>
  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.2/angular.min.js"></script>
</head>
<body>
  <div ng-controller="MyController">
    <input type="text" ng-model="message">
    <div ng-bind="message"></div>
  </div>

  <script>
    angular.module('myApp', [])
      .controller('MyController', function($scope) {
        $scope.message = '';
      });
  </script>
</body>
</html>
```

In this example, `ng-bind` is used instead of `{{message}}` to ensure that the content is treated as plain text rather than HTML.

### Conclusion

Understanding and preventing DOM-based XSS vulnerabilities is crucial for securing web applications. By following best practices such as input sanitization, implementing Content Security Policies, and using secure coding techniques, developers can significantly reduce the risk of XSS attacks.

### Hands-On Practice

For further practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

By working through these labs, you can gain practical experience in identifying and mitigating XSS vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/07-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/09-Conclusion|Conclusion]]
