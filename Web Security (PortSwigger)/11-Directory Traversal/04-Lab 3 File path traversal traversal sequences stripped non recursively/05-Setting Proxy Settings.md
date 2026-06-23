---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Setting Proxy Settings

Setting up a proxy is essential for debugging and intercepting network traffic. Tools like Burp Suite allow you to inspect and modify HTTP requests and responses.

### What is a Proxy?

A proxy acts as an intermediary between your client and the server. It forwards requests from the client to the server and returns the server's response back to the client. Proxies are commonly used for debugging, monitoring, and security purposes.

### Why Set Proxy Settings?

Setting proxy settings allows you to route all HTTP and HTTPS traffic through a tool like Burp Suite. This is particularly useful for web security testing, as it enables you to inspect and manipulate the traffic.

### How to Set Proxy Settings

To set proxy settings in Python, you can use the `proxies` parameter in the `requests` library. Here’s an example:

```python
import requests

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

response = requests.get('http://example.com', proxies=proxies)
```

### Real-World Example

Suppose you are testing a web application hosted at `http://localhost:8080`. You want to use Burp Suite to intercept and analyze the traffic. By setting the proxy, you can ensure that all requests are routed through Burp Suite.

### Pitfalls

Using a proxy can introduce latency and may affect the performance of your tests. Additionally, if the proxy is misconfigured, it can lead to connectivity issues.

### How to Prevent / Defend

**Detection**: Use network monitoring tools to ensure that traffic is being routed through the proxy as expected.

**Prevention**: Always verify the proxy settings and ensure that the proxy tool is properly configured.

**Secure Code Fix**:

```python
# Vulnerable code
import requests

response = requests.get('http://example.com')

# Secure code
import requests

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

response = requests.get('http://example.com', proxies=proxies)
```

---
<!-- nav -->
[[04-Main Method and Command Line Arguments|Main Method and Command Line Arguments]] | [[Web Security (PortSwigger)/11-Directory Traversal/04-Lab 3 File path traversal traversal sequences stripped non recursively/00-Overview|Overview]] | [[Web Security (PortSwigger)/11-Directory Traversal/04-Lab 3 File path traversal traversal sequences stripped non recursively/06-Practice Questions & Answers|Practice Questions & Answers]]
