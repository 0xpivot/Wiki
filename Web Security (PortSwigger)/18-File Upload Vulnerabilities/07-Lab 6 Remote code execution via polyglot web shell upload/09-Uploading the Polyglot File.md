---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Uploading the Polyglot File

Once you have created the polyglot file, you can upload it to the vulnerable image upload function in the lab.

### Uploading the File

To upload the file, you can use a tool like `curl` to send an HTTP POST request with the file attached:

```http
POST /upload.php HTTP/1.1
Host: vulnerable-app.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1000

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.png"
Content-Type: image/png

[Binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

### HTTP Request and Response

Here is a complete example of the HTTP request and response for uploading the file:

```http
HTTP Request:
POST /upload.php HTTP/1.1
Host: vulnerable-app.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1000

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.png"
Content-Type: image/png

[Binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--

HTTP Response:
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 100
Content-Type: text/html; charset=UTF-8

File uploaded successfully.
```

### Verifying the Upload

After uploading the file, you should verify that it has been uploaded correctly and that the PHP code can be executed. You can do this by accessing the uploaded file via a web browser or using a tool like `curl` to make an HTTP GET request:

```http
GET /uploads/test.png HTTP/1.1
Host: vulnerable-app.example.com
```

If the PHP code is executed, you should see the output of the PHP code in the response.

---
<!-- nav -->
[[08-Understanding Polyglot Files|Understanding Polyglot Files]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/10-Conclusion|Conclusion]]
