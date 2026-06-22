---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is a file upload vulnerability and how can it be exploited?**

A file upload vulnerability occurs when a web application allows users to upload files without proper validation. This can lead to various exploits, such as uploading malicious scripts that can be executed on the server. For instance, an attacker could upload a PHP script that reads sensitive files like `/etc/passwd`. To exploit this, the attacker needs to:

1. Identify a file upload feature in the application.
2. Ensure the uploaded file can be executed by the server.
3. Trigger the execution of the malicious script by accessing the uploaded file through the application.

**Q2. How do file upload vulnerabilities affect the CIA triad (Confidentiality, Integrity, Availability)?**

File upload vulnerabilities can significantly impact the CIA triad:

- **Confidentiality**: Attackers can access sensitive data stored on the server, such as user credentials or private files.
- **Integrity**: Malicious files can alter the content of the application or database, leading to unauthorized changes.
- **Availability**: Large file uploads can consume server resources, causing a denial-of-service condition.

**Q3. How can you identify file upload vulnerabilities from a black box perspective?**

To identify file upload vulnerabilities from a black box perspective:

1. **Map the Application**: Identify the technologies used (e.g., PHP, Java).
2. **Locate Upload Points**: Find all instances where users can upload files.
3. **Test Validation**: Attempt to upload different types of files (e.g., `.php`, `.jsp`) and observe the response.
4. **Bypass Validation**: Use techniques like changing the `Content-Type` header, URL encoding, or using null bytes to bypass validation checks.

**Q4. Explain how to exploit a file upload vulnerability with insufficient file type validation.**

If a file upload vulnerability lacks proper validation, an attacker can exploit it by:

1. Uploading a malicious script (e.g., a PHP web shell).
2. Intercepting the request in a proxy tool (e.g., Burp Suite) and modifying the `Content-Type` header to mimic a benign file type (e.g., `image/jpeg`).
3. Accessing the uploaded file through the application to trigger its execution.

Example payload:
```php
<?php
if(isset($_GET['cmd'])) {
    echo "<pre>".shell_exec($_GET['cmd'])."</pre>";
}
?>
```

**Q5. Why is using a whitelist approach preferable to a blacklist approach for file upload validation?**

Using a whitelist approach is preferable because:

- **Completeness**: A whitelist explicitly defines allowed file types, reducing the chance of missing dangerous file extensions.
- **Security**: Blacklists can be incomplete, leaving gaps for attackers to exploit (e.g., `.php2`, `.php3`).

Example of a whitelist implementation:
```python
allowed_extensions = ['jpg', 'jpeg', 'png']
file_extension = filename.split('.')[-1]
if file_extension.lower() not in allowed_extensions:
    raise ValueError("Invalid file type")
```

**Q6. How can you prevent file upload vulnerabilities in a web application?**

To prevent file upload vulnerabilities:

1. **Use Whitelists**: Only allow specific file types.
2. **Rename Files**: Avoid naming conflicts and reveal less information.
3. **Validate Before Saving**: Ensure files are fully validated before saving them to the file system.
4. **Use Established Frameworks**: Leverage well-tested frameworks for handling file uploads.

**Q7. What recent real-world examples demonstrate the impact of file upload vulnerabilities?**

Recent examples include:

- **CVE-2021-3560**: A vulnerability in the WordPress plugin "WP File Download" allowed unauthenticated users to upload arbitrary files, leading to remote code execution.
- **CVE-2020-14882**: A vulnerability in the Joomla! CMS allowed attackers to upload and execute PHP files, compromising the server.

These examples highlight the importance of proper validation and the potential severe impacts of file upload vulnerabilities.

---
<!-- nav -->
[[07-White Box Testing|White Box Testing]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/01-File Upload Vulnerabilities Complete Guide/00-Overview|Overview]]
