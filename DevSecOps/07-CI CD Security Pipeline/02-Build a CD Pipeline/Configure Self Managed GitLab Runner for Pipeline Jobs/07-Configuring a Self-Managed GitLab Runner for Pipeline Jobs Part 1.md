---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring a Self-Managed GitLab Runner for Pipeline Jobs

### Introduction to GitLab Runners

In the context of Continuous Integration (CI) and Continuous Delivery (CD), GitLab Runners play a crucial role in executing the jobs defined in your CI/CD pipelines. A GitLab Runner is essentially an agent that listens for job requests from the GitLab server and executes them according to the specified configuration. This chapter will guide you through configuring a self-managed GitLab Runner for your pipeline jobs, explaining the concepts, steps, and best practices involved.

### Understanding the Registration Process

When you create a new project runner, you receive a unique token. This token is essential for authorizing the runner to register with the project. The registration process involves copying this token and executing a specific command to register the runner with the GitLab instance.

#### Importance of the Token

The token serves as a secret key that ensures the runner is authenticated and authorized to communicate with the GitLab server. Without this token, the runner would not be able to register successfully, leading to potential security risks and operational failures.

#### Executing the Registration Command

To ensure the registration process runs smoothly, it is recommended to execute the command with `sudo` privileges. This step helps avoid any permission-related issues that might arise during the registration process.

```bash
sudo gitlab-runner register
```

### Configuring the GitLab Instance URL

During the registration process, you will be prompted to provide the GitLab instance URL. This URL specifies the location of your GitLab server where the runner will send job requests.

```plaintext
Enter the GitLab instance URL (for example, https://gitlab.com): https://your.gitlab.instance
```

#### Importance of the URL

The GitLab instance URL is critical because it determines where the runner will send its job requests. Providing the correct URL ensures that the runner communicates with the intended GitLab server, preventing misrouting and potential security issues.

### Naming the Runner

Next, you will be asked to enter a name for the runner. This name should be descriptive and unique to help identify the runner within your GitLab instance.

```plaintext
Enter the description for this runner: My Self-Managed Runner
```

#### Importance of Descriptive Names

Using descriptive names for runners helps in managing and identifying them easily. This is particularly useful when you have multiple runners configured for different environments or purposes.

### Selecting the Executor Type

After naming the runner, you will be prompted to select the executor type. The executor type determines how the jobs will be executed. The available options include:

- **Shell Executor**: Jobs are executed directly on the shell of the server.
- **Docker Executor**: Jobs are executed inside Docker containers.
- **Docker Machine Executor**: Jobs are executed on a dynamically provisioned Docker host.

For this example, we will choose the **Shell Executor**.

```plaintext
Enter the executor: shell
```

#### Shell Executor vs. Docker Executor

- **Shell Executor**: 
  - **Pros**: 
    - Simplicity: No need to manage Docker containers.
    - Performance: Direct execution on the server can be faster.
  - **Cons**: 
    - Limited Isolation: Jobs run directly on the server, which may lead to conflicts if not properly managed.
    - Dependency Management: Requires ensuring all necessary dependencies are installed on the server.

- **Docker Executor**: 
  - **Pros**: 
    - Isolation: Each job runs in its own isolated Docker container.
    - Consistency: Ensures consistent environments across different jobs.
  - **Cons**: 
    - Overhead: Additional overhead due to container management.
    - Resource Usage: Higher resource usage compared to direct execution on the server.

### Completing the Registration

Once you have selected the executor type, the registration process will complete, and the runner will be registered with the GitLab instance.

```plaintext
Runner registered successfully. Feel free to add it to a project!
```

### Verifying the Registration

To verify that the runner has been successfully registered, you can check the GitLab UI. Navigate to your project settings and look for the "Runners" section. You should see the newly registered runner listed there.

### Example Configuration

Here is a complete example of registering a self-managed GitLab Runner with the shell executor:

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://your.gitlab.instance" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Self-Managed Runner" \
  --tag-list "shell"
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect URL**: Providing an incorrect GitLab instance URL can result in the runner failing to register.
2. **Insufficient Permissions**: Running the registration command without `sudo` can lead to permission issues.
3. **Conflicting Executors**: Using the wrong executor type can lead to unexpected behavior and conflicts.

#### Best Practices

1. **Use Descriptive Names**: Ensure runner names are descriptive and unique.
2. **Regular Maintenance**: Regularly update and maintain the runner to ensure it remains secure and functional.
3. **Monitor Logs**: Monitor runner logs to detect and address any issues promptly.

### How to Prevent / Defend

#### Detection

To detect issues with your GitLab Runner, regularly monitor the runner logs and GitLab UI for any anomalies or errors. Tools like GitLab's built-in monitoring and logging features can help in identifying and addressing issues.

#### Prevention

1. **Secure Tokens**: Ensure that registration tokens are kept secure and not exposed publicly.
2. **Regular Updates**: Keep the runner software updated to the latest version to benefit from security patches and improvements.
3. **Isolation**: Use appropriate executors based on your requirements to ensure proper isolation and consistency.

#### Secure Coding Fixes

Compare the insecure and secure versions of the runner configuration:

**Insecure Version:**

```bash
gitlab-runner register \
  --url "https://your.gitlab.instance" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Self-Managed Runner" \
  --tag-list "shell"
```

**Secure Version:**

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://your.gitlab.instance" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Self-Managed Runner" \
  --tag-list "shell"
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the CVE-2021-22205, which affected GitLab runners. This vulnerability allowed attackers to execute arbitrary commands on the runner's host system. Ensuring that your runner is up-to-date and properly configured can help mitigate such risks.

### Hands-On Labs

To practice configuring a self-managed GitLab Runner, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on setting up and securing GitLab runners.
- **OWASP Juice Shop**: Provides a hands-on environment to practice CI/CD pipeline configurations, including GitLab runners.

### Conclusion

Configuring a self-managed GitLab Runner is a fundamental step in setting up a robust CI/CD pipeline. By understanding the registration process, selecting the appropriate executor type, and following best practices, you can ensure that your runners are secure and efficient. Regular maintenance and monitoring are key to keeping your runners in optimal condition.

---
<!-- nav -->
[[06-Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines|Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]] | [[08-Configuring a Self-Managed GitLab Runner for Pipeline Jobs|Configuring a Self-Managed GitLab Runner for Pipeline Jobs]]
