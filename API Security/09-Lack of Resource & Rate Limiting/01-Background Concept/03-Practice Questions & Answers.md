---
course: API Security
topic: Lack of Resource & Rate Limiting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain why lack of rate limiting in APIs can lead to security vulnerabilities.**

Rate limiting is crucial in securing APIs because it controls the number of requests a client can make within a certain time frame. Without rate limiting, attackers can exploit this by sending a high volume of requests, leading to several issues:

1. **Brute Force Attacks**: Attackers can attempt to guess passwords or other sensitive information by making numerous guesses rapidly. For example, if an API does not enforce rate limits on login attempts, an attacker can automate the process of guessing passwords until they succeed.

2. **Denial of Service (DoS)**: An attacker can flood the API with requests, overwhelming the server’s resources and causing legitimate requests to fail. This can render the service unavailable to genuine users.

3. **Resource Exhaustion**: High volumes of requests can exhaust server resources such as CPU, memory, and network bandwidth, leading to degraded performance or complete failure of the service.

**Q2. How would you exploit an API that lacks rate limiting to perform a brute force attack?**

To exploit an API that lacks rate limiting for a brute force attack, follow these steps:

1. **Identify the Login Endpoint**: Determine which endpoint is used for authentication. This is typically found in the API documentation or through inspection of the application.

2. **Enumerate Usernames**: If possible, gather a list of valid usernames. This can be done through social engineering, leaked data, or by using enumeration techniques if the API allows it.

3. **Craft Requests**: Create automated scripts to send login requests with different password combinations. The script should iterate through a list of potential passwords for each username.

4. **Monitor Responses**: Analyze the responses to determine whether the login was successful or not. Common indicators include HTTP status codes (e.g., 200 OK vs. 401 Unauthorized) or specific error messages.

Here’s a simple Python script to demonstrate this:

```python
import requests

def brute_force_login(url, usernames, passwords):
    for username in usernames:
        for password in passwords:
            response = requests.post(url, json={"username": username, "password": password})
            if response.status_code == 200:
                print(f"Success! Username: {username}, Password: {password}")
                return
            else:
                print(f"Failed: Username: {username}, Password: {password}")

# Example usage
url = "https://example.com/api/login"
usernames = ["admin", "user"]
passwords = ["password123", "123456"]

brute_force_login(url, usernames, passwords)
```

**Q3. Describe a recent real-world example where lack of rate limiting led to a security breach.**

One notable example is the Zoom API vulnerability in early 2020. At the time, Zoom allowed users to create meetings with six-digit passcodes, and there was no rate limiting on login attempts. This made it feasible for attackers to perform brute force attacks on meeting passcodes. By automating the process of guessing passcodes, attackers could gain unauthorized access to Zoom meetings, leading to privacy breaches and potential exposure of sensitive information.

This vulnerability highlighted the importance of implementing rate limiting and enforcing strong authentication mechanisms to prevent such attacks.

**Q4. How would you configure rate limiting on an API to mitigate brute force attacks and DoS attacks?**

To configure rate limiting effectively, consider the following strategies:

1. **Set Reasonable Limits**: Define a maximum number of requests a client can make within a specified time frame. For example, allow 100 requests per minute per IP address.

2. **Use Tokens or Sessions**: Implement token-based authentication where each request must include a valid token. Limit the number of tokens issued and their validity period.

3. **Implement Exponential Backoff**: After a certain number of failed attempts, increase the waiting time before allowing further requests. This makes brute force attacks less effective.

4. **Use CAPTCHAs**: Introduce CAPTCHA challenges after a certain number of failed login attempts to ensure that the request is coming from a human.

Here’s an example configuration using Nginx for rate limiting:

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;

    server {
        location /api/ {
            limit_req zone=api_limit burst=5 nodelay;
            proxy_pass http://backend_server;
        }
    }
}
```

In this configuration, `limit_req_zone` defines a shared memory zone named `api_limit` that stores the IP addresses and their request counts. The `rate=10r/m` directive sets the rate limit to 10 requests per minute. The `burst=5` directive allows a small number of additional requests beyond the rate limit.

**Q5. Explain how lack of resource management in APIs can lead to denial of service attacks.**

Lack of proper resource management in APIs can lead to denial of service (DoS) attacks in several ways:

1. **Excessive Resource Consumption**: If an API does not properly manage resource allocation, an attacker can send requests that consume excessive amounts of CPU, memory, or disk space. For example, requesting a large number of records from a database can overwhelm the server.

2. **Infinite Loops or Recursive Calls**: Poorly designed APIs may contain logic that can lead to infinite loops or recursive calls, consuming all available resources and preventing the server from handling legitimate requests.

3. **Parameter Manipulation**: Attackers can manipulate input parameters to cause the API to perform resource-intensive operations. For instance, changing a pagination parameter to a very large number can cause the API to fetch and process an excessive amount of data.

4. **Concurrency Issues**: If an API does not properly manage concurrent requests, multiple simultaneous requests can overwhelm the server, leading to degraded performance or crashes.

By ensuring proper resource management, such as setting limits on query sizes, enforcing timeouts, and validating input parameters, developers can mitigate the risk of DoS attacks.

---
<!-- nav -->
[[02-Lack of Resource & Rate Limiting in APIs|Lack of Resource & Rate Limiting in APIs]] | [[API Security/09-Lack of Resource & Rate Limiting/01-Background Concept/00-Overview|Overview]]
