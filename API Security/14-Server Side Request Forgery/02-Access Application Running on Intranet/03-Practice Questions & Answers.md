---
course: API Security
topic: Server Side Request Forgery
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of identifying injection points when attempting to access applications running on an intranet?**

The purpose of identifying injection points is to find places within an application where an attacker can inject malicious input. This input can then be used to manipulate the application's behavior, potentially allowing unauthorized access to internal resources or sensitive data. Injection points can include form fields, URL parameters, and API endpoints where user input is accepted and processed by the application.

**Q2. How can you use HTTP requests to determine if a specific port on a local host is accessible?**

To determine if a specific port on a local host is accessible using HTTP requests, you can send a request to that port and observe the response. For example, you can use `curl` or a web browser to send a request to `http://127.0.0.1:<port>`. If the port is open and running a service that responds to HTTP requests, you should receive a response such as a status code 200 OK. If the port is closed or not running a service that listens to HTTP, you may receive no response or a connection refused error.

```bash
# Example command to check port 80
curl http://127.0.0.1:80
```

If the response is successful, it indicates that the port is accessible and likely running an HTTP service.

**Q3. Explain how an attacker might use file protocols to access internal files on a server.**

An attacker can use file protocols to access internal files on a server by exploiting vulnerabilities in the application that allow for directory traversal or file inclusion attacks. By injecting file paths into input fields or URLs, an attacker can attempt to read files from the server's filesystem. For example, using a file protocol like `file:///etc/passwd` can be used to read the `/etc/passwd` file on a Unix-based system.

```bash
# Example of accessing /etc/passwd using file protocol
file:///etc/passwd
```

This method can be particularly dangerous if the application does not properly sanitize or validate input, allowing an attacker to read sensitive configuration files, source code, or other critical information.

**Q4. How can an attacker leverage AWS instance metadata to gain unauthorized access to internal applications?**

An attacker can leverage AWS instance metadata to gain unauthorized access to internal applications by exploiting misconfigured security settings or vulnerabilities in the application. AWS instances provide metadata endpoints that can be accessed via HTTP requests to retrieve information about the instance, including security credentials. If an application running on an AWS instance improperly handles these metadata requests, an attacker might be able to extract sensitive information such as access keys or IAM roles.

For example, an attacker can send a request to the metadata endpoint:

```bash
# Example of accessing AWS metadata endpoint
curl http://169.254.169.254/latest/meta-data/
```

If the application allows unauthorized access to this endpoint, the attacker might be able to retrieve sensitive information that can be used to escalate privileges or access other internal resources.

**Q5. What recent real-world examples demonstrate the risks of improper handling of internal application access?**

One notable example is the Capital One data breach in 2019 (CVE-2019-11510). The breach occurred due to a misconfigured firewall rule that allowed unauthorized access to internal systems. An attacker exploited this misconfiguration to access sensitive customer data stored in AWS S3 buckets. This incident highlights the importance of proper configuration management and the need to restrict access to internal resources.

Another example is the Equifax data breach in 2017, where a vulnerability in the Apache Struts framework was exploited to gain unauthorized access to internal systems. This breach resulted in the exposure of personal data for millions of customers. These incidents underscore the critical nature of securing internal applications and ensuring that proper security measures are in place to prevent unauthorized access.

---
<!-- nav -->
[[API Security/14-Server Side Request Forgery/02-Access Application Running on Intranet/02-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]] | [[API Security/14-Server Side Request Forgery/02-Access Application Running on Intranet/00-Overview|Overview]]
