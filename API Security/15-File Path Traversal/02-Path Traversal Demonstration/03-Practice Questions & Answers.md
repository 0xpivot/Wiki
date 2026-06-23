---
course: API Security
topic: File Path Traversal
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is file path traversal and how does it work in the context of an API?**

File path traversal, also known as directory traversal, is a technique used by attackers to access restricted files and directories on a web server by manipulating the input parameters of a web application. In the context of an API, an attacker might manipulate the input parameters to navigate outside the intended directory structure and access sensitive files such as configuration files, log files, or even system files like `/etc/passwd` or `/etc/shadow`.

For example, if an API endpoint allows users to specify a filename to retrieve, an attacker could provide a specially crafted input like `../../../../etc/passwd` to navigate up several directory levels and access the system's password file.

**Q2. How can you exploit a file path traversal vulnerability in an API using URL encoding?**

To exploit a file path traversal vulnerability using URL encoding, an attacker encodes special characters in the path to bypass simple input validation mechanisms. For instance, instead of using the forward slash (`/`) directly, the attacker uses its URL-encoded form (`%2F`). This can help evade basic filters that block literal slashes.

Here’s an example payload:
```
http://example.com/api/read?filename=../../../../etc/passwd%23
```
In this case, `%2F` represents the forward slash, and `%23` is the URL-encoded form of the hash symbol (`#`), which can be used to comment out additional parts of the URL.

**Q3. Explain why reading log files through a file path traversal vulnerability can be dangerous.**

Reading log files through a file path traversal vulnerability can be dangerous because log files often contain sensitive information such as user credentials, error messages that reveal internal system details, and other operational data. If an attacker gains access to these logs, they can extract valuable information that can be used for further attacks or to understand the internal workings of the system.

For example, if an application logs detailed error messages that include stack traces, an attacker might find hints about the underlying technology stack, version numbers, or even specific vulnerabilities that can be exploited.

**Q4. How can an API developer prevent file path traversal attacks?**

To prevent file path traversal attacks, API developers should implement the following measures:

1. **Input Validation**: Validate all user inputs to ensure they conform to expected formats and values. For example, if the input should be a filename within a specific directory, validate that the filename does not contain path traversal sequences.

2. **Whitelist Filenames**: Use a whitelist approach to allow only specific filenames or patterns. This ensures that only predefined files can be accessed.

3. **Canonicalize Paths**: Canonicalize the input path to remove any relative path components (like `../`) before processing it. This helps prevent navigation outside the intended directory.

4. **Use Safe APIs**: Utilize safe file handling APIs that automatically handle path traversal issues. For example, in Node.js, the `fs` module has methods like `fs.readFile()` that can be used safely when combined with proper validation.

5. **Least Privilege Principle**: Ensure that the application runs with the least privileges necessary. This limits the damage that can be done if an attacker manages to exploit a file path traversal vulnerability.

**Q5. Provide a recent real-world example of a file path traversal vulnerability and explain how it was exploited.**

One notable example is the CVE-2019-16758, which affected the WordPress plugin WP File Download. The vulnerability allowed attackers to bypass the intended directory restrictions and access arbitrary files on the server, including sensitive configuration files.

In this case, the plugin did not properly sanitize user input for the file download functionality. An attacker could craft a request like:
```
https://example.com/wp-content/plugins/wp-file-download/download.php?file=../../../../wp-config.php
```
This would allow the attacker to download the `wp-config.php` file, which contains sensitive database credentials and other configuration settings. By exploiting this vulnerability, an attacker could gain unauthorized access to the website's backend and potentially take control of the entire site.

**Q6. How can you test for file path traversal vulnerabilities in an API?**

To test for file path traversal vulnerabilities in an API, you can perform the following steps:

1. **Identify Input Points**: Identify all input points where the API accepts filenames or paths, such as query parameters, form fields, or JSON payloads.

2. **Craft Test Payloads**: Create test payloads that attempt to traverse directories. Examples include:
   - `../../../etc/passwd`
   - `C:\Windows\System32\cmd.exe`
   - `../../../../etc/shadow`

3. **URL Encoding**: Encode special characters in your payloads to bypass simple input validation. For example:
   - `%2E%2E%2F%2E%2E%2Fetc%2Fpasswd`
   - `%252e%252e%2f%252e%252e%2fetc%2fpasswd`

4. **Automated Tools**: Use automated tools like Burp Suite, OWASP ZAP, or custom scripts to automate the testing process and generate a variety of test cases.

5. **Review Responses**: Analyze the responses to determine if the API is returning unexpected files or error messages that indicate successful traversal.

By systematically testing these inputs, you can identify potential file path traversal vulnerabilities and take appropriate actions to mitigate them.

---
<!-- nav -->
[[API Security/15-File Path Traversal/02-Path Traversal Demonstration/02-File Path Traversal|File Path Traversal]] | [[API Security/15-File Path Traversal/02-Path Traversal Demonstration/00-Overview|Overview]]
