---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Finding SSRF Vulnerabilities

Once you understand what SSRF vulnerabilities are, the next step is to learn how to find them. This section covers both white-box and black-box approaches to identifying SSRF vulnerabilities.

### White-Box Testing

White-box testing involves having access to the application's source code. This allows you to analyze the code and identify potential SSRF vulnerabilities.

#### Steps for White-Box Testing

1. **Identify User Inputs**: Look for places in the code where user inputs are taken, such as form fields, URL parameters, or API endpoints.
2. **Trace Input Usage**: Trace how these inputs are used within the application, particularly in functions that make external requests.
3. **Check for Validation**: Verify whether the inputs are properly validated and sanitized before being used in requests.
4. **Look for External Requests**: Identify functions that make external requests and check if they rely on user inputs.

#### Example: Analyzing Python Code

Consider the following Python code snippet:

```python
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.text
```

In this code, the `fetch_data` function takes a `url` parameter and makes an HTTP GET request to that URL. To identify potential SSRF vulnerabilities, you would need to trace where this function is called and ensure that the `url` parameter is properly validated.

#### Secure Code Fix

To fix this vulnerability, you can add input validation:

```python
import requests
from urllib.parse import urlparse

def fetch_data(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme in ['http', 'https'] and parsed_url.hostname == 'trusted-domain.com':
        response = requests.get(url)
        return response.text
    else:
        raise ValueError("Invalid URL")
```

### Black-Box Testing

Black-box testing involves testing the application without access to its source code. This approach relies on probing the application's behavior to identify potential SSRF vulnerabilities.

#### Steps for Black-Box Testing

1. **Identify User Inputs**: Look for places in the application where user inputs are taken, such as form fields, URL parameters, or API endpoints.
2. **Test with Malicious Inputs**: Provide malicious inputs to these fields to see if the application makes requests to unexpected or internal resources.
3. **Monitor Network Traffic**: Use tools like Burp Suite or Wireshark to monitor the network traffic and identify any unexpected requests.
4. **Analyze Responses**: Analyze the responses to determine if the application is making requests to internal resources or leaking sensitive information.

#### Example: Testing with Burp Suite

Using Burp Suite, you can intercept and modify HTTP requests to test for SSRF vulnerabilities. For example, you can change the `url` parameter in a request to point to an internal IP address or a loopback address:

```http
GET /api/data?url=http://127.0.0.1:8080 HTTP/1.1
Host: vulnerable-app.com
```

If the application responds with data from the internal IP address, it indicates a potential SSRF vulnerability.

### Conclusion

Finding SSRF vulnerabilities requires a thorough understanding of both the application's code and its behavior. By using both white-box and black-box testing techniques, you can effectively identify and mitigate these risks.

---
<!-- nav -->
[[08-Exploiting SSRF to Access Internal Resources|Exploiting SSRF to Access Internal Resources]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/10-Hands-On Labs|Hands-On Labs]]
