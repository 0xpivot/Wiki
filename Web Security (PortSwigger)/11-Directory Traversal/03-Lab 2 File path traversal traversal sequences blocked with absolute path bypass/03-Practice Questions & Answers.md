---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary goal of the lab described in the lecture?**

The primary goal of the lab is to exploit a file path traversal vulnerability to retrieve the contents of the `ATC passWD` file. The application blocks common traversal sequences but allows the use of absolute paths to bypass these restrictions.

**Q2. How did you exploit the path traversal vulnerability manually?**

To exploit the path traversal vulnerability manually, I initially tried using common traversal sequences like `../` but encountered a 400 Bad Request error indicating that the application blocked these sequences. Then, I attempted to directly use the absolute path to the desired file, which successfully retrieved the contents of the `ATC passWD` file.

**Q3. Explain how the Python script exploits the path traversal vulnerability.**

The Python script exploits the path traversal vulnerability by constructing a URL that points directly to the `ATC passWD` file using its absolute path. The script performs an HTTP GET request to this URL, disables TLS certificate verification, and sends the request through Burp Proxy for debugging purposes. Upon receiving the response, the script checks if the expected content (e.g., a specific string) is present in the response to confirm the success of the exploit. If successful, it prints the content of the `ATC passWD` file.

**Q4. How does the script handle errors and ensure proper usage?**

The script handles errors and ensures proper usage by checking the number of command-line arguments. If the number of arguments is incorrect, the script prints usage instructions and exits. Additionally, after performing the exploit, the script checks if the expected content is present in the response. If the expected content is not found, the script prints "exploit failed" and exits.

**Q5. What recent real-world examples demonstrate the importance of securing against path traversal vulnerabilities?**

Recent real-world examples include the CVE-2021-26084 vulnerability in Apache Tomcat, where improper validation of file paths allowed attackers to read arbitrary files on the server. Another example is the CVE-2021-21972 in Atlassian Confluence, where a path traversal vulnerability allowed unauthorized access to sensitive files. These examples highlight the critical importance of securing applications against path traversal attacks to prevent data breaches and unauthorized access.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/03-Lab 2 File path traversal traversal sequences blocked with absolute path bypass/02-Directory Traversal Vulnerability|Directory Traversal Vulnerability]] | [[Web Security (PortSwigger)/11-Directory Traversal/03-Lab 2 File path traversal traversal sequences blocked with absolute path bypass/00-Overview|Overview]]
