---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Secure Shell (SSH)

Secure Shell (SSH) is a cryptographic network protocol used for secure communication between a client and a server. It provides a secure channel over an unsecured network, enabling users to log into remote machines, execute commands on a remote machine, and transfer files from one machine to another. SSH is widely used in the DevOps community due to its robust security features and flexibility.

### What is SSH?

SSH stands for Secure Shell. It is a protocol that allows users to securely access and manage remote systems over an insecure network. SSH uses strong encryption to protect the confidentiality and integrity of data transmitted between the client and the server. This ensures that sensitive information such as passwords and commands are not intercepted or tampered with during transmission.

#### Why Secure?

The primary reason for using SSH is to ensure secure communication. When accessing a remote server over the internet, it is crucial to establish a secure connection to prevent unauthorized access and potential attacks. SSH provides several layers of security:

1. **Encryption**: Data transmitted over SSH is encrypted using strong cryptographic algorithms, ensuring that even if the data is intercepted, it cannot be read by unauthorized parties.
2. **Authentication**: SSH supports various authentication methods to verify the identity of the user attempting to access the remote system. This prevents unauthorized access and ensures that only authorized users can perform actions on the remote server.
3. **Integrity**: SSH ensures the integrity of the data being transmitted by using cryptographic hashes to detect any tampering or modification of the data during transmission.

### Use Cases for SSH

SSH is used in various scenarios, including:

1. **Remote Access**: SSH allows users to remotely access and manage servers located in different geographical locations. This is particularly useful for managing servers in data centers or cloud environments.
2. **File Transfer**: SSH supports secure file transfer protocols such as SCP (Secure Copy) and SFTP (Secure File Transfer Protocol), allowing users to securely transfer files between local and remote systems.
3. **Automation**: SSH can be used to automate tasks on remote systems, such as deploying applications, running scripts, and performing administrative tasks.

### Example Scenario

Consider a scenario where you have written a shell script and want to copy it to another server to execute it there. Alternatively, you might want to copy the script to multiple servers simultaneously. Another common use case is configuring a new server and accessing it to install different software and run your application. The server may be physically located in a different location, possibly in another country. SSH provides a secure and efficient way to accomplish these tasks.

### SSH Authentication Methods

There are two primary methods of authenticating with a remote server over SSH:

1. **Username and Password**
2. **Public Key Authentication**

#### Username and Password

This method involves providing a username and password to authenticate with the remote server. The username must be registered on the remote server, not on the local machine. Here’s how it works:

1. **User Registration**: A user account must be created on the remote server. This account will be used to authenticate the user when connecting via SSH.
2. **Connection Request**: When a user attempts to connect to the remote server using SSH, they provide their username and password.
3. **Authentication**: The remote server verifies the provided credentials against its user database. If the credentials match, the user is granted access.

##### Example

Let’s say we have an application server running remotely. This could be a server in our company's own data center or a server hosted by a cloud provider like AWS. To connect to this server using SSH with username and password authentication, you would use the following command:

```sh
ssh username@remote-server-ip
```

Upon executing this command, you will be prompted to enter the password associated with the `username` on the remote server.

### Public Key Authentication

Public key authentication is a more secure and convenient method of authentication compared to username and password. It involves generating a pair of cryptographic keys: a public key and a private key. The public key is stored on the remote server, while the private key is kept on the local machine.

#### How It Works

1. **Key Generation**: Generate a pair of cryptographic keys using a tool like `ssh-keygen`.
2. **Public Key Upload**: Copy the public key to the remote server, typically stored in the `~/.ssh/authorized_keys` file.
3. **Private Key Storage**: Keep the private key securely on the local machine.
4. **Connection Request**: When a user attempts to connect to the remote server using SSH, the server sends a challenge to the client.
5. **Challenge Response**: The client uses the private key to sign the challenge and send the signed response back to the server.
6. **Verification**: The server verifies the signed response using the public key. If the verification is successful, the user is granted access.

