---
course: API Security
topic: Lab Setup & Postman Document Sharing
tags: [api-security]
---

## Lab Setup and Postman Document Sharing

### Introduction to API Security Labs

In the realm of API security, practical labs are essential for understanding and testing various security mechanisms and vulnerabilities. This chapter will guide you through setting up a lab environment using Docker and sharing API documentation via Postman. We will cover the necessary steps to set up a lab environment, including installing Docker, running Docker Compose, and configuring Postman for API testing.

### Prerequisites

Before diving into the lab setup, ensure you have the following prerequisites installed:

1. **Docker**: A platform for developing, shipping, and running applications inside lightweight containers.
2. **Docker Compose**: A tool for defining and running multi-container Docker applications.

#### Installing Docker

To install Docker, follow these steps:

1. **For Linux**:
    - Update your package manager:
      ```bash
      sudo apt-get update
      ```
    - Install Docker:
      ```bash
      sudo apt-get install docker.io
      ```

2. **For macOS**:
    - Download Docker Desktop from the official website.
    - Follow the installation instructions provided.

3. **For Windows**:
    - Download Docker Desktop from the official website.
    - Follow the installation instructions provided.

#### Verifying Docker Installation

After installation, verify that Docker is correctly installed by running the following command:

```bash
docker --version
```

This should output the version of Docker installed on your system.

### Setting Up the Lab Environment

The lab environment we will set up is based on the DVWF (Damn Vulnerable Web Framework) Node application. This application is designed to demonstrate various web security vulnerabilities and is useful for learning and testing purposes.

#### Running DVWF Node Application

1. **Navigate to the Directory**:
    - Open a terminal and navigate to the directory containing the DVWF Node application:
      ```bash
      cd ~/path/to/dvwf-node
      ```

2. **Run Docker Compose**:
    - Ensure you have the `docker-compose.yml` file in the directory. This file defines the services and configurations required to run the application.
    - Run the following command to start the application:
      ```bash
      docker-compose up
      ```

3. **Check the Running Containers**:
    - Verify that the containers are running by checking the ports:
      ```bash
      docker ps
      ```

4. **Handling Port Conflicts**:
    - If the port 80 is already in use, you need to kill the process using that port. Use the following commands to identify and kill the process:
      ```bash
      lsof -i :80
      sudo kill -9 <PID>
      ```

5. **Restart Docker Compose**:
    - After killing the conflicting process, restart Docker Compose:
      ```bash
      docker-compose up
      ```

### Configuring Postman for API Testing

Postman is a powerful tool for testing APIs. In this section, we will configure Postman to test the DVWF Node application.

#### Sharing Postman Collection

1. **Open Postman**:
    - Launch Postman and create a new collection for the DVWF Node application.

2. **Import Collection**:
    - Import the shared Postman collection by clicking on the "Import" button and selecting the JSON file.

3. **Configure Variables**:
    - Set the environment variables required for the API requests. For example, set the base URL to `http://192.168.1.164:80`.

4. **Make API Requests**:
    - Use the imported collection to make API requests. Click on the "Send" button to execute the requests and observe the responses.

### Example of API Request and Response

Here is an example of an API request and its corresponding response:

```http
GET http://192.168.1.164:80/api/users HTTP/1.1
Host: 192.168.1.164:80
User-Agent: PostmanRuntime/7.28.0
Accept: */*
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 12:00:00 GMT
Content-Type: application/json
Content-Length: 123
Connection: keep-alive

{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane.smith@example.com"
    }
  ]
}
```

### Common Pitfalls and How to Avoid Them

#### Port Conflicts

One common issue is port conflicts. If another service is already using port 80, Docker Compose will fail to start the containers. To avoid this:

1. **Identify the Process Using the Port**:
    - Use the `lsof` command to find the process ID (PID) using the port:
      ```bash
      lsof -i :80
      ```

2. **Kill the Process**:
    - Kill the process using the identified PID:
      ```bash
      sudo kill -9 <PID>
      ```

