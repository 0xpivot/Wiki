---
course: DevSecOps
topic: Improving Your Incident Response Capability
tags: [devsecops]
---

## Identifying Root Causes and Fixing Issues

One of the key advantages of shifting left is the ability to identify the root causes of security incidents and fix them permanently. By understanding the underlying issues, teams can implement long-term solutions that prevent the same problems from recurring.

### Example: Root Cause Analysis

Consider a scenario where a security incident occurs due to a misconfigured server. To identify the root cause, the team might perform the following steps:

1. **Collect Logs**: Gather logs from the affected server to understand the sequence of events leading up to the incident.
2. **Analyze Configuration**: Review the server's configuration files to identify any misconfigurations.
3. **Reproduce Issue**: Attempt to reproduce the issue in a controlled environment to confirm the root cause.
4. **Implement Fix**: Apply the necessary fixes to the server's configuration and validate that the issue is resolved.

#### Example: Correcting Misconfiguration

```yaml
# Before
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
    }
}

# After
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
        deny all;
    }
}
```

In this example, the server's configuration is corrected to deny all access to the `/` location, preventing unauthorized access.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/Shifting Left/04-Hands-On Labs|Hands-On Labs]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/Shifting Left/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/Shifting Left/06-Incorporating Security in DevOps Pipeline|Incorporating Security in DevOps Pipeline]]
