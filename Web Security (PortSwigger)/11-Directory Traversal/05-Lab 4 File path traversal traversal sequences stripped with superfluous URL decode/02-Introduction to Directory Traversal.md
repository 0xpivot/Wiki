---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Introduction to Directory Traversal

Directory traversal, also known as path traversal, is a type of web security vulnerability that allows attackers to access restricted files, directories, and executables on a web server. This vulnerability arises due to improper validation of user-supplied input used to reference files. Attackers can manipulate these inputs to navigate outside the intended directory structure, potentially accessing sensitive information such as configuration files, source code, or even system binaries.

### Why Directory Traversal Matters

Directory traversal attacks can lead to significant security breaches. By accessing unauthorized files, attackers can gain insights into the internal workings of an application, steal sensitive data, or even execute arbitrary commands on the server. This can result in data breaches, loss of intellectual property, and potential legal ramifications for the organization.

### How Directory Traversal Works

The core mechanism of directory traversal involves manipulating file paths to traverse up the directory tree. Typically, this is achieved by injecting special characters like `../` (which represents moving up one directory level) into the input fields of a web application. For instance, consider a web application that allows users to view images by specifying a filename:

```plaintext
http://example.com/images/<filename>
```

If the application does not properly validate the `<filename>` input, an attacker could inject `../` to move up the directory tree and access other files:

```plaintext
http://example.com/images/../../etc/passwd
```

This would allow the attacker to read the `/etc/passwd` file, which contains user account information.

### Real-World Examples

One notable real-world example of a directory traversal vulnerability is CVE-2019-11510, which affected the WordPress REST API. This vulnerability allowed attackers to read arbitrary files on the server, including sensitive configuration files and source code. Another example is CVE-2020-1938, which affected the Apache Struts framework, allowing attackers to read arbitrary files and potentially execute commands on the server.

### Lab Setup

To understand and practice directory traversal, we will use the Web Security Academy provided by PortSwigger. You can access the lab by following these steps:

1. Visit the URL: [PortSwigger Web Security Academy](https://portswigger.net/web-security)
2. Click on the sign-up button to create an account.
3. Once logged in, navigate to the Academy section.
4. Select the learning path for directory traversal.
5. Find and open lab number four titled "File Path Traversal, Traversal Sequences, tripped with superfluous URL decode."

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/05-Lab 4 File path traversal traversal sequences stripped with superfluous URL decode/01-Introduction to Directory Traversal Vulnerabilities|Introduction to Directory Traversal Vulnerabilities]] | [[Web Security (PortSwigger)/11-Directory Traversal/05-Lab 4 File path traversal traversal sequences stripped with superfluous URL decode/00-Overview|Overview]] | [[03-Directory Traversal Vulnerabilities|Directory Traversal Vulnerabilities]]