##### Example

To set up public key authentication, follow these steps:

1. **Generate Keys**:
    ```sh
    ssh-keygen -t rsa -b 4096
    ```
    This command generates a 4096-bit RSA key pair. The private key is stored in `~/.ssh/id_rsa`, and the public key is stored in `~/.ssh/id_rsa.pub`.

2. **Copy Public Key to Remote Server**:
    ```sh
    ssh-copy-id username@remote-server-ip
    ```
    This command copies the public key to the remote server and appends it to the `~/.ssh/authorized_keys` file.

3. **Connect Using SSH**:
    ```sh
    ssh username@remote-server-ip
    ```
    Upon executing this command, you will be connected to the remote server without needing to enter a password.

### SSH Configuration

SSH configurations are managed through configuration files on both the client and the server. These files contain settings that control various aspects of SSH behavior.

#### Client Configuration

The client configuration file is typically located at `~/.ssh/config`. This file allows you to define host-specific settings, such as the hostname, port, and authentication method.

##### Example Configuration

```sh
Host myserver
    HostName remote-server-ip
    User username
    IdentityFile ~/.ssh/id_rsa
```

With this configuration, you can connect to the remote server using a simple command:

```sh
ssh myserver
```

#### Server Configuration

The server configuration file is typically located at `/etc/ssh/sshd_config`. This file contains settings that control the behavior of the SSH daemon (`sshd`).

##### Example Configuration

```sh
Port 22
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
```

This configuration sets the SSH port to 22, disables root login, enables public key authentication, and disables password authentication.

### SSH Commands and Usage

SSH provides a variety of commands and options to facilitate secure communication and management of remote systems.

#### Basic SSH Command

The basic SSH command is used to establish a secure connection to a remote server:

```sh
ssh username@remote-server-ip
```

#### SSH with Custom Port

If the remote server is configured to listen on a non-standard port, you can specify the port using the `-p` option:

```sh
ssh -p 2222 username@remote-server-ip
```

#### SSH with ProxyJump

ProxyJump allows you to connect to a remote server through an intermediate server. This is useful when the remote server is not directly accessible from the client.

```sh
ssh -J intermediate-user@intermediate-server-ip remote-user@remote-server-ip
```

#### SSH with Tunneling

SSH tunneling allows you to create a secure tunnel between the client and the server, enabling secure communication over an unsecured network.

##### Example: Local Port Forwarding

Local port forwarding allows you to forward traffic from a local port to a remote server.

```sh
ssh -L 8080:localhost:80 username@remote-server-ip
```

This command forwards traffic from port 8080 on the local machine to port 80 on the remote server.

##### Example: Remote Port Forwarding

Remote port forwarding allows you to forward traffic from a remote server to a local machine.

```sh
ssh -R 8080:localhost:80 username@remote-server-ip
```

This command forwards traffic from port  8080 on the remote server to port 80 on the local machine.

### SSH Security Considerations

While SSH provides robust security features, it is important to follow best practices to ensure the security of your SSH connections.

#### Strong Passwords

Using strong passwords is essential to prevent brute-force attacks. Ensure that passwords are complex and unique.

#### Disable Root Login

Disabling root login via SSH reduces the risk of unauthorized access to the server. This can be done by setting `PermitRootLogin no` in the `/etc/ssh/sshd_config` file.

#### Enable Public Key Authentication

Enabling public key authentication provides a more secure alternative to password-based authentication. This can be done by setting `PubkeyAuthentication yes` in the `/etc/ssh/sshd_config` file.

#### Disable Password Authentication

Disabling password authentication further enhances security by preventing unauthorized access via brute-force attacks. This can be done by setting `PasswordAuthentication no` in the `/etc/ssh/sshd_config` file.

#### Use Strong Encryption Algorithms

