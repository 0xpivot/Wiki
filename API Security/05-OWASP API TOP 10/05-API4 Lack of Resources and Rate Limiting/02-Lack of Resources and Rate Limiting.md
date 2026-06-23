---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Lack of Resources and Rate Limiting

### Introduction

In the realm of API security, one of the most critical vulnerabilities is the lack of proper resource and rate limiting mechanisms. This issue arises when an API does not adequately protect itself against an excessive number of calls or large payload sizes. Attackers can exploit these weaknesses to perform various malicious activities, such as brute-force attacks, denial-of-service (DoS) attacks, and unauthorized access.

### What is Resource and Rate Limiting?

Resource and rate limiting are techniques used to control the number of requests an API can handle within a specified time frame. These mechanisms ensure that the API remains responsive and available even under heavy load conditions. By setting limits on the number of requests per user or IP address, the API can prevent abuse and maintain performance.

#### Why is Resource and Rate Limiting Important?

Without proper resource and rate limiting, an API can become overwhelmed by a high volume of requests, leading to several issues:

1. **Performance Degradation**: Excessive requests can cause the API to slow down or become unresponsive, affecting legitimate users.
2. **Denial of Service (DoS)**: Attackers can flood the API with requests, making it unavailable to other users.
3. **Brute-Force Attacks**: Without rate limiting, attackers can attempt to guess passwords or authentication tokens through repeated login attempts.
4. **Unauthorized Access**: Large payload sizes can be used to bypass input validation checks, potentially leading to data exfiltration or injection attacks.

### How Does Resource and Rate Limiting Work?

Resource and rate limiting typically involve the following components:

1. **Rate Limiting**: This mechanism restricts the number of requests a client can make within a given time period. Commonly, rate limits are expressed in terms of requests per second (RPS) or requests per minute (RPM).

2. **Resource Limiting**: This mechanism restricts the amount of resources (such as memory, CPU, or storage) that an API can consume. This helps prevent resource exhaustion attacks.

#### Implementation Techniques

There are several ways to implement resource and rate limiting:

1. **Client-Side Rate Limiting**: This approach involves sending rate limit information to the client, which then enforces the limits. However, this method is less secure as clients can bypass the limits.

2. **Server-Side Rate Limiting**: This approach involves enforcing rate limits on the server side. This is more secure but requires additional server-side logic.

3. **Third-Party Services**: Using third-party services like Cloudflare or AWS WAF can help manage rate limiting and resource limits.

### Real-World Examples

#### Example 1: Brute-Force Attack on WordPress

In 2017, a widespread brute-force attack targeted WordPress installations. Attackers exploited the lack of rate limiting on the login endpoint to guess passwords through repeated login attempts. This led to numerous compromised accounts and data breaches.

**HTTP Request Example:**

```http
POST /wp-login.php HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 31

log=admin&pwd=guessme123
```

**HTTP Response Example:**

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>WordPress Login</title>
</head>
<body>
    <!-- HTML content -->
