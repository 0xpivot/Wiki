---
course: API Security
topic: Regular Expression DOS Attack
tags: [api-security]
---

## Regular Expression Denial of Service (ReDoS)

### Introduction to Regular Expressions

Regular expressions (regex) are powerful tools used to match patterns within strings. They are widely used in various programming languages and applications to validate input, search for specific patterns, and manipulate text. However, regex can also introduce vulnerabilities if not used carefully.

### Catastrophic Backtracking

One such vulnerability is **catastrophic backtracking**, which occurs when a regex engine spends an excessive amount of time trying to match a pattern due to the complexity of the regex or the input string. This can lead to a denial-of-service (DoS) attack, where an attacker can cause the application to become unresponsive by submitting specially crafted input that triggers the backtracking.

#### Example of Catastrophic Backtracking

Consider the following regex pattern:

```regex
^(a+)+$
```

This pattern matches a string that consists of one or more `a` characters. However, if the input string is something like `aaaaaaaaaaaaab`, the regex engine will spend a lot of time trying to match the pattern because it will repeatedly attempt to backtrack and re-evaluate the matches.

#### Real-World Example

A real-world example of ReDoS was seen in the **CVE-2018-1235** vulnerability in the `express.js` framework. The vulnerability was caused by a regex pattern used in the middleware that could be exploited to perform a DoS attack. The regex pattern was:

```regex
^\/(.*?)(?:\?(.*))?$ 
```

An attacker could submit a specially crafted URL that would cause the regex engine to spend a significant amount of time trying to match the pattern, leading to a denial of service.

### Regular Expression Denial of Service (ReDoS) Attack

A ReDoS attack exploits the inefficiency of certain regular expressions to cause a denial of service. The attacker submits input that causes the regex engine to spend an excessive amount of time trying to match the pattern, effectively making the application unresponsive.

#### Example Scenario

Let's consider a registration API that uses a regex pattern to validate usernames. The regex pattern might look something like this:

```regex
^[a-zA-Z0-9]+$
```

This pattern ensures that the username contains only alphanumeric characters. However, if the regex pattern is more complex, such as:

```regex
^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$
```

This pattern allows usernames with hyphens between alphanumeric segments. An attacker could submit a username like `username----username----username----...` that would cause the regex engine to spend a lot of time trying to match the pattern.

### Detection and Prevention

#### Detection

To detect ReDoS attacks, you can monitor the performance of your application and look for signs of increased CPU usage or slow response times. Tools like **OWASP ZAP** or **Burp Suite** can help you identify potential ReDoS vulnerabilities by analyzing the regex patterns used in your application.

#### Prevention

To prevent ReDoS attacks, you should follow these best practices:

1. **Use Efficient Regex Patterns**: Simplify your regex patterns to avoid unnecessary complexity. Avoid using patterns that can cause catastrophic backtracking.
2. **Time Limits**: Implement time limits for regex matching operations. If a regex operation takes too long, it should be terminated.
3. **Input Validation**: Validate input before passing it to regex patterns. Ensure that input conforms to expected formats and lengths.
4. **Use Safe Libraries**: Use libraries that are designed to handle regex safely. For example, the `re2` library is designed to avoid catastrophic backtracking.

#### Secure Coding Practices

Here is an example of how to implement a secure regex pattern in Python:

```python
import re

# Vulnerable regex pattern
vulnerable_pattern = r'^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$'

# Secure regex pattern
secure_pattern = r'^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+){0,10}$'

def validate_username(username):
    if re.match(vulnerable_pattern, username):
        print("Vulnerable: Matched")
    elif re.match(secure_pattern, username):
        print("Secure: Matched")
    else:
        print("Invalid username")

# Test with a long username
validate_username('username----username----username----username----username----username----username----username----username----username----')
```

In this example, the `vulnerable_pattern` can cause catastrophic backtracking, while the `secure_pattern` limits the number of hyphenated segments to 10, preventing excessive backtracking.

### Hands-On Practice

To practice detecting and preventing ReDoS attacks, you can use the following labs:

- **PortSwigger Web Security Academy**: This lab provides exercises to identify and mitigate ReDoS vulnerabilities in web applications.
- **OWASP Juice Shop**: This lab includes challenges that involve identifying and fixing ReDoS vulnerabilities in a simulated web application.

By following these best practices and using the provided resources, you can ensure that your application is protected against ReDoS attacks.

### Conclusion

Regular Expression Denial of Service (ReDoS) attacks are a serious threat to the security and performance of web applications. By understanding the principles of catastrophic backtracking and implementing secure coding practices, you can protect your application from these types of attacks. Always validate input and use efficient regex patterns to avoid unnecessary complexity.

---
<!-- nav -->
[[02-Regular Expression Denial of Service (ReDoS) Attack on Register API|Regular Expression Denial of Service (ReDoS) Attack on Register API]] | [[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/00-Overview|Overview]] | [[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/04-Practice Questions & Answers|Practice Questions & Answers]]
