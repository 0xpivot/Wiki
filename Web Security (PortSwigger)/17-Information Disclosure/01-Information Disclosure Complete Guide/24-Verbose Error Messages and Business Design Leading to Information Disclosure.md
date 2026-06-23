---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Verbose Error Messages and Business Design Leading to Information Disclosure

### What Are Verbose Error Messages and Business Design Leading to Information Disclosure?

Verbose error messages and business design leading to information disclosure occur when the application is designed in a way that inadvertently discloses sensitive information. For example, if the application displays different error messages for incorrect usernames and incorrect passwords, an attacker can use this information to determine valid usernames.

### Why Does This Matter?

Verbose error messages and business design leading to information disclosure can provide attackers with valuable information that can be used to launch further attacks. For example, if an attacker knows a valid username, they can focus their efforts on guessing the password, leading to potential account compromise.

### How Does This Work Under the Hood?

Consider a login page where the application displays different error messages for incorrect usernames and incorrect passwords. For example:

- If the username is incorrect, the application displays "The username is incorrect."
- If the username is correct but the password is incorrect, the application displays "The password is incorrect."

An attacker can use this information to determine valid usernames by trying different usernames and observing the error messages.

### Real-World Examples

One of the most notable examples of verbose error messages leading to information disclosure is the Heartbleed bug (CVE-2014-0160). In this vulnerability, attackers could use verbose error messages to extract sensitive information from memory, including private keys, passwords, and other confidential data.

### How to Prevent / Defend

#### Detection

To detect verbose error messages and business design leading to information disclosure, you can use static code analysis tools like SonarQube or Fortify. These tools scan the source code for patterns that indicate verbose error messages and flag them for review.

#### Prevention

To prevent verbose error messages and business design leading to information disclosure, you should ensure that the application does not disclose sensitive information through error messages. For example, the application should display a generic error message regardless of whether the username or password is incorrect.

Here is an example of a generic error message:

```html
<form action="/login" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username"><br>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password"><br>
    <input type="submit" value="Login">
</form>

{% if error %}
    <p>{{ error }}</p>
{% endif %}
```

In this example, the application displays a generic error message regardless of whether the username or password is incorrect.

### Secure Coding Fixes

#### Vulnerable Code

```html
<form action="/login" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username"><br>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password"><br>
    <input type="submit" value="Login">
</form>

{% if error == "incorrect_username" %}
    <p>The username is incorrect.</p>
{% elif error == "incorrect_password" %}
    <p>The password is incorrect.</p>
{% endif %}
```

#### Fixed Code

```html
<form action="/login" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username"><br>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password"><br>
    <input type="submit" value="Login">
</form>

{% if error %}
    <p>Login failed. Please check your username and password and try again.</p>
{% endif %}
```

In the fixed code, the application displays a generic error message regardless of whether the username or password is incorrect.

### Hands-On Labs

For hands-on practice with this topic, you can use the following labs:

- **PortSwigger Web Security Academy**: This lab provides exercises on detecting and preventing verbose error messages and business design leading to information disclosure.
- **OWASP Juice Shop**: This lab includes scenarios where verbose error messages and business design lead to information disclosure, and you can practice identifying and fixing these issues.

By thoroughly understanding and implementing these preventive measures, you can significantly reduce the risk of information disclosure in your applications.

---
<!-- nav -->
[[23-Using Insecure Hashing Algorithms|Using Insecure Hashing Algorithms]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/25-Conclusion|Conclusion]]
