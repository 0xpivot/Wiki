---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to External Requests Using Python

In the realm of DevOps, making external requests to remote applications is a common task. One of the most popular modules used for this purpose is `requests`. This module simplifies the process of sending HTTP requests and handling responses from remote applications. In this section, we will delve deep into how to use the `requests` module to interact with remote applications, specifically focusing on GitLab as an example.

### What is the `requests` Module?

The `requests` module is a powerful and user-friendly HTTP library for Python. It allows you to send HTTP requests and handle the responses easily. Unlike some other libraries, `requests` abstracts away many of the complexities involved in making HTTP requests, such as handling different types of HTTP methods (GET, POST, PUT, DELETE, etc.), managing cookies, and parsing responses.

#### Why Use `requests`?

Using `requests` offers several advantages:

1. **Ease of Use**: The `requests` module provides a simple and intuitive interface for making HTTP requests.
2. **Comprehensive Features**: It supports various HTTP methods, handles cookies, and parses responses automatically.
3. **Community Support**: Being widely used, `requests` has extensive community support and documentation.

### Installing the `requests` Module

Since `requests` is not included in the standard Python library, you need to install it using `pip`, the Python package installer. Ensure you have `pip` installed, which typically comes bundled with Python installations.

#### Installation Steps

1. Open your terminal or command prompt.
2. Run the following command to install `requests`:

```bash
pip install requests
```

Upon successful installation, you should see output similar to the following:

```
Collecting requests
  Downloading requests-2.28.1-py2.py3-none-any.whl (62 kB)
Installing collected packages: requests
Successfully installed requests-2.28.1
```

After installation, you can verify that the module is installed correctly by checking the `site-packages` directory in your Python environment.

### Importing and Using the `requests` Module

Once `requests` is installed, you can import it in your Python script and start using its functionalities.

#### Basic Usage Example

Here’s a basic example of how to use `requests` to make a GET request to a remote server:

```python
import requests

response = requests.get('https://api.gitlab.com')
print(response.status_code)
print(response.text)
```

This script sends a GET request to the GitLab API and prints the status code and response body.

### Making Requests to GitLab

GitLab is a popular web-based Git repository manager that provides a RESTful API for interacting with repositories, users, and other resources. Let’s explore how to use `requests` to interact with GitLab.

#### Authentication

To authenticate with GitLab, you typically need to provide an access token. This token is used to identify the user making the request.

##### Obtaining an Access Token

You can obtain an access token by following these steps:

1. Log in to your GitLab account.
2. Navigate to your profile settings.
3. Go to the "Access Tokens" section.
4. Generate a new access token with the necessary scopes.

##### Using the Access Token

Once you have the access token, you can include it in your requests using the `headers` parameter.

#### Example: Fetching User Information

Let’s fetch user information from GitLab using the `requests` module.

```python
import requests

access_token = 'your_access_token_here'
headers = {'PRIVATE-TOKEN': access_token}

response = requests.get('https://gitlab.com/api/v4/user', headers=headers)

if response.status_code == 200:
    print("User Information:")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
```

This script sends a GET request to the GitLab API endpoint `/api/v4/user` and includes the access token in the `PRIVATE-TOKEN` header. If the request is successful, it prints the user information; otherwise, it prints an error message.

### Handling Different HTTP Methods

The `requests` module supports various HTTP methods, including GET, POST, PUT, DELETE, and more. Here are examples of how to use these methods.

#### GET Request

A GET request is used to retrieve data from a server.

```python
response = requests.get('https://api.gitlab.com/projects')
print(response.json())
```

#### POST Request

A POST request is used to send data to a server to create a resource.

```python
data = {
    'name': 'New Project',
    'description': 'This is a new project'
}
response = requests.post('https://gitlab.com/api/v4/projects', json=data, headers=headers)
print(response.json())
```

#### PUT Request

A PUT request is used to update an existing resource.