Ensure that strong encryption algorithms are used to protect the confidentiality and integrity of data transmitted over SSH. This can be done by configuring the `Ciphers` and `MACs` directives in the `/etc/ssh/sshd_config` file.

### Real-World Examples and Breaches

SSH has been involved in several high-profile breaches and vulnerabilities. Understanding these incidents can help you better secure your SSH connections.

#### CVE-2016-6210: "sshroothole"

CVE-2016-6210, also known as "sshroothole," is a vulnerability in OpenSSH that allows attackers to bypass authentication and gain root access to the server. This vulnerability affects versions of OpenSSH prior to 7.2p2.

##### Impact

An attacker could exploit this vulnerability to gain root access to the server, potentially leading to a complete compromise of the system.

##### Prevention

To prevent this vulnerability, ensure that you are using a version of OpenSSH that is patched against CVE-2016-6210. This can be done by updating to the latest version of OpenSSH.

#### CVE-2016-10009

CVE-2016-10009 is a vulnerability in OpenSSH that allows attackers to bypass authentication and gain access to the server. This vulnerability affects versions of OpenSSH prior to 7.2p2.

##### Impact

An attacker could exploit this vulnerability to gain access to the server, potentially leading to a complete compromise of the system.

##### Prevention

To prevent this vulnerability, ensure that you are using a version of OpenSSH that is patched against CVE-2016-10009. This can be done by updating to the latest version of OpenSSH.

### Secure Coding Practices

When working with SSH, it is important to follow secure coding practices to ensure the security of your SSH connections.

#### Avoid Hardcoding Credentials

Avoid hardcoding credentials such as usernames and passwords in your scripts. Instead, use environment variables or configuration files to store sensitive information.

##### Example: Environment Variables

```sh
export SSH_USERNAME=username
export SSH_PASSWORD=password
```

##### Example: Configuration Files

```sh
[ssh]
username = username
password = password
```

#### Use SSH Agent

Using an SSH agent can help you securely manage your SSH keys. An SSH agent allows you to load your private key into memory, eliminating the need to enter your passphrase every time you use SSH.

##### Example: SSH Agent

```sh
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

### Detection and Prevention

Detecting and preventing SSH-related vulnerabilities is crucial to maintaining the security of your systems.

#### Monitoring SSH Logs

Monitoring SSH logs can help you detect unauthorized access attempts and potential security breaches. SSH logs are typically located at `/var/log/auth.log` or `/var/log/secure`.

##### Example: Monitoring SSH Logs

```sh
tail -f /var/log/auth.log
```

#### Intrusion Detection Systems (IDS)

Intrusion detection systems (IDS) can help you detect and respond to security breaches in real-time. IDS can monitor network traffic and alert you to suspicious activity.

##### Example: Snort IDS

Snort is an open-source intrusion detection system that can be used to monitor network traffic and detect potential security breaches.

```sh
sudo apt-get install snort
```

#### Network Segmentation

Network segmentation can help you isolate critical systems and reduce the risk of unauthorized access. By segmenting your network, you can limit the spread of attacks and prevent lateral movement.

##### Example: VLANs

Virtual LANs (VLANs) can be used to segment your network and isolate critical systems.

```sh
sudo vconfig add eth0 10
```

### Conclusion

Secure Shell (SSH) is a powerful and versatile protocol that provides secure communication between a client and a server. By understanding the concepts and usage of SSH, you can effectively manage remote systems and ensure the security of your SSH connections. Following best practices and staying up-to-date with the latest security measures can help you prevent potential security breaches and maintain the integrity of your systems.

### Practice Labs

For hands-on practice with SSH, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including SSH.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including SSH.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including SSH.
- **WebGoat**: An interactive web security training application that includes SSH exercises.

These labs provide real-world scenarios and challenges to help you master SSH and related security concepts.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/01-Linux & OS Basics/05-Secure Shell Concepts And Usage/00-Overview|Overview]] | [[02-Secure Shell Concepts and Usage|Secure Shell Concepts and Usage]]
