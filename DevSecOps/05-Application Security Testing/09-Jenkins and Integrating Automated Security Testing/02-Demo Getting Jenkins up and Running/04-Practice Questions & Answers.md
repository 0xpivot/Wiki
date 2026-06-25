---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why is it important to match the Docker group ID in the Jenkins service configuration?**

Matching the Docker group ID in the Jenkins service configuration is crucial because Jenkins needs to interact with Docker to manage containers. If the group IDs do not match, Jenkins may not have the necessary permissions to start, stop, or manage Docker containers, leading to operational issues. This ensures that Jenkins can perform actions such as building and deploying applications within Docker containers without encountering permission errors.

**Q2. How would you create a Docker Compose overwrite file to change the Docker group ID for the Jenkins service?**

To create a Docker Compose overwrite file to change the Docker group ID for the Jenkins service, follow these steps:

1. Create a new file named `docker-compose.override.yml`.
2. Add the following content to the file:

```yaml
version: '3.5'
services:
  jenkins:
    user: "999"
```

Replace `999` with the actual Docker group ID on your system. This file overrides the original `docker-compose.yml` file and sets the `user` parameter for the Jenkins service to the correct Docker group ID.

3. Save the file and use it alongside the original `docker-compose.yml` file to start the services.

**Q3. Explain how to find the initial root password for Jenkins after starting the Docker services.**

To find the initial root password for Jenkins after starting the Docker services, follow these steps:

1. Use the `docker logs` command with the `-f` flag to follow the logs of the Jenkins container. For example:

```bash
docker logs -f jenkins
```

2. Look for the line that displays the initial root password. This password is generated randomly and is required to access Jenkins for the first time.

3. Copy the displayed password and use it to log in to the Jenkins web interface at `http://jenkins.demo.local:8080`.

**Q4. What plugins should be installed in Jenkins for basic Git integration and pipeline support?**

For basic Git integration and pipeline support in Jenkins, the following plugins should be installed:

1. **Git Plugin**: This plugin provides support for cloning and managing Git repositories within Jenkins jobs.
2. **Pipeline Plugin**: This plugin enables the creation and management of Jenkins pipelines, allowing for automation of build, test, and deployment processes.
3. **Pipeline Stage View Plugin**: This plugin provides a visual representation of the stages in a Jenkins pipeline, making it easier to track the progress and status of each stage.

To install these plugins, follow these steps:

1. After logging into Jenkins, click on "Manage Jenkins" in the left-hand menu.
2. Select "Manage Plugins".
3. Go to the "Available" tab and search for the plugins mentioned above.
4. Check the boxes next to the desired plugins and click "Install".

**Q5. How would you configure Jenkins to use a custom admin user during the initial setup?**

To configure Jenkins to use a custom admin user during the initial setup, follow these steps:

1. Log in to Jenkins using the initial root password obtained from the Docker logs.
2. On the initial setup page, click on "Select plugins to install".
3. Choose "None" to deselect all suggested plugins.
4. Click on "Save and Finish".
5. On the next page, create an admin user by filling in the required fields:
   - Username
   - Password (super secure)
   - Full Name
   - Email Address
6. Click on "Save and Finish" to complete the setup.

By creating a custom admin user, you ensure that Jenkins is secured with a known username and password, enhancing the security of the Jenkins instance.

---
<!-- nav -->
[[03-Setting Up Jenkins for DevSecOps|Setting Up Jenkins for DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/03-Demo Getting Jenkins up and Running/00-Overview|Overview]]
