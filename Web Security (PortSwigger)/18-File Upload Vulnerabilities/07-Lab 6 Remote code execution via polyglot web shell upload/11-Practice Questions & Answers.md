---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the polyglot technique works in the context of the lab exercise.**

The polyglot technique used in the lab exercise involves embedding a PHP web shell within an image file in such a way that the image appears valid to the server's validation process while still allowing the PHP code to be executed. The `exiftool` command-line tool is used to inject the PHP code into the metadata of a JPEG image. When the server processes the image, it sees it as a valid image file due to its correct header and structure. However, when accessed via a web request, the embedded PHP code can be executed, allowing remote code execution.

**Q2. How would you exploit the file upload vulnerability described in the lab?**

To exploit the file upload vulnerability, follow these steps:

1. Create a PHP web shell that reads the contents of the `/home/Carlos/secret` file.
2. Use `exiftool` to embed the PHP code into a JPEG image file.
3. Upload the modified image file through the application’s file upload feature.
4. Access the uploaded image file via a web request to trigger the execution of the embedded PHP code.
5. Extract the secret information from the response.

Here is an example of the PHP code that could be used:

```php
<?php
echo file_get_contents("/home/Carlos/secret");
?>
```

And the `exiftool` command to embed this code into a JPEG image:

```bash
exiftool -Comment="<?php echo file_get_contents('/home/Carlos/secret'); ?>" image.jpg
```

**Q3. Why does the server reject the initial attempt to upload a plain PHP file?**

The server rejects the initial attempt to upload a plain PHP file because it performs a check to ensure that the uploaded file is a valid image. This check typically involves examining the file headers and structure to confirm that they match those of a known image format (e.g., JPEG). A plain PHP file lacks these characteristics and thus fails the validation.

**Q4. What recent real-world examples demonstrate the risks associated with file upload vulnerabilities?**

One notable example is the 2017 Equifax data breach, where attackers exploited a vulnerability in Apache Struts, a web application framework. Among other issues, the vulnerability allowed for remote code execution through file uploads. Attackers were able to upload malicious files that were executed on the server, leading to the exposure of sensitive personal data of millions of individuals.

Another example is the 2019 Magecart attack on British Airways, where attackers injected malicious JavaScript into the website, potentially stealing payment card details. While this attack did not involve file upload vulnerabilities directly, it highlights the broader risks associated with inadequate input validation and server-side code execution.

**Q5. How would you configure a web server to mitigate the risk of file upload vulnerabilities?**

To mitigate the risk of file upload vulnerabilities, a web server can be configured in several ways:

1. **Strict File Type Validation**: Ensure that only specific file types are accepted for upload. This can be done by checking the file extension and MIME type.
   
   ```php
   $allowedTypes = ['image/jpeg', 'image/png'];
   $fileType = $_FILES['upload']['type'];
   if (!in_array($fileType, $allowedTypes)) {
       die('Invalid file type.');
   }
   ```

2. **Content Inspection**: Use tools like `exiftool` or libraries to inspect the content of uploaded files to ensure they do not contain executable code.

3. **File Storage Isolation**: Store uploaded files outside the web root directory to prevent direct access via URLs.

4. **Limit File Size**: Set limits on the size of uploaded files to prevent resource exhaustion attacks.

5. **Use Content Security Policies (CSP)**: Implement CSP to restrict the sources from which resources can be loaded, reducing the risk of XSS attacks.

By implementing these measures, the risk of file upload vulnerabilities can be significantly reduced.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/10-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]]
