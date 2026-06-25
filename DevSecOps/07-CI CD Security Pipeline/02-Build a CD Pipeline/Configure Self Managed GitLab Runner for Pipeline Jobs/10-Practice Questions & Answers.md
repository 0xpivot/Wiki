---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between using shared runners and self-managed runners in GitLab.**

Self-managed runners provide greater control and security compared to shared runners. Shared runners are managed by GitLab and are available to all users, which means they are public servers and lack the privacy and security needed for sensitive operations. On the other hand, self-managed runners are hosted on your own infrastructure, allowing you to control the environment and ensure that sensitive data remains within your private network. This setup is particularly beneficial for organizations with high security standards.

**Q2. How do you configure an EC2 instance to act as a self-managed GitLab runner?**

To configure an EC2 instance as a self-managed GitLab runner, follow these steps:

1. **Launch an EC2 Instance**: Choose an appropriate instance type (e.g., t3.large) and install an operating system (e.g., Ubuntu).
2. **Configure Storage**: Allocate sufficient storage (e.g., 20 GB) to handle the build process, especially for Docker images.
3. **SSH Access**: Set up SSH access using a key pair for secure communication.
4. **Install GitLab Runner**: Use the following commands to install GitLab Runner on the EC2 instance:
    ```bash
    curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
    sudo apt-get install gitlab-runner
    ```
5. **Register the Runner**: Register the runner with your GitLab project using the registration token provided in the GitLab interface:
    ```bash
    sudo gitlab-runner register --non-interactive \
      --url "https://gitlab.com/" \
      --registration-token "your_registration_token" \
      --executor "shell" \
      --description "My EC2 Runner" \
      --tag-list "ec2,shell"
    ```

**Q3. Why is it important to use a larger instance type and sufficient storage for the EC2 runner?**

Using a larger instance type ensures that the runner has enough resources (CPU and memory) to handle resource-intensive tasks such as Docker image building. Insufficient resources can lead to job failures due to timeouts or resource exhaustion. Sufficient storage is crucial because the build process often requires more temporary space than the final image size, especially when installing dependencies like Node.js modules. Without adequate storage, the build process might fail due to insufficient disk space.

**Q4. How can you leverage AWS roles to enhance security when using a self-managed GitLab runner?**

By assigning an AWS role to the EC2 instance acting as a GitLab runner, you can enable the runner to authenticate with AWS services without needing to store AWS credentials directly on the runner. This approach follows the principle of least privilege and reduces the risk of credential exposure. The AWS role can be configured to have specific permissions to access required services, ensuring that the runner can perform necessary actions while maintaining strict security controls.

**Q5. What are the benefits of using a shell executor over a Docker executor in a self-managed GitLab runner?**

The shell executor runs jobs directly on the server's shell, whereas the Docker executor creates a new Docker container for each job. Benefits of using a shell executor include:

- **Resource Efficiency**: No overhead of container creation and management.
- **Persistent State**: Jobs can share state across executions, which can be useful for certain workflows.
- **Simplified Configuration**: Easier to configure and maintain compared to managing Docker containers.

However, the choice depends on the specific needs of your pipeline. For example, if isolation between jobs is critical, a Docker executor might be more suitable.

**Q6. How do you ensure that the self-managed GitLab runner is properly registered and operational?**

To ensure the self-managed GitLab runner is properly registered and operational:

1. **Check Registration**: Verify the registration token and URL are correctly entered during the `gitlab-runner register` command.
2. **Runner Status**: Check the runner status in the GitLab UI under the project’s CI/CD settings. A green icon indicates the runner is online and ready to execute jobs.
3. **Test Execution**: Run a simple pipeline job to confirm the runner is functioning correctly. Monitor the job logs for any errors or warnings.

**Q7. What recent real-world examples highlight the importance of using self-managed runners for security?**

Recent breaches and vulnerabilities, such as the Log4j vulnerability (CVE-2021-44228), underscore the importance of controlling the environment where sensitive operations are performed. Using self-managed runners allows organizations to apply strict security measures and monitor activities closely, reducing the risk of exposure to vulnerabilities present in shared environments.

---
<!-- nav -->
[[09-Configuring a Self-Managed GitLab Runner|Configuring a Self-Managed GitLab Runner]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]]
