---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Lab Setup and Overview

In this lab, we will be working with a vulnerable image upload function. The application checks the contents of the file to verify that it is a genuine image, but it is still possible to upload and execute server-side code.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the sign-up button to create an account if you don't already have one.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select all labs.
6. Search for "file upload vulnerabilities."
7. Select lab number six titled "Remote Code Execution via Polyglot WebShell Upload."

### Lab Goal

The goal of this lab is to bypass the defense mechanisms in place, upload a PHP web shell, and exfiltrate the contents of the file `/home/Carlos/secret`.

### Provided Credentials

You are given the credentials of a regular user to log into your own account. Use these credentials to access the lab environment.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/01-Introduction to File Upload Vulnerabilities|Introduction to File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[03-Exfiltrating the Secret File|Exfiltrating the Secret File]]
