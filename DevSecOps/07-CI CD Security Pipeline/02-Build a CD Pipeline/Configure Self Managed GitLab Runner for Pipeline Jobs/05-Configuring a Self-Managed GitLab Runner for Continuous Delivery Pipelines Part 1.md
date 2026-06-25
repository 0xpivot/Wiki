---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines

### Introduction

In the realm of DevSecOps, setting up a Continuous Delivery (CD) pipeline is crucial for ensuring that your software is built, tested, and deployed efficiently and securely. One key component of this setup is the GitLab Runner, which executes the pipeline jobs. In this section, we will delve into configuring a self-managed GitLab Runner to ensure that your pipeline runs smoothly and securely.

### Understanding the GitLab Runner

The GitLab Runner is an open-source tool that allows you to run CI/CD jobs for your GitLab projects. It acts as a worker that listens for jobs from the GitLab server and executes them according to the defined configuration. The runner can be installed on various platforms, including Linux, macOS, and Windows.

#### Why Use a Self-Managed GitLab Runner?

Using a self-managed GitLab Runner provides several advantages:

1. **Customization**: You have full control over the environment where your jobs run, allowing you to tailor it to your specific needs.
2. **Performance**: By running the runner on your own infrastructure, you can optimize performance based on your workload.
3. **Security**: You can enforce strict security policies and controls on your runner environment, reducing the risk of unauthorized access.

### Setting Up the GitLab Runner

To configure a self-managed GitLab Runner, follow these steps:

1. **Install the GitLab Runner**:
   - Download the appropriate package for your operating system from the GitLab Runner releases page.
   - Install the package using your system’s package manager or by extracting the binary.

2. **Register the Runner**:
   - Run the `gitlab-runner register` command to start the registration process.
   - Provide the necessary details such as the GitLab server URL, token, and description.
   - Choose the executor type (e.g., shell, docker, kubernetes).

#### Example Registration Command

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.example.com/" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Shell Runner" \
  --tag-list "shell,mytags"
```

### Running the Registration Command with `sudo`

When registering the GitLab Runner, it is recommended to use `sudo` to ensure that the command has the necessary permissions to interact with the GitLab server and configure the runner correctly.

#### Why Use `sudo`?

Using `sudo` ensures that the registration command runs with elevated privileges, which is often required to:

1. **Access System Resources**: The runner may need to access system resources such as network interfaces, storage, and other services.
2. **Write Configuration Files**: The runner writes configuration files to system directories, which typically require root access.
3. **Run Background Services**: The runner daemon needs to run as a background service, which often requires root privileges.

#### Potential Issues Without `sudo`

If you attempt to register the runner without `sudo`, you may encounter issues such as:

1. **Permission Errors**: The command may fail due to insufficient permissions to write to system directories or access certain resources.
2. **Job Execution Failures**: The runner may not be able to execute jobs correctly, leading to crashes or incomplete job executions.

#### Example of Registration Without `sudo`

```bash
gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.example.com/" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Shell Runner" \
  --tag-list "shell,mytags"
```

#### Expected Output

Upon successful registration, you should see a success message indicating that the runner has been registered and is ready to execute jobs.

```plaintext
Running in system mode.

Registering runner... succeeded
Runner registered successfully. Feel free to add it to a project!
```

### Verifying the Runner Registration

Once the runner is registered, you can verify its status through the GitLab web interface.

1. **Navigate to the Runners Page**:
   - Go to your GitLab project settings and navigate to the "CI/CD" section.
   - Click on "Runners" to view the list of registered runners.

2. **Check Runner Status**:
   - Ensure that the runner is listed and has a green icon, indicating that it is online and ready to execute jobs.

#### Example of Runner Details

Inside the runner detail view, you can see additional information such as:

- **IP Address**: The public IP address of the runner.
- **Version**: The version of the GitLab runner installed.

### Ensuring Compatibility with GitLab Runner Version

It is important to ensure that your GitLab Runner version is compatible with the GitLab server version. As mentioned in the transcript, you need to have version 16 or higher to register the runner properly.

#### Checking GitLab Runner Version

You can check the version of your GitLab Runner by running the following command:

```bash
gitlab-runner --version
```

#### Updating GitLab Runner

If your version is outdated, you can update it by downloading the latest package from the GitLab Runner releases page and reinstalling it.

### Handling Common Pitfalls

#### Issue: Runner Crashes During Job Execution

Sometimes, the runner may crash during job execution, leading to incomplete or failed builds. This could be due to various reasons such as resource constraints, misconfigured environments, or bugs in the runner itself.

##### How to Prevent / Defend

1. **Resource Management**:
   - Ensure that the runner has sufficient CPU, memory, and disk space to handle the workload.
   - Monitor resource usage and scale up if necessary.

2. **Environment Configuration**:
   - Verify that the runner environment is correctly configured with all necessary dependencies and tools.
   - Use consistent and reproducible environments (e.g., Docker images) to avoid configuration drift.

3. **Logging and Monitoring**:
   - Enable detailed logging for the runner to capture errors and exceptions.
   - Set up monitoring and alerting to detect and respond to runner failures promptly.

#### Example of Secure Environment Configuration

```yaml
image: node:14

stages:
  - build
  - test
  - deploy

before_script:
  - npm install

build:
  stage: build
  script:
    - npm run build

test:
  stage: test
  script:
    - npm test

deploy:
  stage: deploy
  script:
    - npm run deploy
```

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-22205

CVE-2021-22205 is a critical vulnerability in GitLab that allows attackers to execute arbitrary code on the server. This vulnerability affects versions of GitLab prior to 13.12.7, 14.2.4, and 14.3.0.

##### Impact

An attacker could exploit this vulnerability to gain unauthorized access to the GitLab server and potentially compromise the entire infrastructure, including the runners.

##### How to Prevent / Defend

1. **Keep GitLab Updated**:
   - Regularly update GitLab to the latest version to ensure that you have the latest security patches.
   - Monitor the GitLab security advisories and apply updates promptly.

2. **Use Secure Configurations**:
   - Follow best practices for securing GitLab installations, such as enabling two-factor authentication, restricting access to sensitive repositories, and using secure communication protocols (e.g., HTTPS).

3. **Monitor for Anomalies**:
   - Set up monitoring and alerting to detect unusual activity or signs of compromise.
   - Regularly review logs and audit trails to identify potential security incidents.

### Hands-On Practice

To gain practical experience with configuring a self-managed GitLab Runner, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for learning web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide a controlled environment to practice configuring and managing GitLab Runners for continuous delivery pipelines.

### Conclusion

Configuring a self-managed GitLab Runner is a critical step in setting up a robust and secure continuous delivery pipeline. By following the steps outlined in this chapter, you can ensure that your runner is properly registered, configured, and ready to execute jobs efficiently and securely. Additionally, by being aware of common pitfalls and recent vulnerabilities, you can take proactive measures to defend against potential threats and maintain the integrity of your pipeline.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/04-Introduction to Self-Managed GitLab Runners|Introduction to Self-Managed GitLab Runners]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]] | [[06-Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines|Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines]]
