---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to SSH Key Pair Creation for Jenkins Integration

In this section, we will delve into the process of creating an SSH key pair for Jenkins integration. This is a crucial step in automating your CI/CD pipeline, especially when working with Docker and Docker Compose. We'll cover the theoretical background, practical steps, and security considerations involved in setting up SSH keys for Jenkins.

### Background Theory

SSH (Secure Shell) is a cryptographic network protocol for operating network services securely over an unsecured network. It provides a secure channel over an insecure network in a client-server architecture, connecting an SSH client application with an SSH server. Common applications include remote command-line login, remote command execution, and file transfer.

An SSH key pair consists of a public key and a private key. The public key is stored on the server and the private key is kept on the client machine. When a connection is established, the server uses the public key to encrypt data, which can only be decrypted by the corresponding private key.

### Why Use SSH Keys?

Using SSH keys for authentication is more secure than using passwords. Passwords can be guessed or brute-forced, whereas SSH keys provide a much stronger form of authentication. Additionally, SSH keys allow for automated processes, such as Jenkins jobs, to authenticate without requiring manual intervention.

### Steps to Create SSH Key Pair

Let's go through the steps to create an SSH key pair and integrate it with Jenkins.

#### Step 1: Generate SSH Key Pair

To generate an SSH key pair, you can use the `ssh-keygen` command. Here’s how to do it:

```sh
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

This command generates an RSA key pair with a bit length of 4096 bits. The `-C` option adds a comment to the key, typically your email address.

The output will look something like this:

```
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/user/.ssh/id_rsa.
Your public key has been saved in /home/user/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_email@example.com
The key's randomart image is:
+---[RSA 4096]----+
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
+----[SHA256]-----+
```

#### Step 2: Add Public Key to Jenkins

Once you have generated the SSH key pair, you need to add the public key to Jenkins. This can be done via the Jenkins UI or by configuring the Jenkins job directly.

##### Adding Public Key via Jenkins UI

1. Log in to Jenkins.
2. Go to `Manage Jenkins` > `Configure System`.
3. Scroll down to the `Global Properties` section.
4. Click on `Add` and select `Environment Variables`.
5. Set the name to `SSH_PUBLIC_KEY` and the value to the contents of your `id_rsa.pub` file.

##### Adding Public Key via Jenkins Job Configuration

Alternatively, you can configure the SSH key directly in the Jenkins job:

1. Go to the Jenkins job configuration page.
2. Under `Build Environment`, check `Inject environment variables to the build process`.
3. Add a new variable with the name `SSH_PUBLIC_KEY` and the value of your `id_rsa.pub` file.

### Integrating SSH Keys with Docker and Docker Compose

Now that we have the SSH keys set up, let's integrate them with Docker and Docker Compose.

#### Installing Docker Compose

Docker Compose is a tool for defining and running multi-container Docker applications. To install Docker Compose, follow these steps:

1. Download the Docker Compose binary using `curl`:

    ```sh
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    ```

2. Make the binary executable:

    ```sh
    sudo chmod +x /usr/local/bin/docker-compose
    ```

3. Verify the installation:

    ```sh
    docker-compose --version
    ```

#### Using SSH Keys with Docker Compose

To use SSH keys with Docker Compose, you need to ensure that the SSH agent is running and the private key is added to the agent.

1. Start the SSH agent:

    ```sh
    eval "$(ssh-agent -s)"
    ```

2. Add your private key to the SSH agent:

    ```sh
    ssh-add ~/.ssh/id_rsa
    ```

3. Configure Docker Compose to use the SSH keys. You can do this by setting environment variables in your `docker-compose.yml` file:

    ```yaml
    version: '3'
    services:
      app:
        image: myapp:latest
        environment:
          - SSH_AUTH_SOCK=/tmp/ssh_auth_sock
    volumes:
      - ~/.ssh:/root/.ssh
      - /tmp/ssh_auth_sock:/tmp/ssh_auth_sock
    ```

### Example: Full Setup with SSH Keys and Docker Compose

Let's walk through a complete example of setting up SSH keys and Docker Compose in a Jenkins job.

#### Jenkins Job Configuration

1. **Job Definition**:

    ```yaml
    pipeline {
        agent any
        stages {
            stage('Setup') {
                steps {
                    sh 'eval $(ssh-agent -s)'
                    sh 'ssh-add ~/.ssh/id_rsa'
                }
            }
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

2. **SSH Key Management**:

    Ensure that the SSH keys are properly managed and secured. Store the private key securely and never commit it to version control.

#### Security Considerations

Using SSH keys for authentication is generally more secure than using passwords, but it is not foolproof. Here are some security considerations:

1. **Key Storage**: Ensure that the private key is stored securely. Use strong passphrases and store the keys in a secure location.
2. **Access Control**: Limit access to the SSH keys. Only authorized users should have access to the private key.
3. **Monitoring**: Monitor SSH connections and log any suspicious activity.
4. **Regular Audits**: Regularly audit SSH configurations and keys to ensure they are up-to-date and secure.

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Regularly review SSH logs to detect any unauthorized access attempts.
2. **Monitoring Tools**: Use monitoring tools like `fail2ban` to automatically block IP addresses that exhibit suspicious behavior.

#### Prevention

1. **Strong Passphrases**: Use strong passphrases for your SSH keys.
2. **Key Rotation**: Rotate SSH keys regularly to minimize the risk of compromise.
3. **Access Control**: Implement strict access controls and limit the number of users who have access to the private key.

#### Secure Coding Fixes

Here is an example of a vulnerable setup and a secure setup:

**Vulnerable Setup**:

```yaml
version: '3'
services:
  app:
    image: myapp:latest
    environment:
      - SSH_AUTH_SOCK=/tmp/ssh_auth_sock
volumes:
  - ~/.ssh:/root/.ssh
  - /tmp/ssh_auth_sock:/tmp/ssh_auth_sock
```

**Secure Setup**:

```yaml
version: '3'
services:
  app:
    image: myapp:latest
    environment:
      - SSH_AUTH_SOCK=/tmp/ssh_auth_sock
volumes:
  - ~/.ssh:/root/.ssh
  - /tmp/ssh_auth_sock:/tmp/ssh_auth_sock
```

In the secure setup, ensure that the SSH keys are stored securely and that access is limited to authorized users.

### Conclusion

Creating and integrating SSH keys with Jenkins and Docker Compose is a critical step in securing your CI/CD pipeline. By following the steps outlined above, you can ensure that your setup is both functional and secure. Always remember to monitor and audit your SSH configurations regularly to maintain the highest level of security.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to SSH and CI/CD pipelines.
- **OWASP Juice Shop**: Provides a web application with numerous vulnerabilities, including SSH-related ones.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for security testing purposes.

These labs will help you gain practical experience in setting up and securing SSH keys in a CI/CD environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/17-Creating SSH Key Pair for Jenkins Integration/00-Overview|Overview]] | [[02-Introduction to SSH Key Pair for Jenkins Integration|Introduction to SSH Key Pair for Jenkins Integration]]
