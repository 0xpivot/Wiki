---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a directory traversal vulnerability is and provide an example of how it can be exploited.**

A directory traversal vulnerability occurs when an application allows a user to access files or directories outside of the intended directory structure by manipulating input parameters. An example is an application that accepts a filename as input and serves the corresponding file. If the input is not properly validated, an attacker can use special characters like `../` to navigate to other directories and access sensitive files such as `/etc/passwd`.

**Q2. How can directory traversal vulnerabilities be introduced in code, and what is the root cause?**

Directory traversal vulnerabilities are typically introduced when user-supplied input is used to construct file paths without proper validation. The root cause is often insufficient input validation, allowing attackers to manipulate file paths and access unauthorized files. For instance, consider the following PHP code snippet:

```php
$template = isset($_COOKIE['template']) ? $_COOKIE['template'] : 'blue.php';
include("/home/users/phpguru/template/{$template}");
```

Here, the `$_COOKIE['template']` value is directly used in the `include` statement without validation, making it vulnerable to directory traversal attacks.

**Q3. Describe how to find directory traversal vulnerabilities from both a black box and a white box perspective.**

From a black box perspective, you can identify potential directory traversal vulnerabilities by mapping the application and identifying input vectors that interact with the file system. Common inputs include URL parameters, form fields, and cookies. Test these inputs with directory traversal payloads like `../`, `%2e%2e%2f`, and `..%c0%af`. Use a web application vulnerability scanner to automate this process.

From a white box perspective, review the application's source code to identify instances where user input is used to construct file paths. Look for functions like `include`, `require`, `open`, and `read`. Check if these functions are properly validating and sanitizing user input. Tools like static analysis tools can help automate this process.

**Q4. How can you exploit a directory traversal vulnerability when the application uses inadequate validation?**

When the application uses inadequate validation, you can exploit the vulnerability by crafting payloads that bypass the validation logic. Here are some strategies:

1. **Absolute Path**: If the application strips out relative path traversal sequences (`../`), try using the absolute path to the desired file.
   
2. **Non-Recursive Stripping**: If the application non-recursively removes path traversal sequences, you can use multiple sequences to bypass the stripping. For example, `../../../../etc/passwd` might be stripped to `../etc/passwd`.

3. **URL Encoding**: Encode the path traversal sequences using URL encoding (e.g., `%2e%2e%2f`) to bypass simple validation checks.

4. **Null Byte Injection**: If the application requires a specific file extension, use a null byte (`%00`) to terminate the filename prematurely. For example, `file.txt%00`.

**Q5. What are the best practices to prevent directory traversal vulnerabilities?**

To prevent directory traversal vulnerabilities, follow these best practices:

1. **Avoid User Input in File Paths**: Whenever possible, avoid using user-supplied input to construct file paths. Instead, use predefined paths or indexes.

2. **Input Validation**: Validate user input by comparing it against an allow list of permitted values. Ensure that only alphanumeric characters are accepted.

3. **Canonicalization**: Use file system APIs to canonicalize the path and verify that it starts with the expected directory. For example, in Java:

   ```java
   String filePath = "/path/to/directory/" + userInput;
   File file = new File(filePath);
   if (!file.getCanonicalPath().startsWith("/path/to/directory/")) {
       throw new SecurityException("Invalid path");
   }
   ```

By combining these layers of defense, you can significantly reduce the risk of directory traversal vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]]
