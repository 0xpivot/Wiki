---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring Docker Repository on Nexus

In this section, we will delve into the process of configuring a Docker repository on Nexus, a popular artifact management solution. This involves setting up the necessary ports, configuring the firewall, and setting up realms for authentication. Each step will be explained in detail, including the underlying mechanisms and potential pitfalls.

### Setting Up the Docker Repository Port

When configuring a Docker repository on Nexus, one of the first steps is to set up the appropriate port. In this case, the port `8083` was chosen. This port is used to communicate with the Docker repository hosted on the Nexus server.

#### Why This Port Matters

The choice of port is crucial because it determines how external clients (such as Docker clients) will communicate with the Nexus server. By default, Docker uses port `5000` for communication, but this can be changed to suit specific requirements or to avoid conflicts with other services.

#### How It Works Under the Hood

When a Docker client attempts to push or pull images from the Nexus repository, it sends HTTP requests to the specified port. These requests are handled by the Nexus server, which processes them according to the configured settings.

#### Checking the Port Configuration

To verify that the port is correctly configured, you can use tools like `netstat` on the server where Nexus is running. Here’s an example of how to check the port:

```bash
sudo netstat -tuln | grep 8083
```

This command will list all listening TCP and UDP ports and filter the output to show only those related to port `8083`.

#### Real-World Example

Consider a scenario where a company uses Nexus to manage Docker images for their microservices architecture. If the port is not correctly configured, Docker clients will not be able to communicate with the Nexus server, leading to failures in deployment pipelines.

### Opening the Port on the Firewall

Once the port is configured on the Nexus server, the next step is to ensure that the firewall allows traffic through this port. In this example, the server is running on a DigitalOcean droplet, and the firewall configuration needs to be updated accordingly.

#### Why Firewall Configuration Matters

Firewalls are essential for securing servers by controlling incoming and outgoing network traffic based on predetermined security rules. Without proper firewall configuration, the port may be blocked, preventing Docker clients from accessing the Nexus repository.

#### How to Configure the Firewall

To open the port on the DigitalOcean firewall, follow these steps:

1. Log in to your DigitalOcean account.
2. Navigate to the Networking > Firewalls section.
3. Select the firewall associated with your droplet.
4. Add a new rule to allow traffic on port `8083`.

Here’s an example of how to add the rule using the DigitalOcean API:

```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-access-token>" \
     -d '{"droplet_ids":[<your-droplet-id>],"inbound_rules":[{"protocol":"tcp","ports":"8083","sources":{"addresses":["0.0.0.0/0"]}}]}' \
     "https://api.digitalocean.com/v2/firewalls"
```

#### Real-World Example

A recent breach involved a misconfigured firewall that allowed unauthorized access to a Docker repository. Ensuring that the firewall is properly configured helps prevent such vulnerabilities.

### Configuring Realms for Authentication

The final step in setting up the Docker repository on Nexus is to configure realms for authentication. Realms determine how users are authenticated when interacting with the repository.

#### What Are Realms?

Realms are configurations that define how authentication is performed. In the context of Nexus, realms can be set up to authenticate users against various sources, such as LDAP, Active Directory, or internal user databases.

#### Why Realms Matter

Realms are crucial for ensuring that only authorized users can interact with the Docker repository. Without proper authentication, anyone could potentially push or pull images, leading to security risks.

#### How to Configure Realms

To configure realms in Nexus, follow these steps:

1. Log in to the Nexus UI.
2. Navigate to the Security > Realms section.
3. Create a new realm, specifying the type (e.g., LDAP, Active Directory).
4. Configure the realm settings according to your environment.

Here’s an example of a realm configuration in Nexus:

```json
{
  "name": "docker-realm",
  "type": "ldap",
  "properties": {
    "ldap.server.url": "ldap://ldap.example.com",
    "ldap.base.dn": "dc=example,dc=com",
    "ldap.user.filter": "(uid={username})",
    "ldap.group.filter": "(member={userDn})"
  }
}
```

#### Real-World Example

