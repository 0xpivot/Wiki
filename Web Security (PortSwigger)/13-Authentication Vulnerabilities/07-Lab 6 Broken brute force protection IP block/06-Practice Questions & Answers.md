---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the verbose error messages in the login process are a security vulnerability.**

Verbose error messages, such as those indicating whether the username or password is incorrect, provide attackers with valuable information. Specifically, they can use these messages to determine if a username is valid, which simplifies the brute-force attack process. By knowing a valid username, attackers can focus their efforts on guessing the password for that specific user, significantly reducing the complexity and time required for a successful attack.

**Q2. How would you exploit the broken brute force protection mechanism described in the lab?**

To exploit the broken brute force protection mechanism, you can use a combination of manual and automated techniques. First, identify the pattern of the soft lockout mechanism, which locks out the user after a certain number of incorrect login attempts. In this lab, the system locks out after three attempts. However, logging in with valid credentials resets the counter. Therefore, you can use a script to alternate between two incorrect password attempts and one correct login attempt to reset the counter. This method allows you to continue attempting passwords without triggering the lockout mechanism.

Here’s a simplified Python script to achieve this:

```python
with open('passwords.txt', 'r') as f:
    passwords = f.readlines()

for i in range(0, len(passwords), 3):
    # Attempt two incorrect passwords
    print(f"Carlos {passwords[i].strip()}")
    print(f"Carlos {passwords[i+1].strip()}")

    # Reset the counter with a valid login
    print("Peter peter")
```

This script alternates between two incorrect password attempts for `Carlos` and one correct login attempt with `Peter`, effectively bypassing the lockout mechanism.

**Q3. Why is it important to limit the number of concurrent requests in the brute force attack?**

Limiting the number of concurrent requests is crucial to avoid triggering the soft lockout mechanism. If multiple requests are sent simultaneously, the server may interpret this as a brute force attack and lock out the user. In the lab, setting the maximum concurrent requests to one ensures that each request is processed sequentially, preventing the lockout mechanism from being triggered. This allows the attacker to continue the brute force attack without interruption.

**Q4. How would you configure Burp Suite to perform the brute force attack with the correct sequence of requests?**

To configure Burp Suite for the brute force attack, follow these steps:

1. **Send the Login Request to Repeater**: Capture the login request and send it to Repeater.
2. **Create Payload Lists**: Create two payload lists: one for usernames and one for passwords. The username list should alternate between `Carlos` and the valid user (`Peter`). The password list should include the candidate passwords and the valid password for `Peter`.
3. **Configure Intruder**:
   - Set the target URL to the login endpoint.
   - Add the positions for the username and password fields.
   - Load the payload lists into the respective positions.
   - Configure the resource pool to allow only one concurrent request.
4. **Start the Attack**: Initiate the attack and monitor the responses for a successful login (HTTP 302 status).

By configuring Burp Suite this way, you ensure that the attack follows the correct sequence of requests, alternating between incorrect password attempts and valid login attempts to reset the counter.

**Q5. What recent real-world example demonstrates the importance of proper brute force protection mechanisms?**

One recent example is the breach of the Capital One data in 2019 (CVE-2019-11274). The attacker exploited a misconfigured server that allowed unauthorized access to sensitive customer data. Although this breach was not directly related to a brute force attack, it highlights the importance of robust security measures, including effective brute force protection mechanisms. Proper implementation of rate limiting and account lockout policies can prevent unauthorized access attempts and protect against similar breaches.

In summary, the Capital One breach underscores the necessity of implementing strong security controls, including effective brute force protection, to safeguard against unauthorized access and data breaches.

---
<!-- nav -->
[[05-Lab Setup Broken Brute Force Protection IP Block|Lab Setup Broken Brute Force Protection IP Block]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/07-Lab 6 Broken brute force protection IP block/00-Overview|Overview]]
