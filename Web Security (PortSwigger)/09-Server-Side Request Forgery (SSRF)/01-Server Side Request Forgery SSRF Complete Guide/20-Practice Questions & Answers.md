---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what an SSRF vulnerability is and provide an example of how it can be exploited.**

An SSRF (Server-Side Request Forgery) vulnerability occurs when an application fetches a remote resource without first validating the user-supplied input. This allows an attacker to coerce the server into making network connections on behalf of the attacker, potentially targeting systems that are behind firewalls.

Example: Consider a shopping application where a user can check if an item is in stock by clicking a button. This action triggers a request to an internal service (e.g., `stock.shop.net`). If the URL for this request is user-controllable and not properly validated, an attacker could modify the URL to point to an admin page (`localhost/admin`) or another sensitive internal service. If the application trusts this internal service, the admin page content would be returned to the attacker, allowing unauthorized access to sensitive functionalities.

**Q2. Describe the different types of SSRF vulnerabilities and provide an example for each.**

There are two main types of SSRF vulnerabilities:

1. **Regular or In-Band SSRF**: The response to the forged request is directly visible to the attacker. For example, if an attacker modifies a URL to point to `localhost/admin`, the content of the admin page is returned to the attacker.

2. **Blind or Out-of-Band SSRF**: The response to the forged request is not visible to the attacker. To detect this, the attacker may modify the URL to point to a server they control (e.g., a Burp Collaborator). If the attacker’s server receives a request, it indicates that the application is vulnerable to SSRF.

**Q3. How can you test for SSRF vulnerabilities from a black box perspective?**

To test for SSRF vulnerabilities from a black box perspective, follow these steps:

1. **Map the Application**: Visit the URL of the application and walk through all accessible pages, noting all input vectors that could talk to the backend.
2. **Identify Input Vectors**: Filter input vectors that contain hostnames, IP addresses, or full URLs.
3. **Fuzz the Application**: Modify the values of these input vectors to specify alternative resources and observe the application’s response.
4. **Test for Blind SSRF**: Modify the input vector to point to a server you control (e.g., Burp Collaborator) and monitor the server for incoming requests.

**Q4. How can you exploit an SSRF vulnerability to port scan an internal network?**

To exploit an SSRF vulnerability to port scan an internal network:

1. Identify an input vector that can be modified to point to internal IP addresses.
2. Use a tool like Burp Intruder to automate the process of sending requests to various IP addresses and ports within the internal network.
3. Monitor the responses to determine which services are running on which internal IP addresses and ports.

For example, if the application is vulnerable and allows requests to internal IPs, you can send requests to `http://10.0.0.1:80`, `http://10.0.0.1:443`, etc., and observe which requests succeed.

**Q5. Discuss recent real-world examples of SSRF vulnerabilities and their impacts.**

One notable example is the Capital One breach in 2019. An attacker exploited an SSRF vulnerability in a cloud instance to obtain metadata, which included credentials for an IAM role with excessive privileges. These credentials allowed the attacker to list and access S3 buckets, leading to the exposure of sensitive customer data.

This incident highlights the importance of proper validation of user inputs and the need for robust security measures to prevent SSRF vulnerabilities from being exploited.

**Q6. What are some defense strategies to prevent SSRF vulnerabilities?**

To prevent SSRF vulnerabilities, implement the following defense strategies:

1. **Sanitize and Validate Input**: Ensure all client-supplied input is sanitized and validated.
2. **Use Whitelists**: Enforce the URL schema, port, and destination with a positive allow list.
3. **Custom Responses**: Avoid sending raw responses to clients; instead, return custom responses with expected data.
4. **Disable HTTP Redirections**: Prevent HTTP redirections to avoid bypass attacks.
5. **Segment Networks**: Segment remote resource access functionality into separate networks to reduce the impact of SSRF.
6. **Firewall Policies**: Implement denied-by-default firewall policies to block unnecessary internal traffic.

By combining these strategies, you can significantly reduce the risk of SSRF vulnerabilities and their potential impacts.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/19-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]]
