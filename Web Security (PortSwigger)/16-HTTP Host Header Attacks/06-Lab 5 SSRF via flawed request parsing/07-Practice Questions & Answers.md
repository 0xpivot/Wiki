---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how SSRF via flawed request parsing can be exploited to access an internal admin panel.**

To exploit SSRF via flawed request parsing, an attacker needs to manipulate the request headers, particularly the `Host` header, to trick the server into accessing internal resources. The server should ideally validate the `Host` header against a whitelist of allowed domains. If the validation is flawed, an attacker can inject a host header pointing to an internal IP address, leading to unauthorized access to internal resources. For example, if the server does not correctly parse the `Host` header and accepts arbitrary values, an attacker can set the `Host` header to an internal IP address hosting an admin panel, thus gaining unauthorized access.

**Q2. How can you confirm that a web application is vulnerable to SSRF through the `Host` header?**

To confirm SSRF vulnerability through the `Host` header, you can use Burp Suite's Collaborator feature. First, capture a request to the web application using Burp Suite's Proxy. Then, modify the `Host` header to point to the Burp Collaborator server's domain. Send the modified request and observe if the server sends a request to the Collaborator server. If the Collaborator server receives a request, it indicates that the web application is vulnerable to SSRF via the `Host` header.

**Q3. Describe how to perform an IP scan to identify an internal admin panel using Burp Suite Intruder.**

To perform an IP scan using Burp Suite Intruder, follow these steps:

1. Capture a request to the web application using Burp Suite's Proxy.
2. Send the captured request to Intruder.
3. Replace the domain in the request with the base IP address of the internal network (e.g., `192.168.0.`).
4. Set the last octet of the IP address as a payload position.
5. Configure the payload type to generate a range of numbers from 1 to 254.
6. Ensure the "Update Host Header to Match Target" option is unchecked.
7. Start the attack and monitor the responses for different status codes or lengths that indicate the presence of an admin panel.

**Q4. How can you exploit a discrepancy between the `Host` header and the request line to access an internal admin panel?**

To exploit a discrepancy between the `Host` header and the request line, follow these steps:

1. Identify a valid request to the web application.
2. Modify the `Host` header to point to an internal IP address hosting the admin panel.
3. Set the request line to include the absolute URL of the admin panel (e.g., `http://192.168.0.243/admin`).
4. Send the modified request and observe the response.
5. If the server processes the request line correctly but uses the `Host` header for validation, you can bypass the validation and access the internal admin panel.

**Q5. Why is it important to ensure that the absolute URL is included in the request line when exploiting SSRF via flawed request parsing?**

Ensuring that the absolute URL is included in the request line is crucial because it helps maintain consistency between the request line and the `Host` header. Some servers may validate the `Host` header independently of the request line. By including the absolute URL in the request line, you can bypass potential validation checks that rely solely on the `Host` header. This approach increases the likelihood of successfully exploiting the SSRF vulnerability and accessing internal resources.

**Q6. Discuss recent real-world examples of SSRF vulnerabilities and how they were exploited.**

One notable example is the SSRF vulnerability in Tesla’s vehicle firmware (CVE-2020-28494). The vulnerability allowed attackers to send malicious requests to internal services within the vehicle’s network. By manipulating the `Host` header, attackers could trigger the vehicle’s firmware update process to download and execute malicious code from an attacker-controlled server. This exploit demonstrates the critical importance of proper input validation and network segmentation to prevent SSRF attacks.

Another example is the SSRF vulnerability in Docker Hub (CVE-2020-15253), where attackers could use the `Host` header to access internal services and steal sensitive data. The vulnerability was exploited by sending crafted requests to Docker Hub, which then forwarded the requests to internal services, allowing attackers to read environment variables and other sensitive information.

These examples highlight the severe consequences of SSRF vulnerabilities and emphasize the need for robust security measures to prevent such exploits.

---
<!-- nav -->
[[06-Understanding HTTP Host Headers|Understanding HTTP Host Headers]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/00-Overview|Overview]]
