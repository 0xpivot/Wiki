---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring a Self-Managed GitLab Runner

### Step 1: SSH into the GitLab Runner Machine

To begin, you need to SSH into the machine where the GitLab Runner will be installed. Assuming the machine is running Ubuntu, you can use the following command:

```bash
ssh ubuntu@<public_ip_address>
```

Replace `<public_ip_address>` with the actual public IP address of your server.

### Step 2: Update System Repositories

Once you are logged in, it's a good practice to update the system repositories to ensure you have the latest package information. Run the following commands:

```bash
sudo apt-get update
sudo apt-get upgrade
```

### Step 3: Install GitLab Runner

Next, you need to install the GitLab Runner software. GitLab provides a script to simplify this process. Run the following command:

```bash
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install gitlab-runner
```

This script adds the GitLab repository and installs the `gitlab-runner` package.

### Step 4: Register the GitLab Runner

After installing the GitLab Runner, you need to register it with your GitLab project. To do this, you need to obtain the registration token and the URL of your GitLab instance. You can find these details in the GitLab UI under the project's CI/CD settings.

#### Obtaining Registration Details

1. Go to your GitLab project.
2. Navigate to **Settings > CI/CD**.
3. Expand the **Runners** section.
4. Click on **Add runner** to get the registration token and URL.

#### Registering the Runner

Use the following command to register the runner:

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.example.com/" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My first runner" \
  --tag-list "ec2,shell" \
  --run-untagged="false"
```

Replace `"https://gitlab.example.com/"` with your GitLab instance URL and `"YOUR_REGISTRATION_TOKEN"` with the actual registration token.

### Step 5: Verify the Runner Configuration

After registering the runner, verify that it is correctly configured and connected to your GitLab project. You can check the status of the runner in the GitLab UI under **Settings > CI/CD > Runners**.

### Step . Creating a Runner Definition

In the GitLab UI, you can define the characteristics of your runner. This includes specifying the operating system, tags, and other attributes.

#### Operating System

Specify the operating system for the runner. In this case, it is Linux.

#### Tags

Tags are labels that help you identify and select specific runners for your pipeline jobs. Common tags might include the type of executor (e.g., `shell`, `docker`), the environment (e.g., `production`, `staging`), or the machine type (e.g., `ec2`).

#### Example Tags

For this setup, we are using the tags `ec2` and `shell`. This means the runner will be used for jobs that require a shell executor and are running on an EC2 instance.

#### Tag Usage in Pipelines

In your `.gitlab-ci.yml` file, you can specify which runner to use for a particular job by referencing the tags. For example:

```yaml
build_job:
  script:
    - echo "Building the application"
  tags:
    - ec2
    - shell
```

### Step 6: Testing the Runner

To ensure that the runner is working correctly, you can create a simple pipeline job that runs a basic command. For example, you can add the following job to your `.gitlab-ci.yml` file:

```yaml
test_runner:
  script:
    - echo "Runner is working!"
  tags:
    - ec2
    - shell
```

Commit this change and push it to your GitLab repository. The pipeline should trigger, and the runner should execute the job.

### Step 7: Advanced Configuration

For more advanced configurations, you can modify the runner's configuration file (`/etc/gitlab-runner/config.toml`). This file contains detailed settings for the runner, including executors, shell commands, and more.

#### Example Configuration File

Here is an example of a `config.toml` file:

```toml
concurrent = 1
check_interval = 0

[[runners]]
  name = "My first runner"
  url = "https://gitlab.example.com/"
  token = "YOUR_REGISTRATION_TOKEN"
  executor = "shell"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
      server_address = ""
      access_key = ""
      secret_key = ""
      bucket_name = ""
      bucket_location = ""
      path_prefix = ""
      shared = false
```

### Step 8: Monitoring and Maintenance

Regularly monitor the runner's performance and logs to ensure it is functioning correctly. You can view the runner's logs by running the following command:

```bash
sudo journalctl -u gitlab-runner
```

### Step 9: Scaling and Load Balancing

If you have multiple runners, you can scale them to handle more concurrent jobs. This can be achieved by adding more runners or configuring load balancing between existing runners.

### Step 10: Security Considerations

#### Vulnerabilities and Risks

Running CI/CD pipelines can expose your infrastructure to various security risks. Some common vulnerabilities include:

- **Unauthorized Access**: If the runner is not properly secured, unauthorized users could gain access to the runner and execute malicious commands.
- **Sensitive Data Exposure**: If sensitive data (such as API keys or credentials) is exposed in the pipeline, it could be intercepted and misused.
- **Malicious Code Execution**: If an attacker gains control of the runner, they could execute arbitrary code, potentially compromising the entire infrastructure.

#### Real-World Examples

- **CVE-2021-22205**: A vulnerability in GitLab CI/CD allowed attackers to bypass authentication and execute arbitrary code on the runner.
- **CVE-2020-10929**: A vulnerability in GitLab CI/CD allowed attackers to inject arbitrary commands into the pipeline, leading to potential code execution.

#### How to Prevent / Defend

##### Detection

- **Monitor Logs**: Regularly review the runner's logs for suspicious activity.
- **Security Tools**: Use security tools like intrusion detection systems (IDS) to monitor for unusual behavior.

##### Prevention

- **Secure Authentication**: Ensure that the runner is properly authenticated and authorized to access the GitLab instance.
- **Environment Variables**: Use environment variables to securely store sensitive data and avoid hardcoding secrets in the pipeline.
- **Least Privilege Principle**: Limit the permissions of the runner to the minimum required for its tasks.

##### Secure Coding Fixes

Compare the vulnerable and secure versions of a pipeline job:

**Vulnerable Version**

```yaml
deploy_job:
  script:
    - echo "Deploying the application"
    - ssh -i ~/.ssh/id_rsa user@server "cd /path/to/app && git pull"
  tags:
    - ec2
    - shell
```

**Secure Version**

```yaml
deploy_job:
  script:
    - echo "Deploying the application"
    - ssh -i $SSH_KEY_PATH user@server "cd /path/to/app && git pull"
  tags:
    - ec2
    - shell
  variables:
    SSH_KEY_PATH: "/path/to/ssh/key"
```

In the secure version, the SSH key path is stored as an environment variable, reducing the risk of exposure.

##### Configuration Hardening

- **Limit Executor Permissions**: Restrict the permissions of the runner's executor to the minimum required for its tasks.
- **Use TLS**: Ensure that communication between the runner and the GitLab server is encrypted using TLS.

### Conclusion

Configuring a self-managed GitLab Runner is a crucial step in setting up a robust CI/CD pipeline. By following the steps outlined above, you can ensure that your runner is properly installed, registered, and configured to handle your pipeline jobs efficiently and securely.

### Practice Labs

For hands-on experience with GitLab Runners, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including CI/CD pipeline security.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security, including CI/CD pipeline security.

These labs provide practical scenarios to test and improve your skills in managing GitLab Runners and securing CI/CD pipelines.

---
<!-- nav -->
[[08-Configuring a Self-Managed GitLab Runner for Pipeline Jobs|Configuring a Self-Managed GitLab Runner for Pipeline Jobs]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/10-Practice Questions & Answers|Practice Questions & Answers]]
