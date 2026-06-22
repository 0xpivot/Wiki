---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Setting Up Proxy Settings

When working with web security tools like Burp Suite, it's essential to configure your proxy settings correctly. This ensures that all your requests go through the proxy, allowing you to intercept and analyze the traffic.

### What is a Proxy?

A proxy is an intermediary server that acts as a gateway between your client and the internet. It can be used for various purposes, including caching, filtering, and security.

### Why Set Up Proxy Settings?

Setting up proxy settings is crucial when you're using tools like Burp Suite for debugging and intercepting traffic. It ensures that all your requests are routed through the proxy, allowing you to inspect and modify the traffic as needed.

### How to Set Up Proxy Settings

In Python, you can set up proxy settings using the `proxies` parameter in the `requests` library. Here’s how you can do it:

```python
import requests

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

response = requests.get('http://example.com', proxies=proxies)
print(response.text)
```

### Real-World Example

Consider a scenario where you're testing a web application hosted on `http://example.com`. By setting up the proxy, you can intercept and analyze the traffic between your client and the server.

### Pitfalls

While setting up proxy settings is useful for testing, it should be done with caution. In a production environment, using a proxy can introduce additional latency and potential security risks. Always ensure that you remove the proxy settings once your testing is complete.

### How to Prevent / Defend

#### Detection

To detect if proxy settings are being used, you can check the codebase for instances where the `proxies` parameter is set. Additionally, you can monitor network traffic to see if requests are being routed through a proxy.

#### Prevention

Always ensure that proxy settings are removed from production environments. For development and testing, consider using tools like Burp Suite to manage your proxy settings.

### Secure Code Fix

Here’s an example of how to handle proxy settings securely:

```python
import requests

def main():
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }

    response = requests.get('http://example.com', proxies=proxies)
    print(response.text)

if __name__ == '__main__':
    main()
```

### Explanation of the Code

- **Proxy Settings**: The `proxies` dictionary is defined to specify the proxy settings.
- **HTTPS Request**: The `requests.get` function is used to make an HTTP request to `http://example.com` with the specified proxy settings.

### Conclusion

Setting up proxy settings is a crucial step when using web security tools like Burp Suite. Always ensure that you remove the proxy settings once your testing is complete to avoid potential security risks.

---
<!-- nav -->
[[05-Disabling TLS Warnings|Disabling TLS Warnings]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/10-Lab 9 User ID controlled by request parameter with data leakage in redirect/00-Overview|Overview]] | [[07-Starting a Session Object|Starting a Session Object]]
