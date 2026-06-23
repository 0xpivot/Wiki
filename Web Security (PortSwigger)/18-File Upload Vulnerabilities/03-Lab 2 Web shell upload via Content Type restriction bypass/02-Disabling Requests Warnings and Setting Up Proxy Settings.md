---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Disabling Requests Warnings and Setting Up Proxy Settings

### Disabling Insecure Request Warnings

When working with HTTP requests in Python using the `requests` library, you might encounter warnings related to insecure connections. These warnings can clutter your output and are generally useful during development but can be disabled in production environments. To disable these warnings, you can use the following code snippet:

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL certificate verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
```

#### Why Disable Warnings?

Disabling warnings is particularly useful when you are working with self-signed certificates or when you are intentionally bypassing SSL verification for testing purposes. However, it is important to understand the security implications of disabling these warnings. Disabling them means you are ignoring potential security issues related to man-in-the-middle attacks or other SSL/TLS vulnerabilities.

### Setting Up Proxy Settings

To ensure that all HTTP traffic is routed through a proxy like Burp Suite, you need to configure the `proxies` parameter in the `requests` library. This is crucial for intercepting and analyzing HTTP traffic during penetration testing or security assessments.

```python
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}
```

#### Why Use a Proxy?

Using a proxy like Burp Suite allows you to inspect, modify, and replay HTTP requests and responses. This is essential for identifying and exploiting vulnerabilities such as file upload vulnerabilities, SQL injection, cross-site scripting (XSS), and more.

### Example Code Snippet

Here is a complete example of setting up the environment with disabled warnings and configured proxies:

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL certificate verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set up proxy settings
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

# Example usage
response = requests.get('http://example.com', proxies=proxies, verify=False)
print(response.text)
```

### Main Method and Command Line Arguments

The main method is typically used to handle the entry point of a script. It checks the command line arguments and initializes the necessary components.

```python
import sys
import requests

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <URL>")
        print("Example: python script.py http://www.example.com")
        sys.exit(1)

    url = sys.argv[1]
    session = requests.Session()
    # Further logic to interact with the URL using the session

if __name__ == "__main__":
    main()
```

### Explanation of the Code

- **Command Line Arguments**: The script expects one command line argument, which is the URL of the target application.
- **Session Object**: A `requests.Session()` object is created to maintain a persistent connection to the server, which can improve performance and allow for better handling of cookies and headers.

### Real-World Examples

#### CVE-2021-3129: Apache Struts 2 File Upload Vulnerability

In 2021, a critical vulnerability was discovered in Apache Struts 2, allowing attackers to upload malicious files due to improper validation of file types. This vulnerability could lead to remote code execution.

**Example Exploit**:

```python
import requests

url = "http://target-server/upload"
file_path = "/path/to/malicious/file.php"

files = {'file': open(file_path, 'rb')}
response = requests.post(url, files=files, proxies=proxies, verify=False)

print(response.text)
```

**Detection and Prevention**:

- **Detection**: Monitor file uploads for suspicious file types or patterns.
- **Prevention**: Implement strict file type validation and content inspection.

### How to Prevent / Defend Against File Upload Vulnerabilities

#### Secure Coding Practices

1. **Strict File Type Validation**: Ensure that only allowed file types are uploaded.
2. **Content Inspection**: Scan uploaded files for malicious content.
3. **File Name Sanitization**: Avoid using user-provided file names directly.

**Vulnerable Code**:

```python
import os

def upload_file(file):
    filename = file.filename
    file.save(os.path.join("/uploads", filename))
```

**Secure Code**:

```python
import os
import re

def upload_file(file):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg'}
    filename = file.filename
    extension = os.path.splitext(filename)[1][1:].lower()

    if extension not in allowed_extensions:
        raise ValueError("Invalid file type")

    sanitized_filename = re.sub(r'[^\w\.-]', '_', filename)
    file.save(os.path.join("/uploads", sanitized_filename))
```

### Conclusion

Understanding and securing file upload mechanisms is crucial for maintaining the integrity and security of web applications. By implementing strict validation, content inspection, and proper sanitization, you can significantly reduce the risk of file upload vulnerabilities. Always ensure that your security measures are up-to-date and tested regularly.

### Practice Labs

For hands-on practice with file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including file upload vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to test and learn about different types of web vulnerabilities, including file upload vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/03-Lab 2 Web shell upload via Content Type restriction bypass/01-Introduction to File Upload Vulnerabilities|Introduction to File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/03-Lab 2 Web shell upload via Content Type restriction bypass/00-Overview|Overview]] | [[03-File Upload Vulnerabilities Web Shell Upload via Content Type Restriction Bypass|File Upload Vulnerabilities Web Shell Upload via Content Type Restriction Bypass]]
