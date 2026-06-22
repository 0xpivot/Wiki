---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Information Disclosure Vulnerabilities

Information disclosure vulnerabilities occur when sensitive information is inadvertently exposed to unauthorized users. This can happen through various means, such as stack traces, verbose headers, and cryptographic failures. Understanding these vulnerabilities is crucial for both attackers and defenders, as they can significantly impact the security posture of an application.

### Stack Traces and Backend Technology Enumeration

One of the most common forms of information disclosure is through stack traces. When an application encounters an error, it often generates a stack trace that provides detailed information about the internal workings of the application. This information can include the version numbers of libraries, frameworks, and other dependencies used by the application.

#### Example: Stack Trace Exposure

Consider the following scenario where an application exposes a stack trace:

```plaintext
HTTP/1.1 500 Internal Server Error
Content-Type: text/html; charset=utf-8
Content-Length: 1024

<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>
<body>
    <h1>Internal Server Error</h1>
    <pre>
        at com.example.app.handler.handleRequest(Request.java:45)
        at com.example.app.servlet.HttpServlet.service(HttpServlet.java:729)
        at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:303)
        at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
        at org.apache.catalina.core.StandardWrapperValve.invoke(StandardWrapperValve.java:219)
        at org.apache.catalina.core.StandardContextValve.invoke(StandardContextValve.java:106)
        at org.apache.catalina.authenticator.AuthenticatorBase.invoke(AuthenticatorBase.java:502)
        at org.apache.catalina.core.StandardHostValve.invoke(StandardHostValve.java:142)
        at org.apache.catalina.valves.ErrorReportValve.invoke(ErrorReportValve.java:79)
        at org.apache.catalina.valves.AbstractAccessLogValve.invoke(AbstractAccessLogValve.java:617)
        at org.apache.catalina.core.StandardEngineValve.invoke(StandardEngineValve.java:88)
        at org.apache.catalina.connector.CoyoteAdapter.service(CoyoteAdapter.java:518)
        at org.apache.coyote.http11.AbstractHttp11Processor.process(AbstractHttp11Processor.java:1091)
        at org.apache.coyote.AbstractProtocol$AbstractConnectionHandler.process(AbstractProtocol.java:668)
        at org.apache.tomcat.util.net.NioEndpoint$SocketProcessor.doRun(NioEndpoint.java:1521)
        at org.apache.tomcat.util.net.NioEndpoint$SocketProcessor.run(NioEndpoint.java:1478)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at org.apache.tomcat.util.threads.TaskThread$WrappingRunnable.run(TaskThread.java:61)
        at java.lang.Thread.run(Thread.java:748)
    </pre>
</body>
</html>
```

In this example, the stack trace reveals that the application is using Apache Tomcat as the web server and Java as the programming language. Additionally, it shows the version numbers of various libraries and frameworks used by the application.

#### Why Stack Traces Matter

Stack traces provide attackers with valuable information about the backend technologies used by the application. This information can be used to tailor attacks to exploit known vulnerabilities in specific versions of these technologies. For instance, if an attacker knows that the application is using a specific version of a library that is known to have a vulnerability, they can craft an exploit specifically targeting that version.

#### How to Prevent / Defend Against Stack Trace Exposure

To prevent stack trace exposure, developers should ensure that error handling is properly configured to avoid revealing sensitive information. Here are some steps to take:

1. **Custom Error Pages**: Implement custom error pages that do not expose stack traces.
2. **Error Logging**: Log errors internally but do not expose them to the user.
3. **Configuration Settings**: Configure the application server to disable stack trace exposure in error responses.

Here is an example of a secure configuration in a Spring Boot application:

```yaml
# application.yml
server.error.include-stacktrace=never
```

This configuration ensures that stack traces are never included in error responses.

### Verbose Headers and Backend Technology Enumeration

Another common form of information disclosure is through verbose headers in HTTP responses. These headers can reveal details about the backend technologies used by the application, such as the web server and framework.

#### Example: Verbose Headers

Consider the following HTTP response:

```http
HTTP/1.1 200 OK
Date: Tue, 20 Mar 2023 12:00:00 GMT
Server: Microsoft-IIS/10.0
X-Powered-By: ASP.NET
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Welcome</title>
</head>
<body>
    <h1>Welcome to Our Website</h1>
</body>
</html>
```

