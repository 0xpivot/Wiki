---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Clickjacking: An In-Depth Analysis

### Introduction to Clickjacking

Clickjacking, also known as UI redress attack or user interface (UI) redress attack, is a malicious technique used by attackers to trick users into clicking on hidden buttons or links. This is typically achieved by overlaying transparent or opaque layers over legitimate web pages. When a user interacts with what they believe to be a legitimate element, they are actually interacting with a hidden element controlled by the attacker.

### Understanding the Vulnerability

#### What is Clickjacking?

Clickjacking occurs when an attacker tricks a user into clicking on a button or link that is invisible or obscured. The attacker achieves this by layering a transparent or nearly transparent iframe over a legitimate website. When the user clicks on what they think is a legitimate button, they are actually clicking on the attacker's hidden button.

#### Why Does Clickjacking Matter?

Clickjacking can lead to serious security vulnerabilities, such as unauthorized access to sensitive information, execution of unwanted actions, and even financial loss. For instance, an attacker might trick a user into liking a post on a social media platform or clicking a button that grants administrative privileges to the attacker.

### Historical Context and Real-World Examples

#### Historical Context

The term "clickjacking" was coined in 2008 by Jeremiah Grossman and Robert Hansen. Since then, numerous high-profile incidents have highlighted the severity of this vulnerability. One notable example is the Facebook Likejacking incident in 2010, where attackers used clickjacking to trick users into liking malicious content.

#### Recent Real-World Examples

In recent years, several major websites have fallen victim to clickjacking attacks:

- **CVE-2021-3116**: A clickjacking vulnerability was discovered in Microsoft Edge, allowing attackers to trick users into granting permissions to malicious extensions.
- **CVE-2020-1472**: This vulnerability in Microsoft Exchange Server allowed attackers to perform clickjacking attacks, leading to unauthorized access to sensitive data.

These examples underscore the importance of implementing robust defenses against clickjacking.

### Defense Mechanisms Against Clickjacking

#### X-Frame-Options Header

One of the primary defenses against clickjacking is the `X-Frame-Options` HTTP response header. This header specifies whether or not a browser should be allowed to render a page in a `<frame>`, `<iframe>`, `<object>`, or `<embed>` context.

##### How X-Frame-Options Works

The `X-Frame-Options` header can take one of three values:

1. **DENY**: The page cannot be displayed in a frame.
2. **SAMEORIGIN**: The page can be displayed in a frame on the same origin as the page itself.
3. **ALLOW-FROM uri**: The page can be displayed in a frame on the specified origin.

Here is an example of how to set the `X-Frame-Options` header in a web server configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header X-Frame-Options SAMEORIGIN;
    }
}
```

This configuration ensures that the `X-Frame-Options` header is set to `SAMEORIGIN` for all requests to `example.com`.

##### Limitations of X-Frame-Options

Despite its effectiveness, the `X-Frame-Options` header has several limitations:

1. **Per-Page Policy Specification**: The `X-Frame-Options` header needs to be specified for every single page, which can be cumbersome and error-prone. Developers can mitigate this by implementing a filter that automatically adds the header to every page in the application.

2. **Obsolete Allow-From Option**: The `ALLOW-FROM uri` option is obsolete and no longer supported by modern browsers. If an attacker uses this option and the browser does not support it, the clickjacking defense is ineffective.

3. **No Support for Multiple Values**: The `X-Frame-Options` header does not support multiple values, making it difficult to allow both the current site and third-party sites to frame the same response.

### Content Security Policy (CSP)

To address the limitations of `X-Frame-Options`, developers often turn to Content Security Policy (CSP). CSP is a more comprehensive approach to securing web applications by defining a set of policies that control how resources are loaded and executed.

#### How CSP Works

CSP allows developers to specify a list of trusted sources from which resources can be loaded. This includes scripts, stylesheets, images, and other resources. By defining these policies, developers can prevent malicious content from being loaded and executed.

Here is an example of how to set up a basic CSP in a web server configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Content-Security-Policy "frame-ancestors 'self'";
    }
}
```

This configuration sets the `Content-Security-Policy` header to `frame-ancestors 'self'`, which restricts framing to the same origin.

#### Frame-Ancestors Directive

The `frame-ancestors` directive in CSP is specifically designed to prevent clickjacking attacks. It allows developers to specify which origins are allowed to frame a resource. The `frame--ancestors` directive supports the following values:

- `'none'`: The resource cannot be framed.
- `'self'`: The resource can be framed by the same origin.
- `'origin'`: The resource can be framed by the same origin and any subdomains.
- `'origin *'`: The resource can be framed by the same origin and any subdomains, as well as any other origins.
- Specific origins: You can specify specific origins that are allowed to frame the resource.

Here is an example of a more complex CSP configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Content-Security-Policy "frame-ancestors 'self' https://trusted-origin.com";
    }
}
```

This configuration allows framing from the same origin (`'self'`) and from `https://trusted-origin.com`.

### How to Prevent / Defend Against Clickjacking

#### Detection

To detect clickjacking vulnerabilities, developers can use automated tools and manual testing methods:

1. **Automated Tools**:
   - **OWASP ZAP**: OWASP ZAP is a free and open-source tool that can detect clickjacking vulnerabilities.
   - **Burp Suite**: Burp Suite is a commercial tool that provides comprehensive security testing capabilities, including clickjacking detection.

2. **Manual Testing**:
   - Developers can manually test their applications by attempting to frame pages using different origins and checking if the `X-Frame-Options` or `Content-Security-Policy` headers are correctly set.

#### Prevention

To prevent clickjacking attacks, developers should implement the following measures:

1. **Set X-Frame-Options Header**:
   - Ensure that the `X-Frame-Options` header is set to `SAMEORIGIN` or `DENY` for all pages.
   - Implement a filter to automatically add the header to every page in the application.

2. **Implement Content Security Policy (CSP)**:
   - Use the `frame-ancestors` directive in CSP to restrict framing to trusted origins.
   - Set the `frame-ancestors` directive to `SAMEORIGIN` or specific trusted origins.

3. **Regular Security Audits**:
   - Conduct regular security audits to identify and fix potential clickjacking vulnerabilities.
   - Use automated tools and manual testing methods to ensure that the application is secure.

#### Secure Coding Practices

Developers should follow secure coding practices to prevent clickjacking attacks:

1. **Avoid Using iframes for Untrusted Content**:
   - Do not use iframes to load untrusted content from external sources.
   - Instead, use secure methods to embed content, such as using the `frame-ancestors` directive in CSP.

2. **Use HTTPS**:
   - Ensure that all resources are loaded over HTTPS to prevent man-in-the-middle attacks.
   - Use HSTS (HTTP Strict Transport Security) to enforce HTTPS connections.

3. **Validate User Input**:
   - Validate user input to prevent malicious content from being injected into the application.
   - Use input validation libraries and frameworks to ensure that user input is safe.

### Conclusion

Clickjacking is a serious security vulnerability that can lead to unauthorized access to sensitive information and execution of unwanted actions. To defend against clickjacking attacks, developers should implement the `X-Frame-Options` header and Content Security Policy (CSP). Regular security audits and secure coding practices are essential to ensure that the application is secure.

By understanding the concepts, limitations, and defense mechanisms against clickjacking, developers can protect their applications from this type of attack.

---
<!-- nav -->
[[04-Black Box Testing Perspective|Black Box Testing Perspective]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[06-Combining X-Frame-Options and CSP|Combining X-Frame-Options and CSP]]
