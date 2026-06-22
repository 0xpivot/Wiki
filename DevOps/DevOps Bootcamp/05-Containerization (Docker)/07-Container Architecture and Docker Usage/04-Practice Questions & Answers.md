---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the difference between a Docker image and a Docker container.**

A Docker image is a lightweight, standalone, executable package that includes everything needed to run a piece of software, including the code, a runtime, libraries, environment variables, and config files. An image becomes a container when it is instantiated and runs in a Docker environment. The container is the runtime instance of the image—it’s what’s created when you tell Docker to run an image. Containers share the host system kernel and thus are more lightweight than virtual machines.

**Q2. How does Docker ensure efficient downloading of images by utilizing layers?**

Docker images are built in layers, which allows for efficient downloading and updating. When a new version of an image is pulled, Docker only downloads the layers that have changed since the last version. For example, if you have an image with multiple layers and you update the application layer, Docker will only download the updated application layer, not the entire image. This significantly reduces download times and storage requirements. 

**Q3. How would you run two different versions of PostgreSQL on your local machine using Docker?**

To run two different versions of PostgreSQL on your local machine using Docker, you would pull and run the desired versions of the PostgreSQL Docker image. Here is an example:

```bash
# Pull and run PostgreSQL version 9.6
docker run --name postgresql96 -e POSTGRES_PASSWORD=mysecretpassword -d postgres:9.6

# Pull and run PostgreSQL version 10.10
docker run --name postgresql1010 -e POSTGRES_PASSWORD=mysecretpassword -d postgres:10.10
```

In this example, `--name` assigns a name to the container, `-e` sets environment variables, and `-d` runs the container in detached mode. You can verify that both versions are running by using the `docker ps` command.

**Q4. Why is it important for base images to be small in size?**

Base images being small in size is crucial for several reasons:

1. **Efficiency**: Smaller images mean faster downloads and quicker startup times for containers. This is particularly important in CI/CD pipelines where speed is critical.
   
2. **Resource Utilization**: Smaller images consume fewer resources on the host machine, allowing for more efficient use of hardware.

3. **Security**: Smaller images tend to have fewer vulnerabilities because they contain fewer components that could be exploited. Alpine Linux, for example, is often used as a base image due to its minimal footprint and security benefits.

**Q5. What recent real-world examples highlight the importance of container security?**

One notable example is the Log4j vulnerability (CVE-2021-44228), which affected many Java-based applications and services, including those running in containerized environments. This vulnerability demonstrated the importance of keeping container images and their dependencies up-to-date and secure. Organizations had to quickly patch their container images and ensure that the underlying operating systems and libraries were not vulnerable to such exploits.

Another example is the widespread use of unsecured Docker daemons, which led to several high-profile breaches. In 2017, a misconfigured Docker daemon allowed attackers to deploy cryptocurrency mining software on thousands of servers, highlighting the need for proper security configurations and monitoring of container environments.

---
<!-- nav -->
[[03-Container Architecture and Docker Usage|Container Architecture and Docker Usage]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/07-Container Architecture and Docker Usage/00-Overview|Overview]]