</body>
</html>
```

#### Example 2: Denial of Service Attack on GitHub

In 2018, GitHub experienced a massive DDoS attack that involved sending a large number of requests to their API endpoints. The attackers exploited the lack of rate limiting to overwhelm the service, causing it to become temporarily unavailable.

**HTTP Request Example:**

```http
GET /api/v3/repos/github/linguist HTTP/1.1
Host: api.github.com
User-Agent: curl/7.54.0
Accept: */*
Authorization: token abcdefghijklmnopqrstuvwxyz
```

**HTTP Response Example:**

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 1234
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999

{
  "id": 1,
  "name": "linguist",
  "full_name": "github/linguist",
  "private": false,
  "owner": {
    "login": "github",
    "id": 9919
  },
  "html_url": "https://github.com/github/linguist",
  "description": "GitHub Linguist is a Ruby library that guesses the language of a project by examining the files it contains.",
  "fork": false,
  "url": "https://api.github.com/repos/github/linguist",
  "created_at": "2011-09-06T19:19:08Z",
  "updated_at": "2023-11-20T12:00:00Z"
}
```

### How to Prevent / Defend Against Lack of Resources and Rate Limiting

#### Detection

To detect potential rate-limiting issues, you can monitor your API logs for unusual patterns of requests. Look for:

- A sudden increase in the number of requests from a single IP address.
- Repeated failed login attempts.
- Large payloads being sent to the API.

#### Prevention

To prevent these issues, implement the following measures:

1. **Implement Rate Limiting**: Set rate limits on your API endpoints to restrict the number of requests per user or IP address. Use tools like Nginx, Apache, or third-party services like Cloudflare to enforce these limits.

2. **Use CAPTCHA**: Implement CAPTCHA challenges to prevent automated bots from making excessive requests.

3. **Input Validation**: Ensure that all inputs are properly validated to prevent large payloads from being processed.

4. **Monitor and Log**: Continuously monitor your API logs for suspicious activity and set up alerts for unusual patterns.

#### Secure Coding Fixes

Here is an example of how to implement rate limiting using Nginx:

**Nginx Configuration Example:**

```nginx
http {
    limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;

    server {
        listen 80;
        server_name example.com;

        location /api/ {
            limit_req zone=one burst=5 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

**Explanation:**
- `limit_req_zone`: Defines a shared memory zone to store the number of requests per IP address.
- `zone=one:10m`: Allocates 10MB of memory for storing the request counts.
- `rate=1r/s`: Sets the rate limit to 1 request per second.
- `burst=5`: Allows a burst of 5 requests above the normal rate limit.
- `nodelay`: Ensures that requests are not delayed during the burst.

#### Secure Code Example

Here is an example of how to implement rate limiting in a Python Flask application using Redis:

**Python Flask Example:**

```python
from flask import Flask, request, jsonify
import redis

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/api/login', methods=['POST'])
def login():
    ip_address = request.remote_addr
    key = f"rate_limit:{ip_address}"
    
    if redis_client.exists(key):
        remaining_requests = int(redis_client.get(key))
        if remaining_requests <= 0:
            return jsonify({"error": "Too many requests"}), 429
        else:
            redis_client.decr(key)
    else:
        redis_client.set(key, 5, ex=60)  # 5 requests per minute
    
    # Process login request
    username = request.form['username']
    password = request.form['password']
    
    # Validate credentials
    if validate_credentials(username, password):
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

def validate_credentials(username, password):
    # Dummy validation function
    return username == "admin" and password == "secret"

if __name__ == '__main__':
    app.run(debug=True)
```

**Explanation:**
- `redis_client.exists(key)`: Checks if the rate limit key exists for the IP address.
- `redis_client.get(key)`: Retrieves the remaining number of requests.
- `redis_client.decr(key)`: Decrements the remaining number of requests.
- `redis_client.set(key, 5, ex=60)`: Sets the rate limit key with 5 requests allowed per minute.

### Pitfalls and Common Mistakes

1. **Not Enforcing Limits**: Failing to enforce rate limits can leave your API vulnerable to abuse.
2. **Incorrect Configuration**: Misconfiguring rate limits can either be too strict (blocking legitimate users) or too lenient (allowing abuse).
3. **Ignoring Large Payloads**: Not validating large payloads can lead to resource exhaustion attacks.
4. **No Monitoring**: Failing to monitor API logs can make it difficult to detect and respond to abuse.

### Conclusion

Proper resource and rate limiting are essential for maintaining the security and performance of your API. By implementing these mechanisms, you can prevent abuse and ensure that your API remains responsive and available to legitimate users. Regular monitoring and logging are also crucial for detecting and responding to potential threats.

### Practice Labs

For hands-on practice with API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on API security, including rate limiting and resource exhaustion.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including API security.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application for practicing security skills, including API security.

These labs provide real-world scenarios and challenges to help you master API security concepts.

---
<!-- nav -->
[[01-Lack of Resource and Rate Limiting|Lack of Resource and Rate Limiting]] | [[API Security/05-OWASP API TOP 10/05-API4 Lack of Resources and Rate Limiting/00-Overview|Overview]] | [[API Security/05-OWASP API TOP 10/05-API4 Lack of Resources and Rate Limiting/03-Practice Questions & Answers|Practice Questions & Answers]]