```python
data = {
    'name': 'Updated Project',
    'description': 'This is an updated project'
}
response = requests.put('https://gitlab.com/api/v4/projects/project_id', json=data, headers=headers)
print(response.json())
```

#### DELETE Request

A DELETE request is used to delete a resource.

```python
response = requests.delete('https://gitlab.com/api/v4/projects/project_id', headers=headers)
print(response.status_code)
```

### Error Handling and Responses

When making HTTP requests, it’s important to handle potential errors and parse the responses correctly.

#### Checking Response Status Codes

HTTP status codes indicate the outcome of a request. Common status codes include:

- **200 OK**: The request was successful.
- **201 Created**: A new resource was created.
- **400 Bad Request**: The request was invalid.
- **401 Unauthorized**: Authentication failed.
- **404 Not Found**: The requested resource does not exist.
- **500 Internal Server Error**: An unexpected error occurred on the server.

#### Parsing Responses

Responses from the server can be parsed using the `.json()` method if the response is in JSON format.

```python
response = requests.get('https://api.gitlab.com/projects')
if response.status_code == 200:
    projects = response.json()
    for project in projects:
        print(project['name'])
else:
    print(f"Error: {response.status_code}")
```

### Security Considerations

When making HTTP requests, especially to sensitive APIs like GitLab, security is paramount. Here are some key points to consider:

#### Secure Communication

Always use HTTPS to ensure that data is transmitted securely. HTTPS encrypts the data between the client and the server, preventing eavesdropping and man-in-the-middle attacks.

#### Protecting Access Tokens

Access tokens should be treated as sensitive credentials. Avoid hardcoding them in your scripts and store them securely. Consider using environment variables or a secrets management service.

#### Rate Limiting

APIs often enforce rate limits to prevent abuse. Be aware of the rate limits imposed by the API and handle them appropriately in your code.

### How to Prevent / Defend

#### Detection

Regularly monitor your API usage and logs to detect any unauthorized access or unusual activity. Tools like GitLab’s built-in logging and monitoring features can help with this.

#### Prevention

1. **Use Strong Authentication**: Always use strong authentication mechanisms, such as OAuth or JWT.
2. **Limit Permissions**: Grant access tokens only the minimum permissions required.
3. **Secure Storage**: Store access tokens securely, using environment variables or secrets management services.
4. **Rate Limiting**: Implement rate limiting to prevent abuse.

#### Secure Coding Fixes

Here’s an example of how to securely handle access tokens:

**Vulnerable Code:**

```python
access_token = 'your_access_token_here'
headers = {'PRIVATE-TOKEN': access_token}
```

**Secure Code:**

```python
import os

access_token = os.getenv('GITLAB_ACCESS_TOKEN')
headers = {'PRIVATE-TOKEN': access_token}
```

By using environment variables, you avoid hardcoding sensitive information in your scripts.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-22205

CVE-2021-22205 is a critical vulnerability in GitLab that allowed attackers to bypass authentication and gain unauthorized access to sensitive data. This vulnerability highlights the importance of keeping your software up-to-date and securing access tokens.

#### Example: GitLab Data Breach

In 2021, GitLab experienced a data breach that exposed sensitive user information. This incident underscores the importance of secure coding practices and regular security audits.

### Conclusion

Using the `requests` module to make external requests to remote applications like GitLab is a fundamental skill in DevOps. By understanding how to use `requests`, handle different HTTP methods, and manage security considerations, you can effectively interact with remote APIs and build robust applications.

### Practice Labs

For hands-on practice with `requests` and GitLab, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including API interactions.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning web security.

These labs provide practical experience in using `requests` and interacting with APIs securely.

---

This comprehensive chapter covers the essential concepts, detailed explanations, and practical examples needed to master making external requests using the `requests` module in Python.

---
<!-- nav -->
[[02-Introduction to API Requests in Python|Introduction to API Requests in Python]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/12-Python API Requests to GitLab/00-Overview|Overview]] | [[04-Introduction to GitLab API and Python Requests|Introduction to GitLab API and Python Requests]]
