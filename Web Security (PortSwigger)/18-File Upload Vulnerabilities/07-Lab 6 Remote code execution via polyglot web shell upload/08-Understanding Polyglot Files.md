---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Understanding Polyglot Files

A polyglot file is a file that can be interpreted in multiple ways depending on the context. In the context of web security, polyglot files can be crafted to appear as valid images while also containing executable code.

### How Polyglot Files Work

Polyglot files leverage the fact that many file formats have a flexible structure. By carefully crafting the file, it can be made to pass the initial validation checks (e.g., checking for a valid image header) while still containing executable code.

#### Example of a Polyglot File

Consider the following polyglot file that appears as a valid PNG image but also contains PHP code:

```php
<?php
// PHP code to be executed
echo "This is a PHP web shell.";
?>
```

When uploaded, the file will pass the initial validation checks as a valid PNG image, but when accessed via a web browser, the PHP code will be executed.

### Creating a Polyglot File

To create a polyglot file, you can use tools like `exiftool` to embed PHP code within an image file. Here is an example of how to create a polyglot file using `exiftool`:

```bash
# Create a new PNG image
convert -size 100x100 xc:white test.png

# Embed PHP code within the image
exiftool -Comment="<?php echo 'This is a PHP web shell.'; ?>" test.png
```

This will create a PNG image with embedded PHP code that can be executed when accessed via a web browser.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/07-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[09-Uploading the Polyglot File|Uploading the Polyglot File]]
