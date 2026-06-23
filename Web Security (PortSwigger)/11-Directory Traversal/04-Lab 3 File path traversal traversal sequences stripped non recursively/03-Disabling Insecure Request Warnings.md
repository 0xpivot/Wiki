---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Disabling Insecure Request Warnings

When working with web security tools and scripts, it's often necessary to interact with servers that may have self-signed certificates or other SSL/TLS issues. These issues can cause Python's `urllib3` library to raise `InsecureRequestWarning` exceptions. To avoid these warnings cluttering your output, you can disable them programmatically.

### What is `InsecureRequestWarning`?

The `InsecureRequestWarning` is a warning raised by `urllib3` when a request is made to a server using HTTPS but the certificate cannot be verified. This typically happens when the server uses a self-signed certificate or the certificate chain is incomplete.

### Why Disable `InsecureRequestWarning`?

Disabling these warnings is useful in development and testing environments where self-signed certificates are common. However, in production environments, it's generally better to address the root cause of the warning rather than suppress it.

### How to Disable `InsecureRequestWarning`

To disable `InsecureRequestWarning`, you can use the following code snippet:

```python
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Disable InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
```

### Real-World Example

Consider a scenario where you are developing a script to test a local web application that uses a self-signed certificate. Without disabling the warning, you might see output like this:

```
InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/security.html
```

By disabling the warning, you can focus on the actual output of your script without being distracted by these warnings.

### Pitfalls

While disabling the warning can be useful during development, it's important to remember that it should not be done in a production environment. Suppressing the warning without addressing the underlying issue can lead to security vulnerabilities.

### How to Prevent / Defend

**Detection**: Use tools like `openssl s_client` to verify the SSL/TLS certificate of the server.

**Prevention**: Ensure that all servers use valid, trusted certificates. If self-signed certificates are necessary, configure your client to trust those specific certificates.

**Secure Code Fix**:

```python
# Vulnerable code
import requests

response = requests.get('https://localhost', verify=False)

# Secure code
import requests
import ssl

# Trust custom CA bundle
response = requests.get('https://localhost', verify='/path/to/ca-bundle.pem')
```

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/04-Lab 3 File path traversal traversal sequences stripped non recursively/02-Directory Traversal Vulnerability|Directory Traversal Vulnerability]] | [[Web Security (PortSwigger)/11-Directory Traversal/04-Lab 3 File path traversal traversal sequences stripped non recursively/00-Overview|Overview]] | [[04-Main Method and Command Line Arguments|Main Method and Command Line Arguments]]
