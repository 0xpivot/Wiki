---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of an EC2 instance in AWS and how it fits into the compute product category.**

An EC2 (Elastic Compute Cloud) instance in AWS is a virtual server that runs in one of Amazon's data centers. It is categorized under the compute product category because it provides users with computing power. EC2 instances can be used to run various applications, including web servers, databases, and other software services. By providing scalable and flexible computing resources, EC2 enables users to quickly provision and manage computing capacity according to their needs.

**Q2. How do you create an EC2 instance and configure it for a basic web application deployment?**

To create an EC2 instance and configure it for a basic web application deployment, follow these steps:

1. **Launch an EC2 Instance:**
   - Go to the EC2 Dashboard in the AWS Management Console.
   - Click on the "Launch Instance" button.
   - Choose an AMI (Amazon Machine Image), such as Amazon Linux.
   - Select an instance type, like `t2.micro` for a free-tier eligible option.
   - Configure instance details, such as the number of instances, network settings, and subnet selection.
   - Add storage as needed.
   - Tag the instance with metadata, such as `Type=WebServer`.
   - Configure security groups to allow SSH (port 22) and HTTP (port 80).

2. **Connect to the Instance:**
   - Download the key pair (`.pem` file) and store it securely.
   - Use SSH to connect to the instance:
     ```sh
     ssh -i path/to/keypair.pem ec2-user@public-ip-address
     ```

3. **Install Docker:**
   - Update the package manager:
     ```sh
     sudo yum update
     ```
   - Install Docker:
     ```sh
     sudo yum install docker
     ```
   - Start Docker:
     ```sh
     sudo service docker start
     ```
   - Add the user to the Docker group:
     ```sh
     sudo usermod -a -G docker ec2-user
     ```
   - Log out and log back in for the changes to take effect.

4. **Deploy the Web Application:**
   - Pull the Docker image from a private repository:
     ```sh
     docker login
     docker pull username/repository:tag
     ```
   - Run the Docker container:
     ```sh
     docker run -d -p 80:3080 username/repository:tag
     ```

5. **Configure External Access:**
   - Ensure the security group allows traffic on port 80.
   - Access the application via the public IP address or DNS name in a browser.

**Q3. Why is it important to configure a security group for an EC2 instance? Provide an example of how to configure a security group to allow SSH and HTTP traffic.**

Configuring a security group for an EC2 instance is crucial because it acts as a virtual firewall to control inbound and outbound traffic. Properly configured security groups help ensure that only necessary traffic is allowed, enhancing the security of the instance.

Example of configuring a security group to allow SSH and HTTP traffic:

1. **Create a New Security Group:**
   - Name the security group (e.g., `WebServerSecurityGroup`).
   - Add inbound rules:
     - **SSH (TCP)**: Allow traffic on port 22 from your IP address or a range of IP addresses.
       - Type: SSH
       - Protocol: TCP
       - Port Range: 22
       - Source: Your IP address (e.g., `192.0.2.0/24`)
     - **HTTP (TCP)**: Allow traffic on port  80 from anywhere.
       - Type: HTTP
       - Protocol: TCP
       - Port Range: 80
       - Source: Anywhere (e.g., `0.0.0.0/0`)

2. **Attach the Security Group to the EC2 Instance:**
   - When launching the instance, attach the newly created security group.

By setting these rules, you ensure that only necessary traffic (SSH and HTTP) is allowed, while blocking unauthorized access.

**Q4. How would you troubleshoot an issue where a deployed web application on an EC2 instance is not accessible via its public IP address?**

To troubleshoot an issue where a deployed web application on an EC2 instance is not accessible via its public IP address, follow these steps:

1. **Check Security Group Rules:**
   - Ensure the security group attached to the EC2 instance allows inbound traffic on the required port (e.g., port 80 for HTTP).
   - Verify that the source IP address range is correctly specified to allow traffic from your client machine.

2. **Verify Network Configuration:**
   - Check the network interface associated with the EC2 instance to ensure it has a public IP address assigned.
   - Confirm that the instance is running in a subnet that supports public IP addresses.

3. **Inspect Docker Container Status:**
   - Ensure the Docker container is running and listening on the expected port.
   - Use `docker ps` to check the status of the container.
   - Use `docker logs <container-id>` to inspect the container logs for any errors.

4. **Check Firewall Settings:**
   - Ensure that any additional firewalls (e.g., iptables) on the EC2 instance are not blocking the required traffic.

5. **Test Connectivity:**
   - From another machine, attempt to reach the EC2 instance using tools like `ping`, `telnet`, or `curl` to verify connectivity and port accessibility.
   - Example:
     ```sh
     curl http://public-ip-address:80
     ```

6. **Review Application Logs:**
   - Check the application logs for any errors or warnings that might indicate issues with the application itself.

By systematically checking each component, you can identify and resolve the issue preventing the web application from being accessible.

**Q5. What recent real-world examples or CVEs highlight the importance of securing EC2 instances and their deployed applications?**

Recent real-world examples and CVEs highlight the critical importance of securing EC2 instances and their deployed applications. One notable example is the widespread exploitation of unsecured Kubernetes clusters, which often run on EC2 instances.

For instance, in 2021, several Kubernetes clusters were compromised due to misconfigured security groups and exposed API endpoints. Attackers exploited these vulnerabilities to gain unauthorized access to the clusters and deploy malicious cryptocurrency mining software. This incident underscores the importance of properly configuring security groups and ensuring that only necessary ports are exposed.

Another example is the exploitation of unsecured Docker daemons. In 2020, attackers targeted Docker daemons exposed to the internet, compromising numerous EC2 instances. They used these instances to launch distributed denial-of-service (DDoS) attacks and mine cryptocurrencies. This highlights the need for strict security measures, including proper firewall configurations and limiting access to sensitive services.

These incidents emphasize the necessity of securing EC2 instances and their deployed applications to prevent unauthorized access and potential misuse.

---
<!-- nav -->
[[16-Running a Docker Container from a Private Repository|Running a Docker Container from a Private Repository]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/15-Deploying Web Applications Using EC2 Instances/00-Overview|Overview]]
