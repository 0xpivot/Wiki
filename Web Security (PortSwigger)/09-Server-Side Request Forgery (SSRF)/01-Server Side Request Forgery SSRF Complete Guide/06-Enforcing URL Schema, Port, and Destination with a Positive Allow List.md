---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Enforcing URL Schema, Port, and Destination with a Positive Allow List

### What is a Positive Allow List?

A positive allow list, also known as a whitelist, is a security mechanism that explicitly defines a set of allowed values or actions. In the context of SSRF, this means defining a list of URLs that the application is permitted to access.

### Why Use a Positive Allow List?

Using a positive allow list helps prevent SSRF attacks by ensuring that the application only makes requests to trusted destinations. This reduces the risk of accessing internal resources or external malicious sites.

#### Example of a Positive Allow List

Suppose an application needs to communicate with `https://we-like-shop.com`. A positive allow list would include this URL and reject any other URLs.

### How to Implement a Positive Allow List

To implement a positive allow list, follow these steps:

1. **Define Allowed URLs**: Create a list of URLs that the application is allowed to access.
2. **Check Against the List**: Before making any HTTP requests, check if the target URL is in the allow list.
3. **Reject Invalid Requests**: Automatically reject any requests that do not match the allow list.

#### Code Example

Here’s an example of how to implement a positive allow list in Python:

```python
ALLOWED_URLS = [
    "https://we-like-shop.com",
    "https://api.example.com"
]

def is_allowed_url(url):
    return url in ALLOWED_URLS

# Example usage
url = "https://we-like-shop.com"
if is_allowed_url(url):
    print("URL is allowed")
else:
    print("URL is not allowed")
```

### Real-World Examples

The CVE-2021-35042 vulnerability in GitLab demonstrated the importance of using positive allow lists. This vulnerability allowed attackers to bypass URL validation and access internal resources, highlighting the need for strict allow lists.

### Pitfalls and Common Mistakes

- **Incomplete Allow Lists**: Failing to include all necessary URLs can leave the application vulnerable.
- **Dynamic URLs**: Handling dynamic URLs requires additional logic to ensure they remain within the allowed scope.
- **Configuration Management**: Ensuring that the allow list is properly managed and updated is crucial.

### How to Prevent / Defend

1. **Centralized Configuration**: Maintain a centralized configuration for the allow list to ensure consistency across the application.
2. **Automated Updates**: Automate updates to the allow list to reflect changes in the application’s requirements.
3. **Logging and Monitoring**: Log and monitor access attempts to detect and respond to suspicious activity.

---
<!-- nav -->
[[05-Detailed Mechanics of SSRF|Detailed Mechanics of SSRF]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[07-Exploiting SSRF Vulnerabilities|Exploiting SSRF Vulnerabilities]]
