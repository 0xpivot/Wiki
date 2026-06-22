---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Basics: Containers and Images

### What is Docker?

Docker is a platform that allows developers to package their applications into lightweight, portable containers. These containers can run consistently across different environments, whether it's a local development machine, a testing server, or a production environment. Docker simplifies the process of deploying and managing applications by providing a consistent and isolated environment for them to run in.

### Containers vs. Images

One of the most fundamental concepts in Docker is the distinction between containers and images. Understanding these concepts is crucial for effectively using Docker.

#### Container

A container is a runtime instance of an image. It is the actual running environment where your application executes. Containers are lightweight and isolated processes that share the host operating system's kernel but have their own isolated user space.

**What is a Container?**

- **Running Environment**: A container is the environment where your application runs. It includes the necessary resources such as the file system, environment variables, and network interfaces.
- **Isolation**: Containers provide isolation from the host system and other containers. This means that changes made within one container do not affect others.
- **Virtual File System**: Containers use a virtual file system that is separate from the host system. This ensures that the container's file system remains isolated and does not interfere with the host's file system.
- **Ports**: Containers can expose ports to communicate with the outside world. This allows your application to receive incoming connections and send outgoing data.

**Why Containers Matter?**

Containers offer several benefits:

- **Consistency**: Containers ensure that your application runs consistently across different environments. This reduces the "works on my machine" problem.
- **Portability**: Containers can be easily moved between different systems, making deployment and scaling easier.
- **Resource Efficiency**: Containers are more resource-efficient than traditional virtual machines because they share the host OS kernel.

**How Containers Work Under the Hood?**

Containers rely on Linux namespaces and control groups (cgroups):

- **Namespaces**: Namespaces provide isolation by creating separate views of the system for each container. This includes namespaces for the process ID, network, mount points, and more.
- **Control Groups (cgroups)**: cgroups limit, account for, and isolate the resource usage (CPU, memory, disk I/O, etc.) of a set of processes.

**Example: Running a Container**

To illustrate, let's consider a simple example of running a container using Docker:

```bash
docker run -d --name my-postgres postgres:latest
```

This command pulls the `postgres` image and starts a container named `my-postgres`. The `-d` flag runs the container in detached mode, meaning it runs in the background.

**Full HTTP Request and Response Example**

When you run a container, Docker communicates with the Docker daemon via HTTP requests. Here’s an example of the HTTP request and response:

```http
POST /v1.41/containers/create HTTP/1.1
Host: localhost:2375
Content-Type: application/json
Content-Length: 116

{
    "Image": "postgres:latest",
    "Name": "my-postgres"
}
```

Response:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Length: 116

{
    "Id": "abc123def456ghi789jkl012mno345pqr678stu901vwxyz",
    "Warnings": null
}
```

#### Image

An image is a read-only template that contains the instructions needed to build a container. It is essentially a snapshot of the application's environment at a specific point in time.

**What is an Image?**

- **Template**: An image is a template that defines the environment in which your application will run. It includes the base operating system, libraries, dependencies, and configurations.
- **Layers**: Docker images are built using layers. Each layer represents a change to the image, such as adding a new file or modifying an existing one.
- **Immutable**: Once an image is created, it cannot be modified. Any changes require building a new image.

**Why Images Matter?**

Images are essential because they:

- **Ensure Consistency**: By defining the exact environment, images ensure that your application runs consistently across different systems.
- **Enable Version Control**: You can create different versions of your image, allowing you to track changes and roll back to previous versions if needed.
- **Facilitate Sharing**: Images can be shared and distributed easily, making it simple to deploy applications across different environments.

**How Images Work Under the Hood?**

Images are stored in a registry and are composed of layers:

- **Layered Architecture**: Each layer in an image is a filesystem diff. This allows Docker to efficiently store and transfer images.
- **Union Filesystem**: Docker uses a union filesystem to combine the layers into a single, cohesive file system for the container.

**Example: Building an Image**

Let's consider a simple example of building an image using a Dockerfile:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```

To build the image, you would run:

```bash
docker build -t my-python-app .
```

**Full HTTP Request and Response Example**

Building an image involves sending a request to the Docker daemon:

