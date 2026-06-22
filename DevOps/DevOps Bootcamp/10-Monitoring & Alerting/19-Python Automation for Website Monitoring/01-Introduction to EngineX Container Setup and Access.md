---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to EngineX Container Setup and Access

In this section, we will delve into the process of setting up an EngineX container using Docker, accessing it via both IP address and DNS, and writing a Python script to automate the monitoring of the EngineX application. This comprehensive guide will cover the theoretical background, practical steps, potential pitfalls, and security considerations involved in these processes.

### Setting Up the EngineX Container Using Docker

Docker is a platform that allows developers to package applications into containers—standardized executable packages that contain software and all its dependencies. Containers ensure that applications run consistently across different environments.

#### Step-by-Step Guide to Running EngineX Container

To set up an EngineX container, follow these steps:

1. **Install Docker**: Ensure Docker is installed on your system. You can download it from the official Docker website.

2. **Run the EngineX Container**:
    - Use the `docker run` command to start the container in the background.
    - Map the host port 8080 to the container's port 8080.
    - Specify the EngineX image name.

Here is the complete command:

```bash
docker run -d -p 8080:80 engine-x-image-name
```

- `-d`: Run the container in detached mode (background).
- `-p 8080:80`: Map port 8080 on the host to port 80 on the container.
- `engine-x-image-name`: The name of the Docker image for EngineX.

#### Explanation of the Command

- **Docker Image**: An image is a lightweight, standalone, executable package that includes everything needed to run a piece of software, including the code, runtime, libraries, environment variables, and configuration files.
- **Container**: A container is a standard unit of software that packages up code and all its dependencies so the application runs quickly and reliably from one computing environment to another.
- **Port Mapping**: The `-p` flag maps the host's port 8080 to the container's port 80. This allows external systems to communicate with the EngineX application running inside the container.

### Accessing the EngineX Application

Once the EngineX container is running, you can access the application using either the server's public IP address or its DNS name.

#### Accessing via Public IP Address

To access the EngineX application via the public IP address:

1. **Identify the Public IP Address**: Find the public IP address of the server where the EngineX container is running.
2. **Access the Application**: Use a web browser or a command-line tool like `curl` to access the application.

Example using `curl`:

```bash
curl http://<public-ip-address>:8080
```

Replace `<public-ip-address>` with the actual IP address of the server.

#### Accessing via DNS Name

Alternatively, you can access the EngineX application using its DNS name:

1. **Identify the DNS Name**: Obtain the DNS name associated with the server.
2. **Access the Application**: Use a web browser or a command-line tool like `curl`.

Example using `curl`:

```bash
curl http://<dns-name>:8080
```

Replace `<dns-name>` with the actual DNS name of the server.

### Full HTTP Request and Response Example

Let's look at a complete HTTP request and response when accessing the EngineX application via the DNS name.

#### HTTP Request

```http
GET / HTTP/1.1
Host: <dns-name>
User-Agent: curl/7.64.1
Accept: */*
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: EngineX
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Welcome to EngineX</title>
</head>
<body>
    <h1>Welcome to EngineX</h1>
    <p>This is the welcome page for the EngineX application.</p>
</body>
</html>
```

### Explanation of HTTP Headers

- **Host**: Specifies the domain name of the server being accessed.
- **User-Agent**: Identifies the client making the request (in this case, `curl`).
- **Accept**: Indicates the types of content the client can accept.
- **Date**: The date and time the response was generated.
- **Server**: The server software handling the request.
- **Content-Type**: The MIME type of the content being returned.
- **Content-Length**: The size of the response body in bytes.

### Writing a Python Script to Monitor the EngineX Application

Now that we have the EngineX application up and running, let's write a Python script to monitor it.

#### Creating the Python Script

1. **Open PyCharm Editor**: Open PyCharm and create a new file named `monitor_website.py`.
2. **Write the Script**: Use the `requests` library to send an HTTP GET request to the EngineX application.

Here is the complete Python script:

```python
import requests

def monitor_engine_x():
    url = "http://<dns-name>:8080"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("EngineX is up and running.")
        else:
            print(f"EngineX returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    monitor_engine_x()
```

Replace `<dns-name>` with the actual DNS name of the server.

### Explanation of the Python Script

- **Importing Requests Library**: The `requests` library simplifies HTTP requests in Python.
- **Defining the URL**: The URL points to the EngineX application.
- **Sending the GET Request**: The `requests.get()` function sends an HTTP GET request to the specified URL.
- **Checking the Response**: The script checks the HTTP status code to determine if the application is running correctly.
- **Handling Exceptions**: The script handles exceptions that may occur during the request.

### Potential Pitfalls and How to Prevent Them

#### Common Pitfalls

1. **Incorrect URL**: Ensure the URL is correct, including the port number.
2. **Network Issues**: Check network connectivity between the client and the server.
3. **Firewall Rules**: Ensure firewall rules allow traffic on the specified port.
4. **DNS Resolution**: Verify DNS resolution is working correctly.

#### How to Prevent These Issues

1. **Validate URLs**: Double-check the URL and port number.
2. **Check Network Connectivity**: Use tools like `ping` and `traceroute` to verify network connectivity.
3. **Review Firewall Rules**: Ensure firewall rules permit traffic on the required ports.
4. **Test DNS Resolution**: Use tools like `nslookup` or `dig` to test DNS resolution.

### Security Considerations

#### Vulnerabilities and Risks

1. **Cross-Site Scripting (XSS)**: Ensure the EngineX application is protected against XSS attacks.
2. **SQL Injection**: Protect against SQL injection vulnerabilities.
3. **Authentication Bypass**: Ensure proper authentication mechanisms are in place.

#### Real-World Examples

- **CVE-2021-21972**: A vulnerability in Apache Struts allowed remote code execution.
- **CVE-2021-40500**: A vulnerability in Jenkins allowed unauthorized access to sensitive information.

#### Secure Coding Practices

1. **Input Validation**: Validate all user inputs to prevent injection attacks.
2. **Use HTTPS**: Ensure all communication is encrypted using HTTPS.
3. **Regular Updates**: Keep the EngineX application and all dependencies up to date.

### Complete Secure Code Example

#### Vulnerable Code

```python
import requests

def monitor_engine_x():
    url = f"http://{input('Enter DNS name:')}:{input('Enter port:')}"
    response = requests.get(url)
    print(response.text)

if __name__ == "__main__":
    monitor_engine_x()
```

#### Secure Code

```python
import requests

def monitor_engine_x(dns_name, port):
    url = f"https://{dns_name}:{port}"
    try:
        response = requests.get(url, verify=True)
        if response.status_code == 200:
            print("EngineX is up and running.")
        else:
            print(f"EngineX returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    dns_name = input("Enter DNS name: ")
    port = input("Enter port: ")
    monitor_engine_x(dns_name, port)
```

### Conclusion

This comprehensive guide covered the setup and access of an EngineX container using Docker, the creation of a Python script to monitor the application, and the security considerations involved. By following these steps and best practices, you can ensure the reliable and secure operation of your EngineX application.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers extensive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in setting up and securing web applications, which complements the theoretical knowledge gained from this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/19-Python Automation for Website Monitoring/00-Overview|Overview]] | [[02-Introduction to Linode and Virtual Servers|Introduction to Linode and Virtual Servers]]
