---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what web cache poisoning is and how it can be exploited.**

Web cache poisoning is a technique where an attacker exploits the behavior of the application and its corresponding cache to serve harmful HTTP responses to other users of the application. When a user requests a page, the server typically caches the response to reduce load and improve performance. If there are flaws in the cache design or implementation, an attacker can inject a malicious payload into the cache. Subsequent users who request the same page receive the poisoned response, leading to potential security issues such as executing malicious JavaScript in their browsers.

To exploit web cache poisoning, an attacker needs to follow these steps:
1. Identify unkeyed inputs that the cache ignores when deciding whether to serve a cached response.
2. Inject a harmful payload through these unkeyed inputs to elicit a poisoned response from the backend server.
3. Ensure that the poisoned response is cached so that subsequent requests return the malicious content.

**Q2. How would you exploit a web cache poisoning vulnerability using the host header?**

To exploit a web cache poisoning vulnerability using the host header, follow these steps:

1. **Identify the Host Header as an Unkeyed Input**: Determine if the host header is treated as an unkeyed input by the cache. This can be done by sending requests with modified host headers and observing if the cache treats them differently.

2. **Inject Malicious Content**: Craft a request with a modified host header that includes a malicious payload. For example, you might modify the host header to point to a resource controlled by the attacker, such as `http://attacker.com/resources/js/tracking.js`.

3. **Ensure Caching**: Make sure the response containing the malicious host header is cached. This can be verified by checking the cache control headers and ensuring that subsequent requests return the cached response.

4. **Trigger the Exploit**: Once the malicious content is cached, any user who accesses the page will receive the poisoned response, leading to the execution of the malicious JavaScript.

Example payload:
```http
GET / HTTP/1.1
Host: attacker.com
```

**Q3. Why is it important to use a cache buster during testing for web cache poisoning?**

Using a cache buster during testing for web cache poisoning is crucial to prevent unintended consequences. A cache buster is a unique parameter added to the URL to ensure that the request is not served from the cache but is instead fetched directly from the server. This helps in isolating the test environment from the live environment, preventing the exploitation of legitimate users.

For example, adding a random parameter to the URL ensures that the exploit is only tested on a specific, isolated instance:
```http
GET /?cb=123456 HTTP/1.1
Host: vulnerable-site.com
```

This way, if the exploit is successful, it will only affect the specific URL with the cache buster parameter, rather than all users accessing the homepage.

**Q4. What recent real-world examples or CVEs illustrate the impact of web cache poisoning?**

One notable example is the CVE-2019-9193, which affected Akamai's CDN services. This vulnerability allowed attackers to manipulate the host header and inject malicious content into the cache, which was then served to other users. This led to potential security risks, including the execution of arbitrary JavaScript in users' browsers.

Another example is CVE-2020-1938, which affected Cloudflare's CDN services. Attackers could inject malicious content into the cache by manipulating the host header, leading to similar risks as described above.

These examples highlight the importance of securing against web cache poisoning vulnerabilities, as they can have significant impacts on user security and privacy.

**Q5. How would you configure a web server to mitigate web cache poisoning attacks?**

To mitigate web cache poisoning attacks, a web server can be configured in several ways:

1. **Strict Validation of Headers**: Ensure that the server strictly validates all headers, particularly the host header, to prevent injection of malicious content. Use regular expressions or predefined lists to validate acceptable values.

2. **Use Keyed Inputs for Caching**: Configure the cache to use keyed inputs that uniquely identify each request. This ensures that the cache does not serve the same response to different requests.

3. **Implement Cache Busting Mechanisms**: Automatically append unique identifiers to URLs to prevent caching of sensitive requests. This can be done programmatically in the application layer.

4. **Regular Audits and Monitoring**: Regularly audit and monitor the cache to detect any suspicious activity or attempts to inject malicious content. Implement logging and alerting mechanisms to notify administrators of potential threats.

Example configuration for Apache:
```apache
# Validate Host header
RewriteEngine On
RewriteCond %{HTTP_HOST} !^allowed\.domain\.com$ [NC]
RewriteRule .* - [F]

# Use ETag for cache validation
FileETag MTime Size
```

By implementing these configurations, the risk of web cache poisoning can be significantly reduced.

---
<!-- nav -->
[[09-Web Cache Poisoning via Ambiguous Requests|Web Cache Poisoning via Ambiguous Requests]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/00-Overview|Overview]]
