---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Understanding Whitelist-Based Input Filtering

In the given scenario, the application is using a whitelist-based input filtering mechanism to validate the hostname provided by the user. This means that the application only accepts specific hostnames and rejects any others.

### What is Whitelist-Based Input Filtering?

Whitelist-based input filtering is a security measure that restricts input to a predefined set of acceptable values. In this case, the application only accepts the hostname `stock.we like to shop.net` and rejects any other hostnames.

### Why Use Whitelist-Based Filtering?

Whitelist-based filtering is generally considered more secure than blacklist-based filtering because it explicitly defines what is allowed, rather than trying to define what is not allowed. This reduces the risk of unintended inputs slipping through.

### How Does Whitelist-Based Filtering Work?

The application parses the URL provided by the user, extracts the hostname, and compares it against the whitelist. If the hostname matches the whitelist, the request is processed; otherwise, it is rejected.

### Example of Whitelist-Based Filtering

Consider the following code snippet that demonstrates a simple whitelist-based filtering mechanism:

```python
def validate_hostname(hostname):
    whitelist = ["stock.we like to shop.net"]
    if hostname in whitelist:
        return True
    else:
        return False

hostname = "stock.we like to shop.net"
if validate_hostname(hostname):
    print("Hostname is valid")
else:
    print("Hostname is invalid")
```

This code checks if the provided hostname is in the whitelist and returns `True` if it is valid, otherwise `False`.

### Pitfalls of Whitelist-Based Filtering

While whitelist-based filtering is generally more secure, it is not foolproof. Attackers can still find ways to bypass the filtering mechanism, especially if the implementation is not robust.

### Common Mistakes in Whitelist-Based Filtering

- **Incomplete Whitelisting**: If the whitelist does not cover all possible valid inputs, attackers can still exploit the vulnerability.
- **Incorrect Parsing**: If the application incorrectly parses the input, it may accept invalid hostnames.
- **Encoding Vulnerabilities**: Attackers can use various encoding techniques to bypass the filtering mechanism.

---
<!-- nav -->
[[03-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/05-Lab 4 SSRF with whitelist based input filter/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/05-Lab 4 SSRF with whitelist based input filter/05-Practice Questions & Answers|Practice Questions & Answers]]
