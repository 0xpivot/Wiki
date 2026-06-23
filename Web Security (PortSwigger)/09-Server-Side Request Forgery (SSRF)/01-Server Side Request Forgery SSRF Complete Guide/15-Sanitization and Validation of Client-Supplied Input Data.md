---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Sanitization and Validation of Client-Supplied Input Data

### What is Sanitization and Validation?

Sanitization and validation are critical processes in web security that help prevent various types of attacks, including Server-Side Request Forgery (SSRF). **Sanitization** refers to the process of cleaning up user input to remove potentially harmful characters or patterns. **Validation**, on the other hand, ensures that the input conforms to expected formats and constraints.

### Why is Sanitization and Validation Important?

When a web application accepts input from users, this input can come from untrusted sources. Attackers often exploit this by injecting malicious data designed to manipulate the application's behavior. By sanitizing and validating input, you can mitigate these risks and ensure that the application behaves as intended.

#### Example of Malicious Input

Consider a scenario where a user inputs a URL into a form field. An attacker might inject a URL like `http://localhost/admin` to access sensitive administrative pages. Without proper sanitization and validation, the application might inadvertently expose these pages to unauthorized users.

### How to Implement Sanitization and Validation

To implement sanitization and validation effectively, follow these steps:

1. **Define Expected Input Formats**: Clearly define the expected format and constraints for each input field.
2. **Use Regular Expressions**: Utilize regular expressions to match valid input patterns and reject invalid ones.
3. **Whitelist Characters**: Allow only a specific set of characters that are safe for your application.
4. **Escape Special Characters**: Escape special characters that could be used in SQL injection, XSS, or other attacks.

#### Code Example

Here’s an example of how to sanitize and validate a URL input using Python:

```python
import re

def validate_url(url):
    # Define a regular expression pattern for a valid URL
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'([A-Za-z0-9.-]+)'  # domain name
        r'(:\d+)?'  # optional port number
        r'(\/[^\s]*)?$'  # optional path
    )
    
    if url_pattern.match(url):
        return True
    else:
        return False

# Example usage
url = "http://example.com"
if validate_url(url):
    print("URL is valid")
else:
    print("URL is invalid")
```

### Real-World Examples

Recent vulnerabilities have highlighted the importance of input validation. For instance, the CVE-2021-21972 vulnerability in Jenkins allowed attackers to bypass input validation and execute arbitrary commands on the server. This underscores the necessity of thorough input validation to prevent such exploits.

### Pitfalls and Common Mistakes

- **Overly Permissive Patterns**: Using overly permissive regular expressions can lead to vulnerabilities.
- **Ignoring Edge Cases**: Failing to account for edge cases, such as URLs with unusual characters or structures, can leave gaps in security.
- **Manual Validation**: Relying solely on manual validation without automated tools can introduce human error.

### How to Prevent / Defend

1. **Automate Validation**: Use libraries and frameworks that provide built-in validation mechanisms.
2. **Regular Audits**: Regularly audit input validation logic to ensure it remains robust against new attack vectors.
3. **Security Testing**: Conduct security testing, including penetration testing, to identify and fix vulnerabilities.

---
<!-- nav -->
[[14-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[16-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]]
