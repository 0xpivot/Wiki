---
course: API Security
topic: Regular Expression DOS Attack
tags: [api-security]
---

## Introduction to Regular Expression DOS Attacks

Regular Expression Denial of Service (ReDoS) attacks are a class of vulnerabilities that occur when an attacker provides input to a regular expression that causes the engine to take an excessive amount of time to process. This can lead to a denial of service, where the application becomes unresponsive due to the high computational load.

### What is a Regular Expression?

A regular expression (regex) is a sequence of characters that define a search pattern. They are used to match patterns within strings and are widely used in programming languages, text editors, and other tools. Regular expressions can be simple, like matching a specific string, or complex, involving various operators and quantifiers.

### Why Does ReDoS Matter?

ReDoS attacks are particularly dangerous because they can be executed with minimal effort by an attacker. By providing a carefully crafted input, an attacker can cause the regex engine to perform an exponential number of operations, leading to a significant slowdown or crash of the application. This can result in a denial of service, where legitimate users cannot access the application.

### How Does ReDoS Work Under the Hood?

To understand how ReDoS works, let's consider a simple example. Suppose we have a regular expression that matches a string containing a series of `a` characters followed by a `b` character:

```regex
/^a+b$/
```

This regex will match strings like `ab`, `aab`, `aaab`, etc. However, if an attacker provides a string like `aaaaaaaaaaaaaaaaaaaaaaaac`, the regex engine will attempt to match each `a` character individually, leading to a large number of backtracking steps. In the worst case, this can result in an exponential number of operations, causing the engine to hang or crash.

### Real-World Examples of ReDoS Attacks

#### CVE-2017-17455: Express.js ReDoS Vulnerability

In 2017, a ReDoS vulnerability was discovered in the Express.js framework. The vulnerability was caused by a regular expression used in the routing mechanism. An attacker could provide a specially crafted URL that would cause the regex engine to perform an excessive number of operations, leading to a denial of service.

#### CVE-2018-1117: Node.js ReDoS Vulnerability

Another notable example is the ReDoS vulnerability found in Node.js. The vulnerability was caused by a regular expression used in the `path.normalize` function. An attacker could provide a specially crafted path that would cause the regex engine to perform an excessive number of operations, leading to a denial of service.

### Regular Expression DOS Attack on Register API

Let's delve deeper into the specifics of a ReDoS attack on a register API. We will explore the mechanics of the attack, the vulnerable code, and how to defend against it.

#### Vulnerable Code Example

Consider a register API that uses a regular expression to validate user input. The following is a simplified example of such an API:

```javascript
app.post('/register', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;

    // Validate username using a regular expression
    const regex = /^a+b$/;
    if (!regex.test(username)) {
        return res.status(400).send('Invalid username');
    }

    // Process registration
    // ...
});
```

In this example, the regular expression `/^a+b$/` is used to validate the username. If an attacker provides a username like `aaaaaaaaaaaaaaaaaaaaaaaac`, the regex engine will perform an excessive number of operations, leading to a denial of service.

### Full HTTP Request and Response

Let's look at a complete HTTP request and response for this scenario.

#### HTTP Request

```http
POST /register HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 42

{
    "username": "aaaaaaaaaaaaaaaaaaaaaaaac",
    "password": "password123"
}
```

#### HTTP Response

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
Content-Length: 29

{
    "message": "Invalid username"
}
```

### How to Prevent / Defend Against ReDoS Attacks

#### Secure Coding Practices

To prevent ReDoS attacks, it is crucial to follow secure coding practices. Here are some key strategies:

1. **Use Safe Regular Expressions**: Avoid using regular expressions that can cause exponential backtracking. Instead, use simpler patterns that are less likely to cause performance issues.

2. **Limit Input Length**: Limit the length of user input to prevent attackers from providing excessively long strings.

3. **Time Out Mechanisms**: Implement time out mechanisms to ensure that the regex engine does not run indefinitely.

4. **Use Libraries with Built-in Protection**: Use libraries that have built-in protection against ReDoS attacks. For example, the `re2` library is designed to avoid exponential backtracking.

#### Vulnerable vs. Secure Code Comparison

Here is a comparison between the vulnerable and secure versions of the code:

##### Vulnerable Code

```javascript
app.post('/register', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;

    // Vulnerable regular expression
    const regex = /^a+b$/;
    if (!regex.test(username)) {
        return res.status(400).send('Invalid username');
    }

    // Process registration
    // ...
});
```

##### Secure Code

```javascript
app.post('/register', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;

    // Secure regular expression
    const regex = /^[a-z]+b$/;
    if (!regex.test(username)) {
        return res.status(400).send('Invalid username');
    }

    // Process registration
    // ...
});
```

In the secure version, the regular expression `/^[a-z]+b$/` is used, which avoids the potential for exponential backtracking.

### Detection and Prevention Tools

Several tools can help detect and prevent ReDoS attacks:

1. **Static Analysis Tools**: Tools like ESLint can be configured to detect potentially vulnerable regular expressions.

2. **Dynamic Analysis Tools**: Tools like OWASP ZAP can be used to test APIs for ReDoS vulnerabilities.

3. **Regex Testing Tools**: Online tools like regex101 can be used to test regular expressions and identify potential performance issues.

### Practice Labs

For hands-on practice with ReDoS attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including ReDoS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application that includes ReDoS vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to practice identifying and exploiting ReDoS vulnerabilities.

### Conclusion

Regular Expression Denial of Service (ReDoS) attacks are a serious threat to web applications. By understanding the mechanics of these attacks and following secure coding practices, developers can protect their applications from such vulnerabilities. Always test your regular expressions for performance and use tools to detect and prevent ReDoS attacks.

---
<!-- nav -->
[[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/00-Overview|Overview]] | [[02-Regular Expression Denial of Service (ReDoS) Attack on Register API|Regular Expression Denial of Service (ReDoS) Attack on Register API]]
