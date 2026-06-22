---
course: Web Security
topic: Cross-origin Resource Sharing (CORS)
tags: [web-security]
---

## Preventing and Mitigating CORS Attacks

To prevent and mitigate CORS attacks, you need to implement proper security measures and configurations.

### Secure Coding Practices

1. **Validate Allowed Origins**: Ensure that the allowed origins are correctly specified and validated.
2. **Avoid Wildcard Origins**: Avoid using wildcard origins (`*`) unless absolutely necessary.
3. **Use HTTPS**: Always use HTTPS to encrypt data in transit.

### Example: Secure CORS Configuration

Here’s an example of a secure CORS configuration in an `nginx.conf` file:

```nginx
server {
    listen 80;
    server_name example.com;

    location /api/ {
        if ($http_origin ~* (https://trusted-origin.com)) {
            add_header 'Access-Control-Allow-Origin' '$http_origin';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
        }

        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '$http_origin';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }

        # Serve actual requests
        proxy_pass http://backend;
    }
}
```

In this example, the server only allows requests from trusted origins and handles preflight requests appropriately.

### Detection and Prevention

1. **Regular Audits**: Regularly audit your application’s CORS configurations to ensure they are secure.
2. **Automated Scanning**: Use automated scanning tools to detect potential CORS vulnerabilities.
3. **Security Training**: Train developers on secure coding practices related to CORS.

### Real-World Example: Secure Configuration

Consider a real-world example where a company had a CORS misconfiguration that was exploited. After the breach, they implemented a secure configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    location /api/ {
        if ($http_origin ~* (https://trusted-origin.com|https://another-trusted-origin.com)) {
            add_header 'Access-Control-Allow-Origin' '$http_origin';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
        }

        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '$http_origin';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }

        proxy_pass http://backend;
    }
}
```

In this example, the company ensured that only trusted origins could make requests and handled preflight requests securely.

---
<!-- nav -->
[[11-Pre-flight Requests|Pre-flight Requests]] | [[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/00-Overview|Overview]] | [[13-Same Origin Policy (SOP)|Same Origin Policy (SOP)]]
