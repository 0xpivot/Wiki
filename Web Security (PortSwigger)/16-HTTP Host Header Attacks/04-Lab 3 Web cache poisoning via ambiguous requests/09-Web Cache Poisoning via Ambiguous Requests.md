---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Web Cache Poisoning via Ambiguous Requests

Web cache poisoning is a type of attack where an attacker manipulates the content stored in a web cache. This can lead to malicious content being served to unsuspecting users. One way this can happen is through ambiguous requests that are handled differently by the cache and the backend application.

### What is Web Cache Poisoning?

Web cache poisoning occurs when an attacker tricks a caching proxy into storing and serving malicious content. This can happen if the caching mechanism does not correctly handle certain types of requests, such as those with ambiguous `Host` headers.

### How Does Web Cache Poisoning Work?

Consider the following scenario:

1. A user visits a website (`www.example.com`).
2. The website uses a caching proxy to improve performance.
3. An attacker sends a request to the caching proxy with a modified `Host` header (`attacker.com`).
4. The caching proxy stores the response from `attacker.com` as if it were from `www.example.com`.
5. When the user next visits `www.example.com`, the cached (malicious) content is served instead of the legitimate content.

### Real-World Example: CVE-2019-9164

CVE-2019-9164 is a vulnerability in the Varnish caching proxy that allows attackers to perform web cache poisoning. By manipulating the `Host` header, an attacker could cause Varnish to store and serve malicious content.

### How to Prevent / Defend Against Web Cache Poisoning

#### Detection

Monitor your caching proxy logs for unusual or unexpected `Host` headers. Tools like `varnishlog` can help you analyze Varnish logs.

#### Prevention

1. **Strict Validation of `Host` Headers**: Ensure that the `Host` header is validated against a list of allowed domains.
2. **Cache Key Configuration**: Configure your caching proxy to use a unique cache key that includes the `Host` header.
3. **Regular Audits**: Regularly audit your caching proxy configurations to ensure they are secure.

### Secure Coding Practices

Here’s an example of how to configure Varnish to use a unique cache key that includes the `Host` header:

```nginx
sub vcl_hash {
    hash_data(req.url);
    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }
}
```

In this example, the `vcl_hash` subroutine ensures that the cache key includes the `Host` header, making it less likely that an attacker can trick the cache into storing malicious content.

---
<!-- nav -->
[[08-Understanding Web Cache Poisoning|Understanding Web Cache Poisoning]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/10-Practice Questions & Answers|Practice Questions & Answers]]
