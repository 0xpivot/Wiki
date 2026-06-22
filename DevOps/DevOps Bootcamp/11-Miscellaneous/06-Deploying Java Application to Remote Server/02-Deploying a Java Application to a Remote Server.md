---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying a Java Application to a Remote Server

### Introduction

Deploying a Java application to a remote server involves several steps, including transferring the application files to the server, configuring the environment, and ensuring the application can be accessed over the network. In this section, we will cover these steps in detail, using a real-world scenario of deploying a Java application to a DigitalOcean droplet.

### Setting Up the Environment

Before deploying the Java application, ensure that the remote server has the necessary tools installed. In this case, we assume that Java is already installed on the remote server. If not, you can install Java using the following commands:

```bash
# Update package list
sudo apt update

# Install OpenJDK
sudo apt install default-jdk
```

Once Java is installed, you can verify the installation by checking the version:

```bash
java -version
```

### Transferring the Application Files

To transfer the application files to the remote server, you can use various methods such as SCP (Secure Copy Protocol), FTP (File Transfer Protocol), or SFTP (SSH File Transfer Protocol). In this example, we will use SCP to transfer the JAR file to the remote server.

#### Using SCP to Transfer Files

First, ensure that you have the SSH client installed on your local machine. Then, use the following command to transfer the JAR file to the remote server:

```bash
scp /path/to/your/jarfile.jar username@remote-server-ip:/root/
```

Replace `/path/to/your/jarfile.jar` with the actual path to your JAR file, `username` with your remote server username, and `remote-server-ip` with the IP address of your remote server.

After executing the command, the JAR file will be transferred to the `/root/` directory on the remote server.

### Verifying the Transfer

To verify that the JAR file has been successfully transferred, log in to the remote server using SSH:

```bash
ssh username@remote-server-ip
```

Then, navigate to the `/root/` directory and list the contents:

```bash
cd /root/
ls
```

You should see the JAR file listed in the directory.

### Running the Java Application

With the JAR file transferred to the remote server, you can now run the Java application. Use the following command to execute the JAR file:

```bash
java -jar /root/jarfile.jar
```

This command starts the Java application. Since the application is simple, it should start quickly and begin listening on the specified port.

### Configuring the Firewall

For the application to be accessible over the network, you need to configure the firewall to allow traffic on the specific port. In this example, the application is listening on port 7071.

#### Adding a Firewall Rule

To add a firewall rule on DigitalOcean, follow these steps:

1. Log in to your DigitalOcean account.
2. Navigate to the "Firewalls" section.
3. Click on the firewall associated with your droplet.
4. Add a new rule to allow incoming traffic on port 7071.

Here is an example of how to add a firewall rule using the DigitalOcean API:

```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{"inbound_rules": [{"protocol": "tcp", "ports": "7071", "sources": {"addresses": ["0.0.0.0/0"]}}]}' \
     "https://api.digitalocean.com/v2/firewalls/FIREWALL_ID/rules"
```

Replace `YOUR_ACCESS_TOKEN` with your DigitalOcean API token and `FIREWALL_ID` with the ID of your firewall.

### Accessing the Application

Once the firewall rule is added, you can access the application from a web browser. Use the public IP address of the droplet and append the port number:

```
http://REMOTE_SERVER_IP:7071
```

Replace `REMOTE_SERVER_IP` with the actual IP address of your droplet.

### Example Application

The example application in this scenario is a simple country lookup service. When you access the URL, you should see the UI where you can search for countries.

### Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect Firewall Configuration**: Ensure that the firewall rules are correctly configured to allow traffic on the required port.
2. **Security Vulnerabilities**: Exposing services to the internet can introduce security risks. Ensure that proper security measures are in place.

#### Best Practices

1. **Use Secure Protocols**: Consider using HTTPS instead of HTTP to encrypt data in transit.
2. **Limit Access**: Restrict access to the application only to trusted IP addresses or networks.
3. **Regular Updates**: Keep the operating system and applications up to date to mitigate known vulnerabilities.

### Real-World Examples

#### Recent Breaches

One notable breach involving misconfigured firewalls is the Capital One breach in 2019. The attacker exploited a misconfigured firewall rule, allowing unauthorized access to sensitive customer data. This highlights the importance of properly securing network configurations.

### How to Prevent / Defend

#### Detection

1. **Network Monitoring**: Use tools like Wireshark or tcpdump to monitor network traffic and detect unauthorized access attempts.
2. **Logging and Auditing**: Enable logging on the firewall and regularly review logs to identify suspicious activity.

#### Prevention

1. **Secure Configuration Management**: Use configuration management tools like Ansible or Terraform to manage firewall rules consistently and securely.
2. **Least Privilege Principle**: Configure firewall rules to allow only the minimum necessary traffic.

#### Secure Coding Fixes

Here is an example of a vulnerable firewall configuration and its secure counterpart:

**Vulnerable Configuration:**

```json
{
  "rules": [
    {
      "protocol": "tcp",
      "ports": "7071",
      "sources": {
        "addresses": ["0.0.0.0/0"]
      }
    }
  ]
}
```

**Secure Configuration:**

```json
{
  "rules": [
    {
      "protocol": "tcp",
      "ports": "7071",
      "sources": {
        "addresses": ["TRUSTED_IP_ADDRESS/32"]
      }
    }
  ]
}
```

Replace `TRUSTED_IP_ADDRESS` with the IP address of a trusted source.

### Hands-On Labs

For practical experience in deploying Java applications and managing firewalls, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications and managing network configurations.
- **DigitalOcean Tutorials**: Provides detailed guides on setting up and securing servers on DigitalOcean.

By following these steps and best practices, you can effectively deploy and secure a Java application on a remote server.

### Conclusion

Deploying a Java application to a remote server involves transferring the application files, configuring the environment, and ensuring network accessibility. By following the steps outlined in this chapter, you can successfully deploy and secure your application. Always prioritize security and regularly review your configurations to mitigate potential risks.

---
<!-- nav -->
[[01-Introduction to Deploying Java Applications to Remote Servers|Introduction to Deploying Java Applications to Remote Servers]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/06-Deploying Java Application to Remote Server/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/06-Deploying Java Application to Remote Server/03-Practice Questions & Answers|Practice Questions & Answers]]
