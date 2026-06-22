---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Introduction to File Upload Vulnerabilities

File upload vulnerabilities are a critical aspect of web security, particularly in applications that allow users to upload files. These vulnerabilities can lead to severe security issues such as remote code execution (RCE), data leakage, and unauthorized access. In this chapter, we will delve deep into the specific vulnerability of remote code execution via polyglot web shell uploads, focusing on a practical lab scenario from the Web Security Academy.

### What Are File Upload Vulnerabilities?

File upload vulnerabilities occur when an application allows users to upload files without proper validation or sanitization. This can enable attackers to upload malicious files, such as web shells, which can be executed on the server to gain unauthorized access or perform other malicious activities.

#### Why Do File Upload Vulnerabilities Matter?

File upload vulnerabilities are significant because they can lead to:

- **Remote Code Execution (RCE):** Attackers can execute arbitrary code on the server, potentially taking control of the entire system.
- **Data Leakage:** Malicious files can be used to exfiltrate sensitive data from the server.
- **Denial of Service (DoS):** Malicious files can be designed to crash the server or consume excessive resources.

### Real-World Examples

Recent real-world examples of file upload vulnerabilities include:

- **CVE-2021-26084:** A vulnerability in the WordPress plugin "WP File Manager" allowed attackers to upload and execute arbitrary PHP files, leading to RCE.
- **CVE-2022-22965:** A vulnerability in the Joomla CMS allowed attackers to upload and execute PHP files through the "com_media" component, leading to RCE.

These vulnerabilities highlight the importance of securing file upload functionalities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/02-Lab Setup and Overview|Lab Setup and Overview]]
