---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a race condition is in the context of file uploads and how it can be exploited.**

A race condition in the context of file uploads occurs when there is a delay between the time a file is uploaded and the time it is validated. During this delay, an attacker can attempt to access or execute the uploaded file before the validation process removes it. This can be exploited by uploading a malicious file (such as a web shell) and quickly accessing it before the validation process detects and deletes it.

**Q2. How does Turbo Intruder help in exploiting race conditions during file uploads?**

Turbo Intruder is a Burp Suite extension that automates the exploitation of race conditions. It sends multiple requests concurrently, increasing the likelihood of accessing a file before it is validated and deleted. By configuring Turbo Intruder to send a POST request to upload a file and immediately follow it with GET requests to access the file, attackers can exploit the race condition effectively. This automation is crucial because the time window for exploitation is often measured in milliseconds.

**Q3. Describe the steps to exploit a race condition in a file upload feature using Turbo Intruder.**

To exploit a race condition using Turbo Intruder:

1. Identify the file upload feature and note the validation process.
2. Use Burp Repeater to capture the HTTP POST request for uploading a file.
3. Configure Turbo Intruder with the captured POST request and a subsequent GET request to access the file.
4. Customize the Turbo Intruder script to send the POST request followed by multiple GET requests in rapid succession.
5. Run the Turbo Intruder attack to attempt accessing the file before the validation process removes it.

**Q4. What is the purpose of the `check_for_viruses` and `check_file_type` functions in the file upload code?**

The `check_for_viruses` function ensures that the uploaded file is not malicious by checking for known virus signatures or other indicators of harmful content. The `check_file_type` function validates that the file is of an allowed type (e.g., JPEG or PNG). These functions are intended to prevent unauthorized file types from being uploaded and executed on the server.

**Q5. Why is it important to validate file types and check for viruses after moving the file to a temporary location?**

Validating file types and checking for viruses after moving the file to a temporary location helps mitigate the risk of executing malicious files. By performing these checks in a temporary location, the system can safely reject and delete invalid or potentially harmful files without exposing the server to risks. This practice also reduces the window of opportunity for attackers to exploit race conditions.

**Q6. How can recent real-world examples (CVEs/breaches) illustrate the importance of securing file upload features against race conditions?**

Recent breaches such as the 2021 SolarWinds supply chain attack highlight the critical importance of securing file upload features. Attackers often exploit vulnerabilities like race conditions to upload and execute malicious files. Ensuring robust validation and minimizing the time window for race conditions can significantly reduce the risk of such attacks. For example, CVE-2021-39144 involved a race condition in a file upload feature that allowed attackers to bypass security measures and gain unauthorized access.

---
<!-- nav -->
[[05-Understanding File Upload Vulnerabilities|Understanding File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/08-Lab 7 Web shell upload via race condition/00-Overview|Overview]]
