---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to SSH Key Pairs

### What is SSH?

Secure Shell (SSH) is a cryptographic network protocol for operating network services securely over an unsecured network. Typical applications include remote command-line login and remote command execution, but any network service can be secured with SSH. The protocol provides strong authentication and secure communications over insecure channels using a client-server architecture.

### Why Use SSH Keys?

SSH keys provide a more secure way to authenticate users compared to traditional password-based authentication. Passwords can be guessed, stolen, or brute-forced, whereas SSH keys are much harder to compromise. Additionally, SSH keys allow for automated logins, which is essential for many DevOps tasks such as deploying code to servers or managing infrastructure.

### How SSH Keys Work

An SSH key pair consists of two parts: a private key and a public key. The private key is kept secret and should never be shared, while the public key can be freely distributed. When you want to access a server, you present your public key to the server. The server checks if the public key is authorized to access the account. If it is, the server sends a challenge to your computer, which uses the private key to decrypt the challenge and send back a response. If the response is correct, you are granted access.

### Generating SSH Key Pairs

To generate an SSH key pair, you can use the `ssh-keygen` command. This command creates both the private and public keys. Here’s how you can generate an SSH key pair:

```sh
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

This command does the following:
- `-t rsa`: Specifies the type of key to create. RSA is one of the most commonly used types.
- `-b 4096`: Specifies the number of bits in the key. A larger bit size means a stronger key, but also slower encryption and decryption.
- `-C "your_email@example.com"`: Adds a comment to the key, typically your email address. This helps identify the key.

### Storing SSH Keys

The generated keys are stored in the `.ssh` directory in your home directory. By default, the private key is named `id_rsa`, and the public key is named `id_rsa.pub`.

```sh
~/.ssh/id_rsa
~/.ssh/id_rsa.pub
```

### Using SSH Keys

To use your SSH keys, you need to copy the public key (`id_rsa.pub`) to the server you want to access. This is typically done by appending the public key to the `~/.ssh/authorized_keys` file on the server.

#### Example: Copying Public Key to Server

You can use the `ssh-copy-id` command to copy your public key to a server:

```sh
ssh-copy-id user@server_ip
```

This command copies the contents of your `id_rsa.pub` file to the `~/.ssh/authorized_keys` file on the server.

### Recent Real-World Examples

#### CVE-2021-20225: SSH Key Management Vulnerability

In 2021, a vulnerability was discovered in the management of SSH keys in certain versions of OpenSSH. This vulnerability allowed attackers to bypass SSH key restrictions and gain unauthorized access to systems. The vulnerability was due to improper validation of the `AuthorizedKeysCommand` option in the SSH daemon configuration.

**Impact**: Systems using OpenSSH could be compromised if the `AuthorizedKeysCommand` option was misconfigured.

**Mitigation**: Ensure that the `AuthorizedKeysCommand` option is properly configured and validated. Keep your SSH software up to date with the latest security patches.

### Pitfalls and Common Mistakes

#### Exposing Private Keys

One of the most critical mistakes is exposing your private key. If your private key is compromised, anyone with access to it can impersonate you and gain unauthorized access to your systems.

**Prevention**: Store your private key in a secure location, such as a hardware security module (HSM) or a secure key storage service. Use strong passphrases to protect your private key.

#### Misconfiguring SSH Daemon

Misconfiguring the SSH daemon can lead to security vulnerabilities. For example, enabling root login or allowing password authentication can make your system more susceptible to attacks.

**Prevention**: Disable root login and enforce key-based authentication. Configure the SSH daemon to reject password authentication and only accept key-based authentication.

### Secure Coding Practices

#### Vulnerable Code Example

Here is an example of a vulnerable SSH configuration that allows password authentication and root login:

```sh
# /etc/ssh/sshd_config
PermitRootLogin yes
PasswordAuthentication yes
```

#### Secure Code Example

Here is the corrected configuration that disables root login and enforces key-based authentication:

```sh
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

### Detection and Prevention

#### Detection

Regularly audit your SSH configurations and check for unauthorized access attempts. Use tools like `fail2ban` to monitor and block suspicious activity.

#### Prevention

- **Use Strong Passphrases**: Protect your private key with a strong passphrase.
- **Keep Software Updated**: Regularly update your SSH software to the latest version.
- **Limit Access**: Restrict access to your SSH keys and ensure that only authorized users have access to them.
- **Audit Logs**: Regularly review SSH logs to detect any unauthorized access attempts.

### Hands-On Labs

For hands-on practice with SSH key management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including SSH key management.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques, including SSH key management.
- **CloudGoat**: Focuses on cloud security and includes exercises on managing SSH keys in cloud environments.

By following these practices and using the provided resources, you can effectively manage SSH keys and ensure the security of your systems.

---
<!-- nav -->
[[09-Introduction to Infrastructure as Code (IaC)|Introduction to Infrastructure as Code (IaC)]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[11-Creating AWS EC2 Instance Configuration|Creating AWS EC2 Instance Configuration]]
