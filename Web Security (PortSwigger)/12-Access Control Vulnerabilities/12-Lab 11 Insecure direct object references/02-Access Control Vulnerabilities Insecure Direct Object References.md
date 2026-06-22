---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities: Insecure Direct Object References

### Introduction to Access Control Vulnerabilities

Access control vulnerabilities occur when a web application fails to properly restrict access to resources based on the identity and permissions of the user. One common type of access control vulnerability is the **Insecure Direct Object Reference (IDOR)**. This occurs when an application exposes a reference to an internal object (such as a file, database record, or directory) using a predictable parameter, allowing unauthorized users to manipulate these parameters to access sensitive data.

### Understanding Insecure Direct Object References

An **Insecure Direct Object Reference** (IDOR) is a flaw that allows attackers to bypass authorization mechanisms by manipulating parameters that reference objects directly. These objects could be files, database records, or other resources. The key issue is that the application does not validate whether the user has the necessary permissions to access the referenced object.

#### Example Scenario

Consider the scenario described in the lecture:

- A user sends a message and receives a response.
- The application makes a POST request to download a transcript.
- The response redirects to a URL containing a static identifier (e.g., `1.txt`).

The user then tries to access another chat history by changing the identifier to `2.txt`. Since the application does not validate the user's permissions, the user gains access to another chat history, which is a clear indication of an IDOR vulnerability.

### Detailed Explanation of the Scenario

Let's break down the scenario step-by-step:

1. **Initial Request**:
    - The user sends a message and receives a response.
    - The application makes a POST request to download a transcript.
    - The response redirects to a URL containing a static identifier (e.g., `1.txt`).

    ```http
    POST /download_transcript HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "message": "test"
    }

    HTTP/1.1 302 Found
    Location: http://example.com/transcripts/1.txt
    ```

2. **Accessing Another Chat History**:
    - The user changes the identifier to `2.txt` and accesses another chat history.
    - This indicates that the application does not validate the user's permissions before providing access to the resource.

    ```http
    GET /transcripts/2.txt HTTP/1.1
    Host: example.com

    HTTP/1.1 200 OK
    Content-Type: text/plain

    User: test
    Application: Response
    User: test
    Application: Response
    ```

### Why IDOR Matters

IDOR vulnerabilities can lead to serious security issues such as:

- **Data Exposure**: Unauthorized users can access sensitive data.
- **Information Leakage**: Attackers can discover the structure of the application and its underlying data.
- **Privilege Escalation**: Users might gain access to resources intended for higher-privileged users.

### How IDOR Works Under the Hood

To understand how IDOR works, consider the following aspects:

1. **Predictable Identifiers**:
    - The identifiers used to reference objects are often sequential numbers or simple strings.
    - This predictability makes it easy for attackers to guess and manipulate these identifiers.

2. **Lack of Authorization Checks**:
    - The application does not verify whether the user has the necessary permissions to access the referenced object.
    - This oversight allows unauthorized users to access sensitive data.

### Real-World Examples

Recent real-world examples of IDOR vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the WordPress REST API allowed unauthorized users to access private posts.
- **CVE-2022-22965**: A vulnerability in the Atlassian Jira Software allowed unauthorized users to access sensitive data.

### How to Prevent / Defend Against IDOR

#### Detection

To detect IDOR vulnerabilities, you can use automated tools and manual testing techniques:

1. **Automated Tools**:
    - **Burp Suite**: Use Burp Suite to intercept and modify HTTP requests to identify predictable identifiers.
    - **OWASP ZAP**: Use OWASP ZAP to scan for IDOR vulnerabilities.

2. **Manual Testing**:
    - Change the identifier in the URL and observe if the application returns unauthorized data.
    - Use different user accounts to test if the application properly enforces access controls.

#### Prevention

To prevent IDOR vulnerabilities, follow these best practices:

1. **Validate User Permissions**:
    - Ensure that the application checks the user's permissions before granting access to any resource.
    - Use role-based access control (RBAC) to enforce access policies.

2. **Use Non-Predictable Identifiers**:
    - Use UUIDs or other non-predictable identifiers instead of sequential numbers.
    - This makes it harder for attackers to guess and manipulate identifiers.

3. **Session Management**:
    - Ensure that session tokens are securely managed and validated.
    - Use secure session management practices to prevent session hijacking.

#### Secure Coding Fixes

Here is an example of how to implement secure coding practices to prevent IDOR:

```python
# Vulnerable Code
@app.route('/transcripts/<int:file_id>')
def get_transcript(file_id):
    filename = f'{file_id}.txt'
    return send_file(filename)

# Secure Code
@app.route('/transcripts/<int:file_id>')
@login_required
def get_transcript(file_id):
    user_id = current_user.id
    filename = f'{file_id}.txt'
    
    # Check if the user has permission to access the file
    if user_has_permission(user_id, file_id):
        return send_file(filename)
    else:
        abort(403)
```

### Common Pitfalls

When implementing access control, be aware of the following common pitfalls:

1. **Hardcoding Permissions**:
    - Avoid hardcoding permissions in the application logic.
    - Use dynamic permission checks based on user roles and session context.

2. **Ignoring Session Context**:
    - Ensure that the application considers the session context when validating permissions.
    - Do not rely solely on URL parameters to determine access rights.

### Conclusion

Insecure Direct Object References (IDOR) are a significant security risk that can lead to data exposure and privilege escalation. By understanding the underlying mechanisms and implementing robust access control measures, developers can mitigate these risks and ensure the security of their applications.

### Practice Labs

For hands-on practice with IDOR vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about and test for IDOR vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice identifying and exploiting IDOR vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Contains various web application vulnerabilities, including IDOR, for educational purposes.

By engaging with these labs, you can gain practical experience in detecting and preventing IDOR vulnerabilities in real-world scenarios.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/12-Lab 11 Insecure direct object references/01-Introduction to Access Control Vulnerabilities|Introduction to Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/12-Lab 11 Insecure direct object references/00-Overview|Overview]] | [[03-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]]
