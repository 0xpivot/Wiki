---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against File Upload Vulnerabilities

Preventing file upload vulnerabilities requires a combination of proper validation, sanitization, and secure coding practices. Here are some key strategies:

### Secure Coding Practices

1. **Validate File Types**: Ensure that only allowed file types can be uploaded.
2. **Sanitize File Names**: Remove or escape characters that could be used for directory traversal attacks.
3. **Limit File Sizes**: Set reasonable limits on file sizes to prevent denial-of-service attacks.
4. **Use Secure File Storage**: Store uploaded files in a location that is not accessible via the web.
5. **Implement Content Filtering**: Use tools like ClamAV to scan uploaded files for viruses and malware.

### Example Secure Code

Here’s an example of secure code for handling file uploads in Python using Flask:

```python
from flask import Flask, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/var/www/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return "File successfully uploaded"
    else:
        return "Invalid file type"

if __name__ == '__main__':
    app.run()
```

### Detection and Prevention

1. **Static Analysis Tools**: Use tools like SonarQube to detect insecure file handling patterns in the code.
2. **Dynamic Analysis Tools**: Use tools like Burp Suite or OWASP ZAP to test the application for file upload vulnerabilities.
3. **Security Policies**: Implement strict security policies for file uploads, including regular audits and penetration testing.

### Secure Configuration

1. **Web Server Configuration**: Ensure that the web server is configured to prevent directory listing and direct access to uploaded files.
2. **Firewall Rules**: Use firewall rules to restrict access to the directory where uploaded files are stored.
3. **Access Control**: Implement role-based access control to ensure that only authorized users can upload files.

### Example Secure Configuration

Here’s an example of secure configuration for Apache:

```apache
<Directory "/var/www/uploads">
    Options -Indexes
    Order deny,allow
    Deny from all
</Directory>
```

### Hands-On Labs

To practice identifying and mitigating file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on file upload vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

### Conclusion

File upload vulnerabilities are a significant threat to web applications. By understanding the nature of these vulnerabilities, performing thorough testing, and implementing robust security measures, you can significantly reduce the risk of exploitation. Always stay vigilant and keep your security practices up-to-date to protect against emerging threats.

---
<!-- nav -->
[[05-Gray Box Testing|Gray Box Testing]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/01-File Upload Vulnerabilities Complete Guide/00-Overview|Overview]] | [[07-White Box Testing|White Box Testing]]
