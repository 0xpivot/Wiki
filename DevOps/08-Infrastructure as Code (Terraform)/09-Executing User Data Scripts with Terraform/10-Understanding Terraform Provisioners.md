---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Terraform Provisioners

### What Are Terraform Provisioners?

Terraform provisioners are a mechanism within Terraform that allows you to run scripts or commands on resources after they are created. This is particularly useful for setting up software, configuring services, or performing other initialization tasks that are necessary for the resource to function correctly. While provisioners can be powerful tools, they are often considered a workaround for more robust and scalable solutions.

#### Why Use Provisioners?

Provisioners are used primarily for:

1. **Initialization**: Setting up software or configurations on newly created resources.
2. **Customization**: Performing custom tasks that are not covered by standard Terraform modules.
3. **Workarounds**: Handling situations where more sophisticated solutions are not available or practical.

However, it is important to understand that using provisioners can introduce several risks and complexities, which we will explore later.

### How Do Provisioners Work?

When you define a provisioner in your Terraform configuration, Terraform will execute the specified script or command on the target resource after it has been created. This process involves several steps:

1. **Resource Creation**: Terraform creates the resource (e.g., an EC2 instance).
2. **Provisioner Execution**: Once the resource is created, Terraform runs the provisioner.
3. **Error Handling**: If the provisioner fails, Terraform marks the resource as tainted, indicating that it needs to be recreated.

#### Example of a Provisioner in Terraform

Here is a simple example of a Terraform configuration that uses a provisioner to run a script on an EC2 instance:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }

    inline = [
      "sudo yum update -y",
      "sudo yum install -y httpd",
      "echo 'Hello, World!' > /var/www/html/index.html",
      "sudo systemctl start httpd",
      "sudo systemctl enable httpd",
    ]
  }
}
```

In this example, the `remote-exec` provisioner is used to run a series of commands on the EC2 instance after it is created. These commands update the system, install Apache HTTP Server, create an index file, and start the server.

### Pitfalls of Using Provisioners

While provisioners can be useful, they also introduce several potential issues:

1. **Complexity**: Managing scripts and ensuring they run correctly can be complex.
2. **Reproducibility**: Scripts may not always produce the same results, leading to inconsistent states.
3. **Maintenance**: Updating scripts and ensuring they work with new versions of software can be challenging.
4. **Security Risks**: Running arbitrary scripts can introduce security vulnerabilities if not properly managed.

#### Real-World Example: CVE-2021-21972

A notable example of a security issue related to provisioning is CVE-2021-21972, which affected Docker. This vulnerability allowed an attacker to escalate privileges by manipulating the provisioning process. In this case, the attacker could inject malicious code during the provisioning phase, leading to unauthorized access and control over the system.

### How to Prevent / Defend Against Provisioner Risks

To mitigate the risks associated with using provisioners, consider the following strategies:

1. **Use Immutable Infrastructure**: Instead of provisioning resources dynamically, use immutable infrastructure where resources are pre-configured and deployed as-is.
2. **Automate with Configuration Management Tools**: Use tools like Ansible, Puppet, or Chef to manage configurations and ensure consistency.
3. **Secure Script Execution**: Ensure that scripts are securely stored and executed. Use SSH keys and secure connections.
4. **Monitor and Audit**: Regularly monitor and audit the provisioning process to detect and address issues promptly.

#### Secure Code Example

Here is an example of a secure configuration using Ansible instead of a provisioner:

```yaml
---
- name: Configure EC2 Instance
  hosts: ec2_instances
  become: yes
  tasks:
    - name: Update the package list
      yum:
        name: "*"
        state: latest

    - name: Install Apache HTTP Server
      yum:
        name: httpd
        state: present

    - name: Create index file
      copy:
        content: "Hello, World!"
        dest: /var/www/html/index.html

    - name: Start and enable Apache service
      systemd:
        name: httpd
        state: started
        enabled: yes
```

This Ansible playbook ensures that the EC2 instance is configured consistently and securely.

### Full Example: Terraform Apply with Provisioner Failure

Let's walk through a scenario where a provisioner fails due to a missing script. Here is the full Terraform configuration:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "file" {
    source      = "path/to/nonexistent/script.sh"
    destination = "/tmp/script.sh"
  }

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }

    inline = [
      "chmod +x /tmp/script.sh",
      "/tmp/script.sh",
    ]
  }
}
```

When you run `terraform apply`, Terraform will attempt to copy the script and execute it. If the script is not found, Terraform will fail and mark the resource as tainted.

#### Error Message and Result

Here is the full error message and result:

```plaintext
Error: error executing "remote-exec" provisioner: ssh: failed to open file /tmp/script.sh: No such file or directory

  on main.tf line 11, in resource "aws_instance" "example":
  11: resource "aws_instance" "example" {

The resource will be marked for deletion.
```

As you can see, the EC2 instance is created but the provisioner fails, leading to the instance being marked for deletion.

### Conclusion

While Terraform provisioners can be useful for initializing resources, they should be used with caution due to the potential risks and complexities involved. By understanding these risks and implementing proper security measures, you can effectively use provisioners in your Terraform configurations.

### Hands-On Practice

For hands-on practice with Terraform and provisioners, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications, including those involving Terraform and provisioners.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including infrastructure setup with Terraform.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for practicing web security, which can be set up using Terraform.

These labs provide real-world scenarios and challenges to help you master the use of Terraform provisioners and related security practices.

---
<!-- nav -->
[[09-Understanding Provisioners in Terraform|Understanding Provisioners in Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/09-Executing User Data Scripts with Terraform/00-Overview|Overview]] | [[11-Understanding Terraform and User Data Scripts|Understanding Terraform and User Data Scripts]]
