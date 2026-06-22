---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Dockerizing Node.js and MongoDB Development Environment

### Introduction to Dockerizing Applications

Docker is a platform that allows developers to package applications along with their dependencies into lightweight, portable containers. This ensures that the application runs consistently across different environments. In this section, we will focus on setting up a development environment for a Node.js application using MongoDB as the database backend.

### Setting Up MongoDB Container

When working with Docker, it's essential to understand how to configure and run containers for different services. One such service is MongoDB, a popular NoSQL database. To set up MongoDB in a Docker container, we need to ensure that the container is accessible from the host machine and that it is configured correctly.

#### Port Mapping

One of the key aspects of configuring a MongoDB container is port mapping. By default, MongoDB listens on port `27017`. When running MongoDB in a Docker container, we need to map this port from the container to the host machine. This allows the host machine to communicate with the MongoDB instance running inside the container.

```mermaid
graph LR
    A[Host Machine] -- Port 27017 --> B[Docker Container]
    B -- Port 27017 --> C[MongoDB Instance]
```

To achieve this, we use the `-p` flag in the `docker run` command. The syntax is `-p <host-port>:<container-port>`. For example:

```sh
docker run -p 27017:27017 ...
```

This command maps port `27017` on the host machine to port `27017` on the container.

#### Running in Detached Mode

Another important aspect is running the container in detached mode. This means the container runs in the background, allowing you to continue using your terminal. The `-d` flag is used to start the container in detached mode.

```sh
docker run -d ...
```

### Configuring Environmental Variables

MongoDB provides several environmental variables that can be set during container initialization. These variables allow you to customize the behavior of the MongoDB instance. Two commonly used variables are `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`.

#### Setting Root Username and Password

These environmental variables are used to set the root username and password for MongoDB. This is crucial for securing the database and ensuring that only authorized users can access it.

```sh
docker run -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password ...
```

In this example, the root username is set to `admin`, and the root password is set to `password`.

#### Specifying Initial Database

While the initial database can be created later using tools like MongoDB Compass or the MongoDB shell, it's often useful to specify an initial database during container initialization. However, for simplicity, we will only set the root username and password in this example.

### Full Example Command

Combining all the elements discussed, the full command to start a MongoDB container with the specified configurations would look like this:

```sh
docker run -p 27017:27017 -d -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:latest
```

### Complete HTTP Request and Response

While MongoDB does not typically use HTTP for communication, it's important to understand how to interact with MongoDB using the MongoDB shell or other tools. Here is an example of connecting to MongoDB using the MongoDB shell:

```sh
mongo --host localhost --port 27017 -u admin -p password --authenticationDatabase admin
```

### Common Pitfalls and How to Prevent Them

#### Using Default Credentials

Using default credentials (like `admin` and `password`) is a significant security risk. Attackers can easily guess these credentials and gain unauthorized access to the database.

**How to Prevent / Defend:**

1. **Use Strong, Unique Credentials:** Always use strong, unique usernames and passwords. Consider using a password manager to generate and store complex passwords.
   
   ```sh
   docker run -p 27017:27017 -d -e MONGO_INITDB_ROOT_USERNAME=myUniqueUser -e MONGO_INITDB_ROOT_PASSWORD=MyStrongPassword mongo:latest
   ```

2. **Enable Authentication:** Ensure that authentication is enabled for the MongoDB instance. This can be done by setting the appropriate environmental variables.

3. **Regularly Update Credentials:** Regularly update the credentials to reduce the risk of unauthorized access.

### Real-World Examples and Recent Breaches

#### MongoDB Ransomware Attacks

In 2019, there were several high-profile ransomware attacks targeting MongoDB instances. Attackers exploited unsecured MongoDB instances to encrypt data and demand ransom payments. These attacks highlight the importance of securing MongoDB instances and using strong credentials.

**Example:**

- **CVE-2019-10149:** This vulnerability allowed attackers to execute arbitrary code on MongoDB servers. Ensuring that MongoDB is updated to the latest version and using strong credentials can help mitigate such risks.

### Secure Coding Practices

#### Vulnerable Code Example

Here is an example of insecure code that uses default credentials:

```js
const MongoClient = require('mongodb').MongoClient;
const uri = 'mongodb://admin:password@localhost:27017/mydatabase';

MongoClient.connect(uri, function(err, client) {
  if (err) throw err;
  console.log("Connected successfully to server");
});
```

#### Secure Code Example

Here is the corrected version using strong credentials:

```js
const MongoClient = require('mongodb').MongoClient;
const uri = 'mongodb://myUniqueUser:MyStrongPassword@localhost:27017/mydatabase';

MongoClient.connect(uri, function(err, client) {
  if (err) throw err;
  console.log("Connected successfully to server");
});
```

### Hands-On Labs

For practical experience with Dockerizing Node.js and MongoDB, consider the following labs:

- **PortSwigger Web Security Academy:** Offers a variety of labs related to web application security, including Docker and containerization.
- **OWASP Juice Shop:** A deliberately insecure web application for security training. It includes challenges related to Docker and MongoDB.
- **Docker Official Documentation:** Provides detailed tutorials and examples for setting up and managing Docker containers.

By following these steps and best practices, you can effectively set up and secure a MongoDB container for your Node.js application development environment.

---
<!-- nav -->
[[05-Connecting Node.js with MongoDB Using Docker|Connecting Node.js with MongoDB Using Docker]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/17-Dockerizing Node.js and MongoDB Development Environment/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/17-Dockerizing Node.js and MongoDB Development Environment/07-Practice Questions & Answers|Practice Questions & Answers]]
