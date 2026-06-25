---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Compose

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, using a single command, you create and start all the services from your configuration. This makes it easier to manage complex applications with multiple services.

### Why Use Docker Compose?

Docker Compose simplifies the process of managing multi-container applications. Instead of manually starting each container and linking them together, you can define all the necessary services in a single `docker-compose.yml` file. This file specifies the images to use, the ports to expose, the volumes to mount, and the environment variables to set. Once defined, you can start all the services with a single command, making development and deployment much more efficient.

### How Docker Compose Works

Docker Compose uses a YAML file to define the services, networks, and volumes required for your application. Here’s a basic structure of a `docker-compose.yml` file:

```yaml
version: '3'
services:
  web:
    image: my-web-app
    ports:
      - "8000:8000"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
```

In this example, two services are defined: `web` and `db`. The `web` service uses the `my-web-app` image and exposes port 8000. The `db` service uses the `postgres` image and sets an environment variable for the database password.

### Installing Docker Compose

To install Docker Compose, follow the official instructions from the Docker documentation. Docker Compose is not a package that can be installed via `yum`, so you need to download the binary manually.

#### Downloading the Docker Compose Binary

The first step is to download the Docker Compose binary. You can do this by executing the following command:

```sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

This command downloads the latest version of Docker Compose and places it in `/usr/local/bin`.

#### Making the Binary Executable

After downloading the binary, you need to make it executable. Execute the following command:

```sh
sudo chmod +x /usr/local/bin/docker-compose
```

This command adds execute permissions to the `docker-compose` binary.

#### Verifying the Installation

To verify that Docker Compose is installed correctly, run the following command:

```sh
docker-compose --version
```

If the installation was successful, this command will display the version of Docker Compose installed.

### Creating a Docker Compose File

Once Docker Compose is installed, you can create a `docker-compose.yml` file to define your application’s services. Here’s an example of a `docker-compose.yml` file:

```yaml
version: '3'
services:
  web:
    image: my-web-app
    ports:
      - "8000:8000"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
```

In this example, two services are defined: `web` and `db`. The `web` service uses the `my-web-app` image and exposes port  8000. The `db` service uses the `postgres` image and sets an environment variable for the database password.

### Configuring Jenkins to Execute Docker Compose Commands

To integrate Docker Compose with Jenkins, you need to configure the Jenkinsfile to execute Docker Compose commands on the EC2 instance. Here’s an example of a Jenkinsfile:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker-compose build'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
```

In this Jenkinsfile, two stages are defined: `Build` and `Deploy`. The `Build` stage builds the Docker images, and the `Deploy` stage starts the containers in detached mode.

### Running Docker Compose Commands

To run Docker Compose commands, you can use the following commands:

```sh
docker-compose build
docker-compose up -d
```

These commands build the Docker images and start the containers in detached mode.

### Example: Deploying a Multi-Container Application

Let’s walk through an example of deploying a multi-container application using Docker Compose and Jenkins.

#### Step 1: Define the Services in `docker-compose.yml`

Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'
services:
  web:
    image: my-web-app
    ports:
      - "8000:8000"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
```

#### Step 2: Configure Jenkinsfile

Create a Jenkinsfile with the following content:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker-compose build'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
```

#### Step 3: Run Jenkins Pipeline

Run the Jenkins pipeline to build and deploy the application.

### Common Pitfalls and Best Practices

When working with Docker Compose and Jenkins, there are several common pitfalls to avoid:

1. **Incorrect Permissions**: Ensure that the Docker Compose binary has the correct execute permissions.
2. **Network Issues**: Make sure that the services can communicate with each other over the network.
3. **Environment Variables**: Set the necessary environment variables for your services.
4. **Resource Management**: Monitor resource usage to ensure that the containers have enough resources to run smoothly.

### How to Prevent / Defend

#### Detection

To detect issues with Docker Compose and Jenkins, you can monitor the logs and status of the containers. Use the following commands to check the status and logs:

```sh
docker-compose ps
docker-compose logs
```

#### Prevention

To prevent issues, follow these best practices:

1. **Use Latest Versions**: Always use the latest versions of Docker Compose and Jenkins.
2. **Secure Configuration**: Securely configure the environment variables and network settings.
3. **Regular Updates**: Regularly update the Docker images and Jenkins plugins.
4. **Automated Testing**: Implement automated testing to catch issues early.

#### Secure Code Fix

Here’s an example of a vulnerable `docker-compose.yml` file and the corresponding secure version:

**Vulnerable Version:**

```yaml
version: '3'
services:
  web:
    image: my-web-app
    ports:
      - "8000:8000"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
```

**Secure Version:**

```yaml
version: '3'
services:
  web:
    image: my-web-app
    ports:
      - "8000:8000"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

In the secure version, the environment variable is set using a placeholder `${POSTGRES_PASSWORD}` to avoid hardcoding sensitive information.

### Real-World Examples

#### Recent CVEs and Breaches

One recent example of a vulnerability related to Docker Compose is the CVE-2021-21316, which affected Docker Compose versions prior to 1.29.2. This vulnerability allowed attackers to execute arbitrary commands on the host system. To mitigate this, ensure that you are using the latest version of Docker Compose.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

### Conclusion

Docker Compose is a powerful tool for managing multi-container applications. By following the steps outlined in this chapter, you can effectively install and use Docker Compose, integrate it with Jenkins, and deploy your applications securely. Remember to follow best practices and regularly update your configurations to stay secure.

---
<!-- nav -->
[[03-Introduction to Docker Compose and Its Role in DevOps|Introduction to Docker Compose and Its Role in DevOps]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/19-Docker Compose Deployment On Remote Servers With Jenkins/00-Overview|Overview]] | [[05-Passing Parameters to Shell Scripts in Jenkins|Passing Parameters to Shell Scripts in Jenkins]]
