---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain why dynamically fetching the AMI ID from AWS is preferable over hardcoding it in the Terraform configuration.**

Dynamic fetching of the AMI ID from AWS is preferable over hardcoding it in the Terraform configuration for several reasons:

1. **Flexibility**: By dynamically fetching the AMI ID, you can ensure that you always use the latest version of the desired AMI. This is especially important if the AMI is updated frequently.
   
2. **Maintainability**: Hardcoded AMI IDs require manual updates whenever a new version of the AMI is released. Dynamic fetching eliminates this need, reducing maintenance overhead.

3. **Consistency**: Using dynamic fetching ensures that the same AMI is consistently used across different environments and deployments, reducing the risk of inconsistencies due to outdated hardcoded values.

4. **Automation**: Automating the process of fetching the AMI ID aligns with the principles of Infrastructure as Code (IaC), where the goal is to minimize manual intervention and maximize automation.

**Q2. How would you configure Terraform to automatically create an SSH key pair for an EC2 instance? Provide a code snippet.**

To configure Terraform to automatically create an SSH key pair for an EC2 instance, you can use the `aws_key_pair` resource. Here’s a code snippet that demonstrates this:

```hcl
variable "public_key_location" {
  description = "Location of the public key file"
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "server-key"
  public_key = file(var.public_key_location)
}

resource "aws_instance" "my_app_server" {
  ami           = data.aws_ami.latest_amazon_linux.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.ssh_key.key_name

  # Other configurations
}
```

In this example, `var.public_key_location` is a variable that specifies the location of the public key file. The `aws_key_pair` resource creates the key pair, and the `aws_instance` resource references the key pair using `key_name`.

**Q3. Why is it necessary to restrict the permissions of the private key file (PAM file) to 400?**

Restricting the permissions of the private key file (PAM file) to 400 is necessary for the following reasons:

1. **Security**: The private key file contains sensitive information that allows access to the EC2 instance. Restricting the permissions ensures that only the owner (typically the user who needs to SSH into the instance) can read the file. This prevents unauthorized access by other users on the system.

2. **AWS Requirements**: AWS requires that the private key file has strict permissions (400). If the permissions are too loose, AWS will reject SSH requests to the server. Therefore, setting the permissions to 400 is mandatory to comply with AWS requirements.

3. **Best Practices**: Following best practices for managing sensitive files helps prevent accidental exposure of the private key. This is particularly important in shared environments where multiple users might have access to the same system.

**Q4. What are the advantages of automating the creation of EC2 instances and related resources using Terraform instead of doing it manually?**

Automating the creation of EC2 instances and related resources using Terraform offers several advantages over manual processes:

1. **Reproducibility**: Terraform configurations can be version-controlled and reused across different environments (development, staging, production). This ensures consistency and reduces the likelihood of errors that can occur with manual setups.

2. **Scalability**: Automation simplifies scaling operations. You can quickly create and manage multiple instances and resources using Terraform, which is difficult to achieve manually at scale.

3. **Efficiency**: Automating repetitive tasks saves time and effort. Once the initial setup is done, you can apply the same configuration repeatedly without manual intervention.

4. **Documentation**: Terraform configurations serve as documentation for the infrastructure. This makes it easier for others to understand and maintain the setup, reducing the need for separate documentation.

5. **Error Reduction**: Automated processes reduce the risk of human error. Terraform validates the configuration and provides warnings or errors before applying changes, ensuring that the infrastructure is set up correctly.

6. **Ease of Cleanup**: When it’s time to destroy resources, Terraform can handle the cleanup process efficiently, ensuring that all resources are properly removed, including those created manually.

**Q5. How would you exploit a misconfigured security group that allows unrestricted access to port 22 (SSH)? Provide a practical example.**

A misconfigured security group that allows unrestricted access to port 22 (SSH) can be exploited by attempting to SSH into the EC2 instance from an external IP address. Here’s a practical example:

1. **Identify the Vulnerable Instance**: Use tools like `nmap` to scan the network and identify instances with port 22 open to the world.

2. **Attempt SSH Access**: Use the `ssh` command to attempt access to the instance. For example:

    ```bash
    ssh -i /path/to/private/key ec2-user@<instance-public-ip>
    ```

3. **Gain Access**: If the instance is vulnerable and the SSH credentials are known or can be guessed, you can gain unauthorized access to the instance.

**Example Exploit:**

```bash
# Scan the network to find open SSH ports
nmap -p 22 <target-ip-range>

# Attempt SSH access
ssh -i /path/to/private/key ec2-user@<vulnerable-instance-ip>
```

**Real-World Example:**

CVE-2021-20225 is a real-world example where a misconfigured security group allowed unrestricted access to port 22. Attackers exploited this vulnerability to gain unauthorized access to EC2 instances, leading to potential data breaches and unauthorized actions.

**Q6. How would you configure a Terraform module to output the public IP address of an EC2 instance after it is created? Provide a code snippet.**

To configure a Terraform module to output the public IP address of an EC2 instance after it is created, you can use the `output` block. Here’s a code snippet that demonstrates this:

```hcl
resource "aws_instance" "my_app_server" {
  ami           = data.aws_ami.latest_amazon_linux.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.ssh_key.key_name

  # Other configurations
}

output "ec2_public_ip" {
  value = aws_instance.my_app_server.public_ip
}
```

In this example, the `output` block defines an output named `ec2_public_ip`, which captures the public IP address of the EC2 instance (`aws_instance.my_app_server.public_ip`). When you run `terraform apply`, this output will be displayed in the console, providing the public IP address of the newly created instance.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/17-Conclusion|Conclusion]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]]