In this example, the `Server` header reveals that the web server is Microsoft IIS version 10.0, and the `X-Powered-By` header indicates that the application is using ASP.NET version 4.0.30319.

#### Why Verbose Headers Matter

Verbose headers provide attackers with information about the backend technologies used by the application. This information can be used to tailor attacks to exploit known vulnerabilities in specific versions of these technologies. For instance, if an attacker knows that the application is using a specific version of a web server that is known to have a vulnerability, they can craft an exploit specifically targeting that version.

#### How to Prevent / Defend Against Verbose Header Exposure

To prevent verbose header exposure, developers should configure the application server to remove or modify these headers. Here are some steps to take:

1. **Remove Unnecessary Headers**: Remove headers that are not necessary for the operation of the application.
2. **Modify Headers**: Modify headers to remove version numbers or other sensitive information.
3. **Use Security Headers**: Add security headers that can help mitigate information disclosure.

Here is an example of a secure configuration in an Nginx server:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_hide_header Server;
        proxy_hide_header X-Powered-By;
    }
}
```

This configuration removes the `Server` and `X-Powered-By` headers from the response.

### Cryptographic Failures Leading to Information Disclosure

Cryptographic failures can also lead to information disclosure. One common example is the use of an unencrypted channel to transmit information. This can allow attackers to intercept and read the transmitted data.

#### Example: Unencrypted Channel

Consider the following scenario where an application uses HTTP instead of HTTPS to transmit data:

```http
GET /api/user HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
Date: Tue, 20 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 123

{
    "username": "john_doe",
    "email": "john@example.com"
}
```

In this example, the data is transmitted over an unencrypted HTTP connection, allowing anyone on the same network to intercept and read the data.

#### Why Cryptographic Failures Matter

Cryptographic failures can allow attackers to intercept and read sensitive information transmitted over the network. This can include login credentials, personal information, and other sensitive data. For instance, if an attacker intercepts login credentials, they can use them to gain unauthorized access to the application.

#### How to Prevent / Defend Against Cryptographic Failures

To prevent cryptographic failures, developers should ensure that all data is transmitted over encrypted channels. Here are some steps to take:

1. **Use HTTPS**: Ensure that all data is transmitted over HTTPS.
2. **HSTS**: Enable HTTP Strict Transport Security (HSTS) to force browsers to use HTTPS.
3. **TLS Configuration**: Configure TLS settings to use strong ciphers and protocols.

Here is an example of a secure configuration in an Apache server:

```apache
<VirtualHost *:443>
    ServerName example.com
    DocumentRoot /var/www/example.com

    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/example.com.crt
    SSLCertificateKeyFile /etc/ssl/private/example.com.key
    SSLCACertificateFile /etc/ssl/certs/ca-bundle.crt

    <Directory /var/www/example.com>
        Require all granted
    </Directory>

    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</VirtualHost>
```

This configuration enables HTTPS and sets HSTS to enforce the use of HTTPS.

### Real-World Examples and Recent Breaches

Several recent breaches have been attributed to information disclosure vulnerabilities. For instance, the Equifax breach in 2017 was partly due to an information disclosure vulnerability in their web application. The vulnerability allowed attackers to obtain sensitive information about millions of users, including Social Security numbers and birth dates.

Another example is the Capital One breach in 2019, which was caused by a misconfigured web application firewall. The misconfiguration allowed attackers to access sensitive customer data, including Social Security numbers and bank account information.

### Conclusion

Information disclosure vulnerabilities can have severe consequences for the security of an application. By understanding the different forms of information disclosure and how to prevent them, developers can significantly improve the security posture of their applications. Always ensure that sensitive information is not inadvertently exposed to unauthorized users, and use encryption to protect data in transit.

### Practice Labs

For hands-on practice with information disclosure vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including information disclosure.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training and research.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in identifying and mitigating information disclosure vulnerabilities.

---
<!-- nav -->
[[16-Improper Verification of Cryptographic Signatures|Improper Verification of Cryptographic Signatures]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[18-Information Disclosure in Web Applications|Information Disclosure in Web Applications]]