A recent CVE (CVE-2021-44228) involved a vulnerability in the Apache Log4j library, which could be exploited to gain unauthorized access to systems. Properly configuring realms in Nexus helps mitigate such risks by ensuring that only authenticated users can interact with the repository.

### Full Example: Configuring Docker Repository on Nexus

Let’s walk through a complete example of configuring a Docker repository on Nexus, including all the necessary steps and configurations.

#### Step 1: Configure the Port

First, ensure that the Nexus server is listening on the correct port (`8083`). You can verify this using `netstat`:

```bash
sudo netstat -tuln | grep 8083
```

#### Step 2: Open the Port on the Firewall

Next, open the port on the DigitalOcean firewall:

```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-access-token>" \
     -d '{"droplet_ids":[<your-droplet-id>],"inbound_rules":[{"protocol":"tcp","ports":"8083","sources":{"addresses":["0.0.0.0/0"]}}]}' \
     "https://api.digitalocean.com/v2/firewalls"
```

#### Step 3: Configure Realms for Authentication

Finally, configure realms in Nexus:

1. Log in to the Nexus UI.
2. Navigate to the Security > Realms section.
3. Create a new realm, specifying the type (e.g., LDAP, Active Directory).

Here’s an example of a realm configuration in Nexus:

```json
{
  "name": "docker-realm",
  "type": "ldap",
  "properties": {
    "ldap.server.url": "ldap://ldap.example.com",
    "ldap.base.dn": "dc=example,dc=com",
    "ldap.user.filter": "(uid={username})",
    "ldap.group.filter": "(member={userDn})"
  }
}
```

### Pitfalls and Common Mistakes

#### Misconfigured Ports

One common mistake is misconfiguring the port on the Nexus server or the firewall. This can lead to connectivity issues between Docker clients and the Nexus repository.

#### Incorrect Firewall Rules

Another pitfall is incorrectly configuring firewall rules. If the firewall does not allow traffic on the specified port, Docker clients will not be able to communicate with the Nexus server.

#### Weak Authentication Mechanisms

Using weak or default authentication mechanisms can expose the Docker repository to unauthorized access. Always configure strong authentication mechanisms and regularly review and update them.

### How to Prevent / Defend

#### Detection

Regularly monitor the Nexus server and firewall logs for any suspicious activity. Tools like Splunk or ELK Stack can help with log analysis and alerting.

#### Prevention

1. **Strong Authentication**: Ensure that strong authentication mechanisms are in place, such as multi-factor authentication (MFA).
2. **Regular Audits**: Conduct regular audits of the Nexus configuration and firewall rules to ensure they are up-to-date and secure.
3. **Secure Coding Practices**: Follow secure coding practices when configuring Nexus and Docker repositories. Avoid using default credentials and ensure that all configurations are reviewed and tested.

#### Secure-Coding Fixes

Here’s an example of a vulnerable configuration and the corresponding secure configuration:

**Vulnerable Configuration:**

```json
{
  "name": "default-realm",
  "type": "internal",
  "properties": {}
}
```

**Secure Configuration:**

```json
{
  "name": "secure-realm",
  "type": "ldap",
  "properties": {
    "ldap.server.url": "ldap://ldap.example.com",
    "ldap.base.dn": "dc=example,dc=com",
    "ldap.user.filter": "(uid={username})",
    "ldap.group.filter": "(member={userDn})"
  }
}
```

### Conclusion

Configuring a Docker repository on Nexus involves several key steps, including setting up the correct port, configuring the firewall, and setting up realms for authentication. By following these steps and being aware of common pitfalls, you can ensure that your Docker repository is secure and functional.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web security, including Docker and Nexus configurations.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in configuring and securing Docker repositories on Nexus.

---
<!-- nav -->
[[03-Introduction to Docker Repositories on Nexus|Introduction to Docker Repositories on Nexus]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/15-Creating Docker Repository On Nexus/00-Overview|Overview]] | [[05-Configuring a Docker Repository on Nexus|Configuring a Docker Repository on Nexus]]
