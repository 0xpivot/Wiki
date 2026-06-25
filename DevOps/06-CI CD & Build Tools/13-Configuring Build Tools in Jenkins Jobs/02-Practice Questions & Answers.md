---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how to configure Maven in Jenkins using plugins.**

To configure Maven in Jenkins using plugins, follow these steps:

1. Go to the Jenkins dashboard and navigate to `Manage Jenkins`.
2. Click on `Global Tool Configuration`.
3. Scroll down to the `Maven` section.
4. Click on `Add Maven` and provide a name for the Maven installation.
5. Select the version of Maven you want to use from the dropdown menu.
6. Save the configuration.

By doing this, Jenkins will automatically download and install the specified version of Maven. Once configured, Maven commands will be available in all Jenkins jobs.

**Q2. How would you manually install Node.js and NPM on a Jenkins server running in a Docker container?**

To manually install Node.js and NPM on a Jenkins server running in a Docker container, follow these steps:

1. Identify the container ID of the Jenkins container using `docker ps`.
2. Enter the container as the root user using the command `docker exec -u 0 -it <container_id> /bin/bash`.
3. Check the Linux distribution using `cat /etc/issue`.
4. Update the package list and install curl if it’s not already installed using `apt-get update && apt-get install curl`.
5. Download the Node.js and NPM installation script using `curl -O <script_url>`.
6. Execute the installation script to install Node.js and NPM.
7. Verify the installation by checking the versions of Node.js and NPM using `node -v` and `npm -v`.

After these steps, Node.js and NPM will be available as commands in Jenkins jobs.

**Q3. Why is it important to have administrative privileges when installing tools directly on the Jenkins server?**

It is important to have administrative privileges when installing tools directly on the Jenkins server because:

1. **Permissions**: Installing software typically requires writing to system directories, modifying environment variables, and potentially changing configurations. Administrative privileges ensure that the necessary permissions are available to perform these actions.
2. **Consistency**: Ensuring that all required dependencies and configurations are correctly set up can prevent issues during the build process.
3. **Security**: Running Jenkins as a non-root user is a best practice to reduce security risks. However, administrative privileges are needed to install new tools without compromising the security setup.

For example, in the lecture, the container was entered as a root user (`docker exec -u 0`) to install Node.js and NPM, ensuring that the installation had the necessary permissions to modify the system.

**Q4. What are the advantages and disadvantages of configuring build tools via plugins versus direct installation on the Jenkins server?**

Advantages of configuring build tools via plugins:
- **Ease of Use**: Plugins often simplify the process of setting up and maintaining build tools.
- **Automation**: Plugins can automatically handle updates and version management.
- **Integration**: Plugins are tightly integrated with Jenkins, providing a seamless experience.

Disadvantages of configuring build tools via plugins:
- **Limited Control**: You may have less control over the exact versions and configurations of the tools.
- **Dependency on Plugin Maintenance**: If the plugin is no longer maintained, you might face compatibility issues.

Advantages of direct installation on the Jenkins server:
- **Customization**: Direct installation allows for precise control over the versions and configurations of the tools.
- **Flexibility**: You can tailor the installation to meet specific requirements.

Disadvantages of direct installation on the Jenkins server:
- **Complexity**: Direct installation can be more complex and time-consuming.
- **Maintenance**: You are responsible for updating and maintaining the tools.

**Q5. How would you create a Jenkins job to build a Java Maven application and run its tests?**

To create a Jenkins job to build a Java Maven application and run its tests, follow these steps:

1. **Create a New Job**:
   - Go to the Jenkins dashboard and click `New Item`.
   - Provide a name for the job and select `Freestyle project`. Click `OK`.

2. **Configure Source Code Management**:
   - Under `Source Code Management`, select `Git`.
   - Enter the repository URL and credentials if required.

3. **Configure Build Triggers**:
   - Under `Build Triggers`, select `Poll SCM` and specify a schedule (e.g., `H/5 * * * *` to poll every 5 minutes).

4. **Configure Build Steps**:
   - Under `Build`, click `Add build step` and select `Invoke top-level Maven targets`.
   - In the `Goals` field, enter `clean test package`.

5. **Save and Run the Job**:
   - Click `Save` to save the job configuration.
   - Click `Build Now` to run the job.

This configuration will clean the workspace, run the tests, and package the application into a JAR file.

**Q6. How would you create a Jenkins job to build a Node.js application and push it to a Nexus repository?**

To create a Jenkins job to build a Node.js application and push it to a Nexus repository, follow these steps:

1. **Create a New Job**:
   - Go to the Jenkins dashboard and click `New Item`.
   - Provide a name for the job and select `Freestyle project`. Click `OK`.

2. **Configure Source Code Management**:
   - Under `Source Code Management`, select `Git`.
   - Enter the repository URL and credentials if required.

3. **Configure Build Triggers**:
   - Under `Build Triggers`, select `Poll SCM` and specify a schedule (e.g., `H/5 * * * *` to poll every 5 minutes).

4. **Configure Build Steps**:
   - Under `Build`, click `Add build step` and select `Execute shell`.
   - Enter the following commands:
     ```sh
     npm install
     npm test
     npm pack
     ```
   - To push the package to a Nexus repository, you can use a tool like `npm publish` or a custom script to upload the package to Nexus.

5. **Save and Run the Job**:
   - Click `Save` to save the job configuration.
   - Click `Build Now` to run the job.

This configuration will install dependencies, run tests, package the application, and optionally push it to a Nexus repository.

---
<!-- nav -->
[[01-Configuring Build Tools in Jenkins Jobs|Configuring Build Tools in Jenkins Jobs]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/13-Configuring Build Tools in Jenkins Jobs/00-Overview|Overview]]
