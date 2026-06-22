---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the benefits of using a self-managed GitLab runner over Docker-in-Docker for building Docker images.**

The benefits of using a self-managed GitLab runner over Docker-in-Docker include:

1. **Improved Performance via Caching**: When using a self-managed runner, Docker images can be cached on the server. This means that subsequent builds can reuse existing layers, significantly reducing build times. For example, in the lecture, the build time was reduced from 8 minutes to 8 seconds due to caching.

2. **Resource Management**: With Docker-in-Docker, each build runs in a new Docker container, leading to a fresh state every time. This can be inefficient and time-consuming. On the other hand, a self-managed runner allows for persistent storage, enabling efficient use of resources and faster builds.

3. **Flexibility**: A self-managed runner provides more control over the build environment. You can customize the runner to meet specific needs, such as installing necessary tools like Docker and AWS CLI.

4. **Cost Efficiency**: Utilizing a self-managed runner can reduce reliance on shared runners, which have usage limits. By managing your own runner, you avoid hitting those limits and can run pipelines more frequently.

**Q2. How would you configure a self-managed GitLab runner to execute Docker commands without requiring sudo?**

To configure a self-managed GitLab runner to execute Docker commands without requiring sudo, follow these steps:

1. **Install Docker**: Ensure Docker is installed on the runner machine. For Ubuntu, you can use the following commands:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io
   ```

2. **Add Users to Docker Group**: Add the necessary users to the Docker group so they can execute Docker commands without sudo. For example, to add the `ubuntu` user and the `gitlab-runner` user:
   ```bash
   sudo usermod -aG docker ubuntu
   sudo usermod -aG docker gitlab-runner
   ```

3. **Restart Services**: Restart the Docker service and the GitLab Runner service to apply the changes:
   ```bash
   sudo systemctl restart docker
   sudo systemctl restart gitlab-runner
   ```

By following these steps, the specified users will be able to run Docker commands without needing sudo privileges.

**Q3. What are the implications of not cleaning up unused Docker images on a self-managed runner?**

Not cleaning up unused Docker images on a self-managed runner can lead to several issues:

1. **Storage Space Exhaustion**: Over time, unused Docker images can consume a significant amount of disk space. As seen in the lecture, the runner had already used up 14 GB out of 20 GB, leading to potential storage exhaustion.

2. **Build Failures**: If the runner runs out of storage space, subsequent builds may fail due to insufficient disk space. This can disrupt the CI/CD pipeline and delay deployments.

3. **Performance Degradation**: Accumulated unused images can slow down the performance of the runner, as it needs to manage a larger number of images.

To mitigate these issues, it is recommended to periodically clean up unused Docker images using commands like:
```bash
docker image prune -a
```
This command removes all unused images, freeing up valuable storage space.

**Q4. How can you troubleshoot and resolve issues when a job is stuck in a pending state on a self-managed GitLab runner?**

When a job is stuck in a pending state on a self-managed GitLab runner, you can troubleshoot and resolve the issue by following these steps:

1. **Check Runner Status**: Verify that the GitLab runner is running correctly. Use the following command to check the status:
   ```bash
   sudo systemctl status gitlab-runner
   ```

2. **Restart the Runner**: If the runner is not running, restart it using:
   ```bash
   sudo systemctl restart gitlab-runner
   ```

3. **Force Job Execution**: If restarting the runner does not resolve the issue, force the runner to check for and execute pending jobs:
   ```bash
   sudo gitlab-runner verify
   ```

4. **Check Logs**: Review the runner logs for any errors or warnings that might indicate the cause of the issue. The logs can typically be found in `/var/log/gitlab-runner/`.

By following these steps, you can identify and resolve the root cause of the pending job issue, ensuring that the runner can continue to execute jobs effectively.

**Q5. What is the significance of using tags in the pipeline configuration for a self-managed GitLab runner?**

Using tags in the pipeline configuration for a self-managed GitLab runner is significant for the following reasons:

1. **Runner Selection**: Tags allow you to specify which runner should execute a particular job. By defining tags in the pipeline configuration, you ensure that the job is executed on the appropriate runner. For example:
   ```yaml
   build_image:
     script: 
       - echo "Building the Docker image"
     tags:
       - self-managed-runner
   ```

2. **Customization**: Tags provide flexibility to customize the execution environment. Different runners can be configured with different tags to handle specific tasks, such as building Docker images or deploying applications.

3. **Resource Management**: Tags help in managing shared resources efficiently. By specifying tags, you can distribute jobs across multiple runners, ensuring optimal resource utilization and avoiding overloading a single runner.

4. **Consistency**: Using tags ensures consistency in the execution environment. Jobs with the same tags will always run on runners with the same configuration, reducing variability and improving reliability.

By leveraging tags, you can effectively manage and control the execution of jobs in your CI/CD pipeline, ensuring that they run on the most suitable runner.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Build Application Images on Self Managed Runner Leverage Docker Caching/13-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Build Application Images on Self Managed Runner Leverage Docker Caching/00-Overview|Overview]]
