---
course: API Security
topic: Lack of Resource & Rate Limiting
tags: [api-security]
---

## Lack of Resource & Rate Limiting

### Introduction

Resource and rate limiting are critical components of API security. These mechanisms ensure that an API does not get overwhelmed by excessive requests, which can lead to denial-of-service (DoS) attacks or resource exhaustion. In the context of the demonstration provided, we will explore how the lack of proper rate limiting can expose an API to abuse, leading to potential security vulnerabilities.

### Background Theory

#### Resource Limiting

Resource limiting refers to the practice of restricting the amount of resources (such as memory, CPU, or bandwidth) that an API can consume. This is important because an uncontrolled API can exhaust server resources, leading to performance degradation or even service unavailability.

#### Rate Limiting

Rate limiting, on the other hand, restricts the number of requests that can be made to an API within a given time frame. This helps prevent abuse such as spamming, brute-force attacks, and automated scraping. Rate limiting can be implemented at different levels:

- **Per-user**: Limits the number of requests per user.
- **Global**: Limits the total number of requests across all users.
- **IP-based**: Limits the number of requests from a specific IP address.

### Demonstration Analysis

In the provided demonstration, the lecturer attempts to send verification emails through an API. The key points to note are:

1. **Sending Verification Emails**: The lecturer sends verification emails to themselves and then tries to send them to another user.
2. **Rate Limiting Check**: The lecturer uses tools like Burp Suite to capture and replay the request to check if there is any rate limiting in place.

Let's break down the steps and analyze the implications:

#### Step-by-Step Mechanics

1. **Initial Request**:
    - The lecturer sends a verification email to their own email address.
    - The request is successful, indicating that the API allows this action.

2. **Unauthorized Request**:
    - The lecturer attempts to send a verification email to another user (`cali.hap007@example.com`).
    - The request fails due to authorization restrictions, confirming that the API enforces user-specific permissions.

3. **Rate Limiting Test**:
    - The lecturer captures the initial request using Burp Suite.
    - They then use Burp Suite's Intruder tool to send the same request repeatedly.
    - The lecturer sends 100 requests in quick succession to test if there is any rate limiting in place.

#### Raw HTTP Request and Response

Here is an example of the HTTP request and response for sending a verification email:

```http
POST /api/send-email HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "email": "lecturer@example.com",
  "message": "Verification email"
}
```

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 34

{
  "status": "success",
  "message": "Email sent successfully"
}
```

### Implications of Lack of Rate Limiting

The demonstration reveals that the API does not enforce any rate limiting. This means that an attacker could potentially flood the API with requests, leading to several security issues:

1. **Denial of Service (DoS)**: An attacker could overwhelm the API with requests, causing legitimate users to experience slow response times or service unavailability.
2. **Resource Exhaustion**: Excessive requests can exhaust server resources, leading to performance degradation or crashes.
3. **Brute-Force Attacks**: Without rate limiting, an attacker could attempt to brute-force authentication mechanisms by making numerous login attempts in a short period.

### Real-World Examples

Several real-world examples highlight the importance of rate limiting:

- **CVE-2021-22205**: A vulnerability in the WordPress REST API allowed attackers to perform brute-force attacks due to the lack of rate limiting.
- **GitHub Incident (2020)**: GitHub experienced a large-scale DDoS attack where attackers exploited the lack of rate limiting to flood the API with requests.

### How to Prevent / Defend

#### Detection

To detect rate-limiting bypasses, you can monitor API usage patterns and look for unusual spikes in request volumes. Tools like ELK Stack (Elasticsearch, Logstash, Kibana) can help in analyzing logs and identifying anomalies.

#### Prevention

Implementing rate limiting is crucial to prevent abuse. Here are some strategies:

1. **Per-User Rate Limiting**: Limit the number of requests per user within a specified time frame.
2. **IP-Based Rate Limiting**: Limit the number of requests from a specific IP address.
3. **Global Rate Limiting**: Set a global limit on the total number of requests across all users.

#### Secure Coding Fixes

Here is an example of how to implement rate limiting in a Node.js application using Express and Redis:

```javascript
const express = require('express');
const redis = require('redis');

const app = express();
const client = redis.createClient();

app.use(express.json());

// Middleware for rate limiting
function rateLimit(req, res, next) {
  const ip = req.ip;
  client.get(ip, (err, reply) => {
    if (reply && parseInt(reply) >= 100) {
      return res.status(429).send('Too many requests');
    }
    client.incr(ip);
    client.expire(ip, 60); // Reset after 60 seconds
    next();
  });
}

app.post('/api/send-email', rateLimit, (req, res) => {
  // Logic to send email
  res.send({ status: 'success', message: 'Email sent successfully' });
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

#### Configuration Hardening

Ensure that your API gateway or load balancer is configured to enforce rate limiting. For example, in Nginx, you can configure rate limiting using the `limit_req` module:

```nginx
http {
  limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;

  server {
    listen 80;
    location /api/send-email {
      limit_req zone=one burst=5 nodelay;
      proxy_pass http://backend;
    }
  }
}
```

### Common Pitfalls

1. **Overly Permissive Limits**: Setting limits too high can still allow abuse. Ensure that limits are set appropriately based on normal usage patterns.
2. **Ignoring Global Limits**: Focusing only on per-user or IP-based limits can still leave the system vulnerable to distributed attacks.
3. **No Graceful Degradation**: Implementing rate limiting should not cause legitimate users to experience poor service. Ensure that the system gracefully degrades during high traffic periods.

### Conclusion

Proper implementation of resource and rate limiting is essential for securing APIs against abuse and DoS attacks. By enforcing these controls, you can protect your system from malicious actors and ensure smooth operation for legitimate users.

### Practice Labs

For hands-on practice with API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various aspects of web security, including API security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning about web security vulnerabilities.

These labs provide practical scenarios to apply the concepts learned in this chapter.

---
<!-- nav -->
[[API Security/09-Lack of Resource & Rate Limiting/02-Demonstration 1/01-Lack of Resource & Rate Limiting in API Security|Lack of Resource & Rate Limiting in API Security]] | [[API Security/09-Lack of Resource & Rate Limiting/02-Demonstration 1/00-Overview|Overview]] | [[API Security/09-Lack of Resource & Rate Limiting/02-Demonstration 1/03-Practice Questions & Answers|Practice Questions & Answers]]
