---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how routing-based SSRF works in the context of the host header injection vulnerability.**

Routing-based SSRF exploits the reliance of backend servers on the host header to route traffic correctly. When a server implicitly trusts the host header without proper validation, an attacker can manipulate this header to direct requests to internal servers or other unintended locations. For instance, if a server uses the host header to resolve domain names to internal IP addresses, an attacker can inject malicious values into the host header to access internal resources that are otherwise protected by firewalls.

**Q2. How would you exploit a routing-based SSRF vulnerability to access an internal admin panel?**

To exploit a routing-based SSRF vulnerability, follow these steps:

1. Identify the vulnerable parameter, typically the `Host` header.
2. Use a tool like Burp Suite to intercept and modify the `Host` header.
3. Replace the original value with the internal IP address of the admin panel.
4. Send the modified request to the server. If the server trusts the `Host` header, it will forward the request to the specified internal IP address.
5. Access the admin panel and perform desired actions, such as deleting a user.

For example, if the internal admin panel is located at `192.168.0.1/admin`, set the `Host` header to `192.168.0.1` and send the request to the server.

**Q3. Why does the lab block interactions with arbitrary external systems, and how does this relate to SSRF vulnerabilities?**

The lab blocks interactions with arbitrary external systems to prevent attackers from using the SSRF vulnerability to perform unauthorized requests to third-party servers. This is a common security measure to mitigate the risk of SSRF attacks being used to exfiltrate data or launch further attacks on external systems. By restricting access to only internal networks, the lab ensures that any SSRF exploitation remains within the controlled environment, preventing potential misuse.

**Q4. How can you confirm that a web application is vulnerable to SSRF using Burp Suite's Collaborator feature?**

To confirm SSRF vulnerability using Burp Suite's Collaborator feature:

1. Obtain a Collaborator server URL from Burp Suite.
2. Modify the `Host` header in Burp Repeater to include the Collaborator URL.
3. Send the request to the server.
4. Check the Collaborator server for incoming connections. If the server responds and the Collaborator server receives a pingback, it confirms that the application is vulnerable to SSRF.

For example, if the Collaborator URL is `http://abc.collaborator.server`, set the `Host` header to `abc.collaborator.server` and observe the Collaborator server for pings.

**Q5. What recent real-world examples or CVEs demonstrate the impact of SSRF vulnerabilities?**

One notable example is CVE-2021-21972, which affected Kubernetes. This vulnerability allowed attackers to perform SSRF attacks by manipulating the `Host` header in HTTP requests to the Kubernetes API server. An attacker could exploit this to access internal services, steal secrets, or execute commands on the cluster nodes. This demonstrates the critical importance of validating and sanitizing input, especially headers like `Host`, to prevent SSRF attacks.

Another example is CVE-2020-5902, affecting the Jenkins Continuous Integration server. This vulnerability allowed attackers to perform SSRF attacks by manipulating the `Jenkins-Crumb` header, leading to unauthorized access to internal resources and potential data exfiltration. These cases highlight the severe consequences of SSRF vulnerabilities and the need for robust security measures.

---
<!-- nav -->
[[06-Understanding the HTTP Host Header|Understanding the HTTP Host Header]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/05-Lab 4 Routing based SSRF/00-Overview|Overview]]
