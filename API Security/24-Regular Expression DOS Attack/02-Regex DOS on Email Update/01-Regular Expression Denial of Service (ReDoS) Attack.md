---
course: API Security
topic: Regular Expression DOS Attack
tags: [api-security]
---

## Regular Expression Denial of Service (ReDoS) Attack

### Introduction to Regular Expression Denial of Service (ReDoS)

Regular Expression Denial of Service (ReDoS) is a type of attack that exploits the computational complexity of certain regular expressions (regex) to cause a denial of service. This attack occurs when an attacker provides a carefully crafted input string that causes the regex engine to take an excessive amount of time to process, leading to a significant slowdown or even crash of the application.

### Understanding Regular Expressions

Before diving into ReDoS attacks, it's essential to understand regular expressions. Regular expressions are patterns used to match character combinations in strings. They are widely used in various programming languages and tools for tasks such as searching, replacing, and validating text.

#### Syntax and Components of Regular Expressions

- **Literal Characters**: Match specific characters, e.g., `a`, `b`.
- **Character Classes**: Match any character within a set, e.g., `[abc]` matches `a`, `b`, or `c`.
- **Quantifiers**: Specify the number of occurrences of a pattern, e.g., `*` (zero or more), `+` (one or more), `{n}` (exactly n times).
- **Anchors**: Match positions in the string, e.g., `^` (start of string), `$` (end of string).

### Example of a Regular Expression

Consider the following regular expression:

```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

This regex is commonly used to validate email addresses. It checks for a valid format where:
- The local part (before the `@`) can contain letters, digits, dots, underscores, percent signs, plus signs, and hyphens.
- The domain part (after the `@`) can contain letters, digits, dots, and hyphens.
- The top-level domain (TLD) must be at least two characters long.

### ReDoS Attack Mechanism

A ReDoS attack occurs when an attacker crafts an input string that causes the regex engine to perform an excessive number of backtracking steps. Backtracking is a mechanism used by regex engines to try different paths when matching a pattern. In some cases, this can lead to exponential time complexity.

#### Example of a Vulnerable Regular Expression

Consider the following regular expression used to validate email addresses:

```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

If the regex engine encounters a string like `aaaaaaaaaaaaaaaaaaaaa@domain.com`, it may spend a lot of time trying to match the pattern due to the repeated `a`s in the local part.

### Real-World Examples of ReDoS Attacks

ReDoS attacks have been observed in various real-world scenarios. Here are a few notable examples:

- **CVE-2018-1117**: A ReDoS vulnerability was found in the `express-validator` package, which is commonly used in Node.js applications to validate user inputs. The vulnerability allowed attackers to craft malicious input strings that caused the regex engine to consume excessive CPU resources, leading to a denial of service.
  
- **CVE-2019-1010083**: Another ReDoS vulnerability was discovered in the `passport-local-mongoose` package, which is used for authentication in Node.js applications. The vulnerability allowed attackers to craft input strings that caused the regex engine to perform excessive backtracking, leading to a denial of service.

### Detailed Example of a ReDoS Attack

Let's consider a scenario where an application uses a regular expression to validate email addresses. The application might have a route like `/update-email` that accepts a new email address and updates the user's profile.

#### Vulnerable Code Example

Here is a simplified example of a vulnerable server-side code in Node.js:

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// Regular expression to validate email addresses
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

app.post('/update-email', (req, res) => {
    const { email } = req.body;
    
    if (!emailRegex.test(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }
    
    // Update the user's email address
    res.json({ success: true });
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
```

#### Attacker's Payload

An attacker could craft a payload like:

```json
{
    "email": "a".repeat(10000) + "@domain.com"
}
```

When this payload is sent to the `/update-email` endpoint, the regex engine will spend a significant amount of time trying to match the pattern, leading to a denial of service.

### How to Detect ReDoS Attacks

Detecting ReDoS attacks can be challenging, but there are several methods to identify potential vulnerabilities:

1. **Static Analysis Tools**: Use static analysis tools like ESLint, SonarQube, or Bandit to scan your codebase for potential ReDoS vulnerabilities.
2. **Dynamic Analysis Tools**: Use dynamic analysis tools like OWASP ZAP or Burp Suite to test your application for ReDoS vulnerabilities by sending crafted payloads.
3. **Performance Monitoring**: Monitor the performance of your application and look for unusual spikes in CPU usage or response times.

### How to Prevent / Defend Against ReDoS Attacks

Preventing ReDoS attacks involves both coding practices and infrastructure hardening.

#### Secure Coding Practices

1. **Use Safe Regular Expressions**: Avoid using complex or nested quantifiers in your regular expressions. Instead, use simpler patterns that are less likely to cause excessive backtracking.
2. **Limit Input Length**: Set reasonable limits on the length of input strings to prevent attackers from crafting excessively long payloads.
3. **Use Libraries with ReDoS Protection**: Use libraries that have built-in protection against ReDoS attacks. For example, the `re2` library in Python is designed to avoid catastrophic backtracking.

#### Infrastructure Hardening

1. **Rate Limiting**: Implement rate limiting on endpoints that accept user input to prevent attackers from overwhelming your application with requests.
2. **Timeouts**: Set timeouts for regex operations to ensure that they do not run indefinitely. For example, you can use the `setTimeout` function in Node.js to limit the execution time of regex operations.
3. **Monitoring and Alerts**: Set up monitoring and alerts to detect unusual activity that may indicate a ReDoS attack. Use tools like Prometheus and Grafana to monitor CPU usage and response times.

### Secure Code Example

Here is a secure version of the previous code example:

```javascript
const express = require('express');
const app = express();
const re2 = require('re2'); // Using re2 library for safe regex

app.use(express.json());

// Regular expression to validate email addresses
const emailRegex = new re2(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/, 'i');

app.post('/update-email', (req, res) => {
    const { email } = req.body;
    
    if (!emailRegex.test(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }
    
    // Update the user's email address
    res.json({ success: true });
});

app.listen(3000, () => {
    console.log('Server is running on port  3000');
});
```

In this example, we use the `re2` library to ensure that the regex operation does not cause excessive backtracking.

### Conclusion

Regular Expression Denial of Service (ReDoS) attacks are a serious threat to the security and performance of web applications. By understanding the mechanisms behind these attacks and implementing secure coding practices and infrastructure hardening measures, you can protect your applications from ReDoS vulnerabilities.

### Hands-On Practice

To gain practical experience with ReDoS attacks, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on regular expression denial of service attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application that you can use to practice identifying and exploiting ReDoS vulnerabilities.

By practicing in these environments, you can develop a deeper understanding of ReDoS attacks and learn how to defend against them effectively.

---
<!-- nav -->
[[API Security/24-Regular Expression DOS Attack/02-Regex DOS on Email Update/00-Overview|Overview]] | [[02-Regular Expression Denial of Service (ReDoS) Attacks on Email Fields|Regular Expression Denial of Service (ReDoS) Attacks on Email Fields]]
