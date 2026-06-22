---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of using the Burp Collaborator server in this lab?**

The Burp Collaborator server is used to detect out-of-band responses from the server when testing for blind SSRF vulnerabilities. Since the server does not provide direct feedback about the SSRF request, the Burp Collaborator server acts as a monitoring tool to confirm whether the SSRF payload was executed and if the server made an outbound HTTP request to the specified domain.

**Q2. Why is the `Referer` header considered a potential vector for SSRF attacks in this lab?**

The `Referer` header is considered a potential vector for SSRF attacks because the analytics software on the server reads the value of this header and makes an HTTP request to the URL specified in the header. By manipulating the `Referer` header, an attacker can trick the server into making HTTP requests to arbitrary URLs, potentially leading to SSRF vulnerabilities.

**Q3. How would you exploit a blind SSRF vulnerability using the Burp Collaborator server?**

To exploit a blind SSRF vulnerability using the Burp Collaborator server, follow these steps:

1. Identify the parameter or header that is susceptible to SSRF, such as the `Referer` header in this lab.
2. Set up a Burp Collaborator server instance and obtain its unique domain name.
3. Craft a request that includes the Burp Collaborator domain in the vulnerable parameter or header.
4. Send the crafted request to the server.
5. Monitor the Burp Collaborator server to see if the server made an HTTP request to the specified domain.

For example, if the `Referer` header is vulnerable, you would set the `Referer` header to the Burp Collaborator domain and send the request:

```http
GET /product HTTP/1.1
Host: vulnerable-app.com
Referer: http://your-burp-collaborator-domain
```

Then, check the Burp Collaborator server to confirm if the server made an HTTP request to the specified domain.

**Q4. What is the significance of the "out-of-band" aspect in blind SSRF attacks?**

The "out-of-band" aspect in blind SSRF attacks is significant because it allows attackers to detect SSRF vulnerabilities even when the server does not directly return information about the SSRF request. Instead of receiving a direct response, the attacker uses an external service (like the Burp Collaborator server) to monitor for unexpected HTTP requests from the server. This method is crucial for detecting SSRF vulnerabilities in scenarios where the server does not provide any feedback about the SSRF request.

**Q5. How can a blind SSRF vulnerability be used to exploit further vulnerabilities on the network, such as Shellshock?**

A blind SSRF vulnerability can be used to exploit further vulnerabilities on the network by leveraging the SSRF to interact with internal services that are not directly accessible from the internet. For example, if an internal server is vulnerable to the Shellshock vulnerability, an attacker can use the SSRF to craft a request that triggers the Shellshock vulnerability on the internal server.

Here’s a simplified example:

1. Identify an internal server IP address or hostname that is vulnerable to Shellshock.
2. Use the SSRF vulnerability to craft a request that sends a malicious payload to the internal server.
3. The internal server processes the request and executes the payload due to the Shellshock vulnerability.

For instance, if the internal server is at `http://internal-server:8080`, and it is vulnerable to Shellshock, the attacker might use the SSRF to send a request like:

```http
GET /cgi-bin/test.cgi HTTP/1.1
Host: internal-server:8080
User-Agent: () { :; }; echo; /bin/bash -c 'whoami'
```

This payload would trigger the Shellshock vulnerability on the internal server, potentially allowing the attacker to execute commands on the server.

**Q6. Why is the use of Burp Collaborator limited to the professional version of Burp Suite?**

The use of Burp Collaborator is limited to the professional version of Burp Suite because it provides advanced features and capabilities that are not included in the community edition. These features include the ability to monitor and detect out-of-band responses, which are essential for testing blind SSRF vulnerabilities. The professional version ensures that users have access to comprehensive tools for security testing, including the Burp Collaborator server, which is necessary for performing certain types of security assessments.

**Q7. What recent real-world examples demonstrate the impact of blind SSRF vulnerabilities?**

One notable example is the exploitation of blind SSRF vulnerabilities in cloud environments, such as AWS S3 buckets or Azure Blob Storage. In 2020, researchers discovered that misconfigured cloud storage buckets could be exploited through blind SSRF vulnerabilities to gain unauthorized access to sensitive data.

Another example is the exploitation of blind SSRF vulnerabilities in web applications to access internal services or to perform further attacks. For instance, CVE-2021-3594 describes a blind SSRF vulnerability in the Jenkins CI/CD platform that allowed attackers to bypass authentication and execute arbitrary code on the server.

These examples highlight the importance of properly securing web applications against SSRF vulnerabilities, as they can lead to severe consequences if exploited.

---
<!-- nav -->
[[10-Understanding the Vulnerability|Understanding the Vulnerability]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]]
