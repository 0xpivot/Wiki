---
course: API Security
topic: Regular Expression DOS Attack
tags: [api-security]
---

## Regular Expression Denial of Service (ReDoS) Attack on Register API

### Introduction to Regular Expressions (Regex)

Regular expressions (regex) are powerful tools used to match patterns within strings. They are widely used in various programming languages and applications to validate input data, search for specific patterns, and perform string manipulations. However, regex can be complex and potentially dangerous if not used carefully.

#### What is a Regular Expression?

A regular expression is a sequence of characters that define a search pattern. It consists of literal characters and metacharacters that have special meanings. For example:

- `.` matches any single character.
- `*` matches zero or more occurrences of the preceding element.
- `+` matches one or more occurrences of the preceding element.
- `[ ]` defines a character class, matching any one character inside the brackets.
- `|` acts as an OR operator, allowing alternative patterns.

#### Why Use Regular Expressions?

Regular expressions are used for various purposes, such as:

- **Input Validation:** Ensuring that user inputs conform to specific formats (e.g., email addresses, phone numbers).
- **Pattern Matching:** Searching for specific patterns within large bodies of text.
- **String Manipulation:** Extracting, replacing, or transforming parts of strings based on patterns.

### Regular Expression Denial of Service (ReDoS) Attack

A Regular Expression Denial of Service (ReDoS) attack is a type of attack where an attacker exploits the complexity of a regular expression to cause a denial of service. This occurs when a regex pattern is designed in a way that allows for catastrophic backtracking, leading to extremely high computational costs.

#### How ReDoS Works

When a regex engine tries to match a pattern against a string, it follows a set of rules to determine if the pattern matches. In some cases, the regex engine may need to backtrack through the string multiple times, especially if the pattern includes quantifiers like `*` or `+`. This backtracking can become computationally expensive, causing the application to slow down or even crash.

#### Example of a Vulnerable Regex Pattern

Consider the following regex pattern:

```regex
([a-zA-Z]+)*
```

This pattern matches any sequence of letters, repeated zero or more times. If an attacker provides a very long string with many letters, the regex engine may spend a significant amount of time trying to match the pattern, leading to a denial of service.

### Real-World Examples of ReDoS Attacks

ReDoS attacks have been observed in various real-world scenarios. Here are a few notable examples:

#### CVE-2018-16475: Node.js Express.js

In 2018, a vulnerability was discovered in the `express-validator` middleware for Node.js. The regex pattern used for validating email addresses was susceptible to ReDoS attacks. An attacker could send a specially crafted email address that would cause the regex engine to perform excessive backtracking, leading to a denial of service.

#### CVE-2019-10929: Ruby on Rails

Ruby on Rails had a vulnerability where certain regex patterns used in the `ActionDispatch::Http::Parameters` module were prone to ReDoS attacks. An attacker could exploit this by sending a large number of requests with specially crafted parameters, causing the server to become unresponsive.

### ReDoS Attack on Register API

Let's consider a hypothetical scenario where a register API uses regex to validate usernames and passwords. The regex pattern used for validation is as follows:

```regex
^[a-zA-Z]+[0-9]*$
```

This pattern matches a username that starts with one or more letters followed by zero or more digits.

#### Vulnerable Code Example

Here is a simplified example of how the register API might look:

```python
import re

def register(username, password):
    username_pattern = r'^[a-zA-Z]+[0-9]*$'
    password_pattern = r'^[a-zA-Z]+[0-9]*$'

    if not re.match(username_pattern, username):
        return "Invalid username"
    
    if not re.match(password_pattern, password):
        return "Invalid password"

    # Proceed with registration logic
    return "Registration successful"
```

#### Attack Scenario

An attacker could craft a username or password that causes the regex engine to perform excessive backtracking. For example, the following input could be used to exploit the vulnerability:

```plaintext
username = "a"*1000 + "b"
```

This input would cause the regex engine to spend a lot of time trying to match the pattern, leading to a denial of service.

### How to Prevent / Defend Against ReDoS Attacks

To prevent ReDoS attacks, it is essential to use regex patterns that are efficient and avoid catastrophic backtracking. Here are some strategies to mitigate the risk:

#### 1. Use Atomic Groups and Possessive Quantifiers

Atomic groups and possessive quantifiers can help prevent excessive backtracking. For example, the following pattern uses atomic groups:

```regex
^(?>[a-zA-Z]+)(?>[0-9]*)$
```

The `?>` syntax denotes an atomic group, which prevents the regex engine from backtracking once it has matched a portion of the pattern.

#### 2. Limit the Length of Input Strings

Limiting the length of input strings can help prevent attackers from exploiting long strings that cause excessive backtracking. For example:

```python
MAX_USERNAME_LENGTH = 50

def register(username, password):
    if len(username) > MAX_USERNAME_LENGTH:
        return "Username too long"
    
    # Continue with validation and registration logic
```

#### 3. Use Safe Regex Libraries

Some regex libraries provide features to limit the execution time or the number of steps a regex engine can take. For example, the `re2` library in Go is designed to be safe against ReDoS attacks.

#### 4. Validate Input Before Using Regex

Perform basic validation on input strings before applying regex patterns. For example, check the length of the string and ensure it meets basic criteria before using regex for further validation.

### Secure Code Fix Example

Here is an example of how the vulnerable code can be fixed to prevent ReDoS attacks:

```python
import re

def register(username, password):
    MAX_USERNAME_LENGTH = 50
    MAX_PASSWORD_LENGTH = 50

    if len(username) > MAX_USERNAME_LENGTH:
        return "Username too long"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return "Password too long"

    username_pattern = r'^[a-zA-Z]+[0-9]*$'
    password_pattern = r'^[a-zA-Z]+[0-9]*$'

    if not re.match(username_pattern, username):
        return "Invalid username"
    
    if not re.match(password_pattern, password):
        return "Invalid password"

    # Proceed with registration logic
    return "Registration successful"
```

### Detection and Monitoring

To detect and monitor ReDoS attacks, you can implement the following measures:

#### 1. Logging and Monitoring

Log and monitor the performance of your application. Look for unusual spikes in CPU usage or response times that could indicate a ReDoS attack.

#### 2. Rate Limiting

Implement rate limiting to restrict the number of requests a client can make within a given time period. This can help prevent attackers from overwhelming the system with malicious requests.

#### 3. Intrusion Detection Systems (IDS)

Use intrusion detection systems to monitor network traffic and detect patterns that are indicative of ReDoS attacks.

### Conclusion

Regular Expression Denial of Service (ReDoS) attacks are a serious threat to the security and performance of applications that rely on regex for input validation. By understanding the risks associated with regex patterns and implementing proper defenses, you can protect your applications from these types of attacks.

### Practice Labs

For hands-on practice with ReDoS attacks and defenses, consider the following resources:

- **PortSwigger Web Security Academy:** Offers interactive labs on regex vulnerabilities and other web security topics.
- **OWASP Juice Shop:** A deliberately insecure web application for learning about web security vulnerabilities, including regex attacks.
- **DVWA (Damn Vulnerable Web Application):** Provides a variety of web application vulnerabilities, including regex-based attacks.

By engaging with these labs, you can gain practical experience in identifying and mitigating ReDoS vulnerabilities in real-world applications.

---
<!-- nav -->
[[01-Introduction to Regular Expression DOS Attacks|Introduction to Regular Expression DOS Attacks]] | [[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/00-Overview|Overview]] | [[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/03-Regular Expression Denial of Service (ReDoS)|Regular Expression Denial of Service (ReDoS)]]
