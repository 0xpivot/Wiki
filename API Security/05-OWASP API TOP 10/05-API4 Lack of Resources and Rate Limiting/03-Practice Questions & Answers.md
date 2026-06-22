---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain why lack of resources and rate limiting can be a security risk for APIs.**

Lack of resources and rate limiting can be significant security risks for APIs because they allow attackers to overwhelm the system with excessive requests or large payloads. This can lead to denial-of-service (DoS) attacks, where the API becomes unresponsive and cannot handle legitimate requests. Additionally, without proper rate limiting, attackers can exploit vulnerabilities such as brute-force attacks, where they repeatedly attempt to guess passwords or other sensitive information. 

For example, in a recent breach involving a WordPress site, attackers exploited a lack of rate limiting on the login API, allowing them to perform brute-force attacks and gain unauthorized access to the site. Proper rate limiting and resource management can prevent such attacks by ensuring that the API can only handle a reasonable number of requests within a given time frame.

**Q2. How would you configure rate limiting to protect an API from brute-force attacks?**

To protect an API from brute-force attacks, you can configure rate limiting by setting a maximum number of failed login attempts allowed within a specific time period. For instance, you might set a limit of three failed login attempts per minute before temporarily blocking the IP address or account. Here’s an example configuration in a hypothetical API:

```python
from flask import Flask, request
from flask_limiter import Limiter

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

@limiter.limit("3/minute", error_message="Too many login attempts. Please try again later.")
@app.route('/login', methods=['POST'])
def login():
    # Login logic here
    return {"message": "Login successful"}

def get_remote_address():
    return request.remote_addr
```

This configuration limits the number of POST requests to the `/login` endpoint to three per minute, helping to mitigate brute-force attacks.

**Q3. Explain how an attacker could exploit a lack of rate limiting on a file upload API.**

An attacker could exploit a lack of rate limiting on a file upload API by uploading extremely large files or a large number of files in rapid succession. This can exhaust the server's memory and CPU resources, leading to a denial-of-service condition. For example, if an API allows users to upload images without any size or rate limitations, an attacker could upload a massive image or a series of large images, causing the server to run out of memory while creating thumbnails or processing the images.

A real-world example is the case of a popular photo-sharing platform that experienced a DoS attack due to a lack of rate limiting on its file upload API. Attackers uploaded numerous large images, overwhelming the server and making the service unavailable to legitimate users.

**Q4. How would you implement resource exhaustion protection for an API that returns a list of users with a limit of 200 users per page?**

To implement resource exhaustion protection for an API that returns a list of users with a limit of 200 users per page, you can enforce strict validation on the input parameters and limit the maximum number of users returned per request. Here’s an example implementation in Python:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 100))

    # Enforce a maximum size limit
    if size > 200:
        size = 200

    # Fetch users from the database
    users = fetch_users_from_db(page, size)
    
    return {"users": users}

def fetch_users_from_db(page, size):
    # Database query logic here
    return [{"id": i, "name": f"User {i}"} for i in range((page - 1) * size, page * size)]
```

By enforcing a maximum size limit, you prevent attackers from requesting an excessively large number of users, which could cause performance issues on the database and make the API unresponsive.

**Q5. Describe how an attacker could exploit a lack of rate limiting on a two-factor authentication (2FA) API.**

An attacker could exploit a lack of rate limiting on a two-factor authentication (2FA) API by repeatedly attempting to enter incorrect one-time passwords (OTPs). Without rate limiting, the attacker can keep trying different OTPs until they eventually succeed, effectively bypassing the 2FA mechanism. This can be particularly dangerous if the attacker has already obtained the user's regular password through other means, such as phishing or brute-forcing.

For example, if an API does not limit the number of OTP attempts, an attacker could write a script to continuously try different OTPs until they gain access. To prevent this, you should implement rate limiting on the 2FA API, such as allowing only three attempts per minute before temporarily blocking the account or IP address.

**Q6. What is a Gip bomb and how can it be used to exploit a lack of resource management in an API?**

A Gip bomb is a type of malicious archive file that has been designed to consume excessive amounts of resources when unpacked. When an API lacks proper resource management, an attacker can exploit this by uploading a Gip bomb, causing the server to use up all available memory and CPU resources while trying to unpack the file. This can result in a denial-of-service condition, making the API unresponsive to legitimate requests.

For example, an attacker could upload a Gip bomb to an API that processes file uploads, causing the server to exhaust its resources and become unresponsive. To prevent this, the API should include mechanisms to limit the size and complexity of files that can be uploaded and to monitor resource usage to detect and mitigate such attacks.

---
<!-- nav -->
[[02-Lack of Resources and Rate Limiting|Lack of Resources and Rate Limiting]] | [[API Security/05-OWASP API TOP 10/05-API4 Lack of Resources and Rate Limiting/00-Overview|Overview]]