```http
POST /v1.41/build HTTP/1.1
Host: localhost:2375
Content-Type: multipart/form-data; boundary=------------------------1234567890abcdef

--------------------------1234567890abcdef
Content-Disposition: form-data; name="context"

.
--------------------------123456789
Content-Disposition: form-data; name="Dockerfile"

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
--------------------------1234567890abcdef--
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "stream": "Step 1/7 : FROM python:3.9-slim\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Step 2/7 : WORKDIR /app\n",
    "stream": " ---> Using cache\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Step 3/7 : COPY . /app\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Step 4/7 : RUN pip install --no-cache-dir -r requirements.txt\n",
    "stream": " ---> Running in 1234567890abcdef\n",
    "stream": "Collecting Flask==2.0.1\n",
    "stream": "  Downloading Flask-2.0.1-py3-none-any.whl (94 kB)\n",
    "stream": "Collecting Jinja2>=3.0\n",
    "stream": "  Downloading Jinja2-3.0.3-py3-none-any.whl (133 kB)\n",
    "stream": "Collecting Werkzeug>=2.0\n",
    "stream": "  Downloading Werkzeug-2.0.3-py3-none-any.whl (327 kB)\n",
    "stream": "Installing collected packages: Jinja2, Werkzeug, Flask\n",
    "stream": "Successfully installed Flask-2.0.1 Jinja2-3.0.3 Werkzeug-2.0.3\n",
    "stream": "Removing intermediate container 1234567890abcdef\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Step 5/7 : EXPOSE 80\n",
    "stream": " ---> Running in 1234567890abcdef\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Step 6/7 : ENV NAME World\n",
    "stream": " ---> Running in 1234567890abcdef\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Step 7/7 : CMD [\"python\", \"app.py\"]\n",
    "stream": " ---> Running in 1234567890abcdef\n",
    "stream": " ---> 1234567890abcdef\n",
    "stream": "Successfully built 1234567890abcdef\n",
    "stream": "Successfully tagged my-python-app:latest\n"
}
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Confusing Containers and Images

Many beginners confuse containers and images. Remember that an image is a template, while a container is the running instance of that template.

**How to Prevent:**

- **Understand the Difference**: Always keep in mind that an image is static and immutable, while a container is dynamic and can be modified.
- **Use Clear Naming Conventions**: Use clear and descriptive names for both images and containers to avoid confusion.

#### Pitfall: Inconsistent Environments

Inconsistent environments can lead to issues where your application works in one environment but fails in another.

**How to Prevent:**

- **Use Dockerfiles**: Define your application's environment in a Dockerfile to ensure consistency.
- **Version Control**: Use version control for your Dockerfiles and images to track changes and roll back if needed.

#### Pitfall: Resource Overuse

Containers can consume more resources than intended, leading to performance issues.

**How to Prevent:**

- **Limit Resources**: Use Docker's resource limits to control CPU and memory usage.
- **Monitor Usage**: Regularly monitor container resource usage to identify and address overuse.

### Real-World Examples

#### Example: CVE-2021-21366

CVE-2021-21366 is a vulnerability in Docker that allows attackers to escalate privileges and execute arbitrary code. This vulnerability highlights the importance of keeping Docker and its components up to date.

**How to Prevent:**

- **Keep Updated**: Regularly update Docker and its components to the latest versions.
- **Use Secure Configurations**: Follow best practices for securing Docker configurations.

#### Example: Docker Hub Breach

In 2021, Docker Hub experienced a breach that exposed user credentials. This incident underscores the importance of securing your Docker environment.

**How to Prevent:**

- **Use Strong Authentication**: Implement strong authentication mechanisms for accessing Docker Hub.
- **Monitor Access**: Regularly monitor access logs to detect and respond to unauthorized access attempts.

### Conclusion

Understanding the difference between containers and images is crucial for effectively using Docker. Containers provide a consistent and isolated environment for your applications, while images define the environment in which your application will run. By following best practices and being aware of common pitfalls, you can ensure that your Docker environment is secure and efficient.

### Practice Labs

For hands-on practice with Docker basics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover Docker basics and security.
- **OWASP Juice Shop**: Provides a web application that can be deployed using Docker, allowing you to practice container management.
- **DVWA (Damn Vulnerable Web Application)**: Another web application that can be deployed using Docker, offering a practical way to learn about containerization.

By completing these labs, you can gain practical experience with Docker and reinforce your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[02-Introduction to Docker Basics Commands and Concepts|Introduction to Docker Basics Commands and Concepts]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/04-Docker Basics Commands And Concepts/00-Overview|Overview]] | [[04-Introduction to Docker Basics Containers, Images, and Actions|Introduction to Docker Basics Containers, Images, and Actions]]