3. **Restart Docker Compose**:
    - Restart Docker Compose after resolving the conflict:
      ```bash
      docker-compose up
      ```

### Real-World Examples and Recent CVEs

#### CVE-2021-21972: Apache Struts Remote Code Execution

Apache Struts is a popular framework for building web applications. In 2021, a critical vulnerability (CVE-2021-21972) was discovered that allowed remote code execution. This vulnerability could be exploited by sending malicious input to the server, leading to unauthorized access and potential data breaches.

#### Secure Coding Practices

To prevent such vulnerabilities, follow these secure coding practices:

1. **Input Validation**:
    - Validate all user inputs to ensure they meet expected formats and constraints.
    - Use libraries like OWASP Java HTML Sanitizer for sanitizing user inputs.

2. **Parameterized Queries**:
    - Use parameterized queries to prevent SQL injection attacks.
    - Example:
      ```java
      String query = "SELECT * FROM users WHERE username = ?";
      PreparedStatement statement = connection.prepareStatement(query);
      statement.setString(1, username);
      ResultSet resultSet = statement.executeQuery();
      ```

3. **Least Privilege Principle**:
    - Ensure that applications run with the least privileges necessary to perform their tasks.
    - Avoid running applications as root or administrator unless absolutely necessary.

### How to Prevent / Defend

#### Detection

1. **Logging and Monitoring**:
    - Implement comprehensive logging and monitoring to detect unusual activities.
    - Use tools like ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging and analysis.

2. **Security Scanning Tools**:
    - Regularly scan your applications using tools like OWASP ZAP, Burp Suite, or SonarQube to identify vulnerabilities.

#### Prevention

1. **Secure Configuration Management**:
    - Use configuration management tools like Ansible, Puppet, or Chef to maintain consistent and secure configurations across environments.

2. **Regular Updates and Patch Management**:
    - Keep all dependencies and frameworks up to date to mitigate known vulnerabilities.
    - Use tools like Dependabot or Renovate to automate dependency updates.

#### Secure Coding Fixes

Compare the vulnerable code snippet with the secure version:

**Vulnerable Code**:
```java
String query = "SELECT * FROM users WHERE username = '" + username + "'";
ResultSet resultSet = statement.executeQuery(query);
```

**Secure Code**:
```java
String query = "SELECT * FROM users WHERE username = ?";
PreparedStatement statement = connection.prepareStatement(query);
statement.setString(1, username);
ResultSet resultSet = statement.executeQuery();
```

### Hands-On Labs

For hands-on practice, consider the following labs:

1. **PortSwigger Web Security Academy**:
    - Offers a variety of labs covering different aspects of web security, including API security.
    - [Link](https://portswigger.net/web-security)

2. **OWASP Juice Shop**:
    - A deliberately insecure web application for security training.
    - [Link](https://owasp.org/www-project-juice-shop/)

3. **DVWA (Damn Vulnerable Web Application)**:
    - A PHP/MySQL web application that is riddled with vulnerabilities.
    - [Link](https://github.com/ethicalhack3r/DVWA)

4. **WebGoat**:
    - An interactive, gamified training application for learning about web application security.
    - [Link](https://github.com/WebGoat/WebGoat)

### Conclusion

Setting up a lab environment for API security testing is crucial for understanding and mitigating various security vulnerabilities. By following the steps outlined in this chapter, you can effectively set up and configure a lab environment using Docker and Postman. Additionally, by adhering to secure coding practices and regularly updating your applications, you can significantly reduce the risk of security breaches.

---
<!-- nav -->
[[01-Introduction to Lab Setup and Postman Document Sharing|Introduction to Lab Setup and Postman Document Sharing]] | [[API Security/03-Lab Setup & Postman Document Sharing/01-Lab Setup Postman Document Sharing/00-Overview|Overview]] | [[API Security/03-Lab Setup & Postman Document Sharing/01-Lab Setup Postman Document Sharing/03-Practice Questions & Answers|Practice Questions & Answers]]
