---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Introduction to Server-Side Request Forgery (SSRF)

Server-Side Request Forgery (SSRF) is a type of web application vulnerability that allows an attacker to induce the server-side application to make HTTP requests to an unintended endpoint. This can lead to unauthorized data retrieval, internal network scanning, and even remote code execution. SSRF attacks can be categorized into two main types: **Blind SSRF** and **In-Band SSRF**.

### What is Blind SSRF?

Blind SSRF occurs when the server makes a request to an external resource, but the response from that request is not returned to the attacker. Instead, the attacker relies on some form of out-of-band detection to confirm whether the request was successful. This type of SSRF is often harder to detect and exploit but can still be very dangerous.

### Why Does Blind SSRF Matter?

Blind SSRF can be particularly dangerous because it allows attackers to perform actions on the server without receiving direct feedback. This can enable them to scan internal networks, read sensitive files, or even execute commands on the server. The lack of immediate feedback makes these attacks stealthier and harder to trace.

### How Does Blind SSRF Work Under the Hood?

To understand how Blind SSRF works, consider the following scenario:

1. **Vulnerable Parameter**: The server application has a parameter that accepts user input and uses it to make an HTTP request.
2. **Induced Request**: An attacker manipulates this parameter to make the server send a request to an unintended endpoint.
3. **Out-of-Band Detection**: The attacker uses an external service (such as Burp Collaborator) to detect whether the request was made successfully.

### Real-World Example: CVE-2021-21972

A notable real-world example of SSRF is CVE-2021-21972, which affected the Jenkins CI/CD system. This vulnerability allowed attackers to perform SSRF attacks by manipulating the `JENKINS_CRUMB` parameter. By doing so, they could induce the server to make requests to arbitrary endpoints, potentially leading to unauthorized data retrieval or further exploitation.

### Lab Setup: PortSwigger Web Security Academy

For this lab, we will use the PortSwigger Web Security Academy, which provides a controlled environment to practice and learn about web security vulnerabilities. The lab we will focus on is titled "Blind SSRF without a Band Detection."

### Accessing the Lab

To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Click on the "Academy" tab.
3. Select the "SSRF" learning path.
4. Navigate to "Finding and Exploiting Blind SSRF Vulnerabilities."
5. Click on "Lab No. 6: Blind SSRF without a Band Detection."

### Lab Overview

The lab environment uses analytics software that fetches the URL specified in the `Referer` header when a product page is loaded. The goal is to use this functionality to cause an HTTP request to the public Burp Collaborator server.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/02-Common Pitfalls and Mistakes|Common Pitfalls and Mistakes]]
