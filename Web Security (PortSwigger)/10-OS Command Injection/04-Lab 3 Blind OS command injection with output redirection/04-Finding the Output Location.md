---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Finding the Output Location

### Identifying Writable Directories

In many web applications, certain directories are writable for storing user-generated content such as images, logs, etc. To find these directories, you can:

- **Review Application Documentation**: Check if the documentation mentions any writable directories.
- **Inspect File Uploads**: Look at how file uploads are handled and where they are stored.
- **Use Directory Traversal**: Test for directory traversal vulnerabilities to identify writable directories.

### Example: Finding the Public Directory

Assume the application stores images in the `/public/images` directory. You can verify this by uploading an image and checking where it is stored.

#### Vulnerable Code Example

```python
import os

def upload_image(file):
    filename = file.filename
    file.save(os.path.join('/public/images', filename))
```

#### Secure Code Example

```python
import os

def upload_image(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join('/public/images', filename))
```

### Detection and Prevention

**Detection**:
- **File Upload Tests**: Test file uploads to see where files are stored.
- **Directory Traversal Scans**: Use automated scanners to detect directory traversal vulnerabilities.

**Prevention**:
- **Validate File Paths**: Ensure that file paths are valid and within the intended directory.
- **Use Secure Filenames**: Use functions like `secure_filename` to sanitize filenames.

---
<!-- nav -->
[[03-Confirming the Vulnerability|Confirming the Vulnerability]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/00-Overview|Overview]] | [[05-How to Prevent  Defend Against OS Command Injection|How to Prevent  Defend Against OS Command Injection]]
