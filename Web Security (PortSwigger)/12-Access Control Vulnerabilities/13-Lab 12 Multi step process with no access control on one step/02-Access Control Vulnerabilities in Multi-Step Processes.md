---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities in Multi-Step Processes

### Introduction to Access Control Vulnerabilities

Access control vulnerabilities occur when an application fails to properly restrict access to certain resources or actions based on the user's privileges. In a multi-step process, these vulnerabilities can be particularly dangerous because an attacker might bypass intermediate checks and directly manipulate the final outcome. This chapter will delve into the specifics of such vulnerabilities, using a practical example to illustrate the concepts.

### Understanding the Example Scenario

In the given scenario, we have an application with an administrative panel that allows users to upgrade or downgrade other users. The process involves two steps:

1. **Initial Request**: A GET request to `/admin/roles` with parameters specifying the user to be upgraded and the action to be performed.
2. **Confirmation Request**: A POST request to the same `/admin/roles` endpoint to confirm the action.

Let's break down each step and understand the potential vulnerabilities.

#### Step 1: Initial Request

The initial request is made to the `/admin/roles` endpoint with the following parameters:

```http
GET /admin/roles?username=carlos&action=upgrade HTTP/1.1
Host: example.com
Cookie: sessionid=abc123
```

This request specifies the user (`carlos`) and the action (`upgrade`). The `sessionid` cookie ensures that the request is authenticated as the current user.

#### Step 2: Confirmation Request

After the initial request, the user is prompted to confirm the action. The confirmation request is a POST request to the same endpoint:

```http
POST /admin/roles HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Cookie: sessionid=abc123

username=carlos&action=upgrade&confirm=true
```

This request confirms the action by setting the `confirm` parameter to `true`.

### Multi-Step Process Vulnerability

The vulnerability arises when the application does not properly enforce access controls at each step of the process. Specifically, if the application fails to verify the user's permissions before processing the confirmation request, an attacker could bypass the intermediate checks and directly manipulate the final outcome.

#### Real-World Examples

Recent vulnerabilities in multi-step processes have been observed in various applications. For instance, CVE-2021-3129 affected a popular content management system, allowing attackers to bypass access controls in a multi-step user management process. Another example is CVE-2022-22965, which impacted a widely used e-commerce platform, enabling unauthorized privilege escalation through a similar multi-step process.

### How to Exploit the Vulnerability

To exploit this vulnerability, an attacker would need to intercept and modify the confirmation request. By removing or altering the `confirm` parameter, the attacker can force the application to perform the action without proper authorization.

#### Example Exploit

Consider the following modified confirmation request:

```http
POST /admin/roles HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Cookie: sessionid=abc123

username=admin&action=downgrade
```

Here, the attacker has changed the `action` parameter to `downgrade` and removed the `confirm` parameter. If the application does not properly validate the request, it may execute the downgrade action without prompting for confirmation.

### How to Prevent / Defend Against Access Control Vulnerabilities

#### Detection

To detect access control vulnerabilities, security teams should perform thorough testing of multi-step processes. Automated tools like Burp Suite, ZAP, and OWASP ZAP can help identify potential issues by intercepting and modifying requests.

#### Prevention

1. **Enforce Access Controls at Each Step**:
   Ensure that the application verifies the user's permissions at each step of the process. This includes both the initial request and the confirmation request.

2. **Use Nonces or Tokens**:
   Implement nonces or tokens to ensure that each request is unique and cannot be replayed. This adds an additional layer of security by preventing attackers from reusing intercepted requests.

3. **Secure Coding Practices**:
   Follow secure coding practices to avoid common pitfalls. For example, always validate user input and ensure that sensitive operations are protected by appropriate access controls.

#### Secure Code Fix

Here is an example of how to implement proper access controls in a multi-step process:

```python
# Vulnerable code
def handle_upgrade_request(username, action):
    if action == 'upgrade':
        upgrade_user(username)

def handle_confirmation_request(username, action, confirm):
    if confirm:
        handle_upgrade_request(username, action)
```

```python
# Secure code
def handle_upgrade_request(username, action, nonce):
    if action == 'upgrade' and validate_nonce(nonce):
        upgrade_user(username)

def handle_confirmation_request(username, action, confirm, nonce):
    if confirm and validate_nonce(nonce):
        handle_upgrade_request(username, action, nonce)
```

In the secure code, the `validate_nonce` function ensures that the request is valid and has not been tampered with.

### Conclusion

Access control vulnerabilities in multi-step processes can be exploited to bypass intermediate checks and manipulate the final outcome. By enforcing strict access controls at each step, using nonces or tokens, and following secure coding practices, developers can mitigate these risks and ensure the security of their applications.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different types of access control vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application with several access control issues to explore and exploit.
- **DVWA (Damn Vulnerable Web Application)**: Contains numerous vulnerabilities, including access control issues, for educational purposes.

These labs provide a safe environment to learn and practice identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/13-Lab 12 Multi step process with no access control on one step/01-Introduction to Access Control Vulnerabilities|Introduction to Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/13-Lab 12 Multi step process with no access control on one step/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/13-Lab 12 Multi step process with no access control on one step/03-Access Control Vulnerabilities|Access Control Vulnerabilities]]
