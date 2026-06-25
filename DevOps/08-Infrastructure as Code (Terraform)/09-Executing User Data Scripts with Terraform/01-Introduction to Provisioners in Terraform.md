---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Provisioners in Terraform

In the context of infrastructure as code (IAC), Terraform is a powerful tool that allows you to define and manage your infrastructure using declarative configuration files. One of the key features of Terraform is the ability to use provisioners, which are scripts or commands that run after the creation of a resource. This chapter will delve into the details of executing user data scripts with Terraform, focusing on three types of provisioners: `remote-exec`, `file`, and `local-exec`.

### What Are Provisioners?

Provisioners are a way to run scripts or commands on resources managed by Terraform. They are particularly useful for tasks such as installing software, configuring services, or setting up initial states on newly created instances. There are several types of provisioners available in Terraform, but we will focus on the following three:

1. **Remote-exec**: Executes a script or command on the remote machine.
2. **File**: Copies files from the local machine to the remote server.
3. **Local-exec**: Executes a script or command on the local machine.

### Why Use Provisioners?

Provisioners are essential for automating the setup and configuration of resources. By using provisioners, you can ensure that your infrastructure is consistently configured across multiple environments. This is particularly important in a DevOps context, where reproducibility and consistency are key.

### How Provisioners Work

When you define a provisioner in your Terraform configuration, Terraform will execute the specified script or command at the appropriate time during the lifecycle of the resource. For example, a `remote-exec` provisioner will run after the creation of an instance, allowing you to configure the instance immediately after it is created.

### Example: Using Remote-exec Provisioner

Let's start with an example of how to use the `remote-exec` provisioner. Suppose you want to create an EC2 instance and run a script on it to install a specific piece of software.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx",
    ]
  }
}
```

In this example, the `remote-exec` provisioner runs two commands on the remote instance:
1. `sudo apt-get update`: Updates the package list.
2. `sudo apt-get install -y nginx`: Installs the Nginx web server.

### Example: Using File Provisioner

Next, let's look at how to use the `file` provisioner to copy files from the local machine to the remote server.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "file" {
    source      = "./config/nginx.conf"
    destination = "/etc/nginx/nginx.conf"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo systemctl restart nginx",
    ]
  }
}
```

In this example, the `file` provisioner copies the `nginx.conf` file from the local directory to the `/etc/nginx/nginx.conf` location on the remote instance. After the file is copied, the `remote-exec` provisioner restarts the Nginx service.

### Example: Using Local-exec Provisioner

Finally, let's look at how to use the `local-exec` provisioner to execute commands on the local machine.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "local-exec" {
    command = "echo 'Instance ${self.private_ip} created'"
  }
}
```

In this example, the `local-exec` provisioner runs a command on the local machine that prints the private IP address of the created instance.

### Sharing Connections Between Provisioners

One important aspect of using provisioners is that they share connections. This means that if you have multiple provisioners defined for a resource, they will reuse the same SSH connection to the remote machine. This can save time and resources, especially if you have multiple steps that need to be executed on the remote machine.

For example, consider the following configuration:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "file" {
    source      = "./config/nginx.conf"
    destination = "/etc/nginx/nginx.conf"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo systemctl restart nginx",
    ]
  }
}
```

In this configuration, the `file` provisioner and the `remote-exec` provisioner share the same SSH connection to the remote instance.

### Copying Files to Multiple Servers

If you need to copy files to multiple servers, you can define separate connection blocks within each provisioner. For example:

```hcl
resource "aws_instance" "server1" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "file" {
    source      = "./config/nginx.conf"
    destination = "/etc/nginx/nginx.conf"
    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
    }
  }
}

resource "aws_instance" "server2" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "file" {
    source      = "./config/nginx.conf"
    destination = "/etc/nginx/nginx.conf"
    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
    }
  }
}
```

In this example, the `file` provisioner is defined separately for each server, with its own connection block specifying the host and credentials.

### Pitfalls and Best Practices

While provisioners are powerful tools, they also come with potential pitfalls. Here are some best practices to keep in mind:

1. **Security**: Ensure that your SSH keys and other sensitive information are properly secured. Avoid hardcoding sensitive information in your Terraform configurations.
2. **Consistency**: Use provisioners to ensure consistent configuration across multiple environments. This helps avoid configuration drift.
3. **Idempotency**: Make sure that your provisioner scripts are idempotent, meaning they can be run multiple times without causing unintended side effects.
4. **Testing**: Test your provisioner scripts thoroughly to ensure they work as expected. Consider using tools like `Packer` to test your scripts in isolation.

### Real-World Examples

#### Example 1: CVE-2021-21972

CVE-2021-21972 is a critical vulnerability in the Apache Log4j library that allows attackers to execute arbitrary code on affected systems. In a Terraform context, you might use a `remote-exec` provisioner to patch the Log4j library on your servers.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "wget https://archive.apache.org/dist/logging/log4j/2.17.0/apache-log4j-2.17.0-bin.tar.gz",
      "tar -xzvf apache-log4j-2.17.0-bin.tar.gz",
      "mv apache-log4j-2.17.0-bin /opt/log4j",
      "rm apache-log4j-2.17.0-bin.tar.gz",
    ]
  }
}
```

In this example, the `remote-exec` provisioner downloads and installs the patched version of Log4j on the remote instance.

#### Example 2: Breach at Capital One (2019)

The breach at Capital One in 2019 was caused by a misconfigured web application firewall (WAF) that allowed unauthorized access to customer data. In a Terraform context, you might use a `remote-exec` provisioner to configure the WAF correctly.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo yum install -y aws-waf",
      "sudo aws waf update-web-acl --web-acl-id <web_acl_id> --changes '[{\"Action\": \"INSERT\", \"Predicate\": {\"Type\": \"IPMatch\", \"DataId\": \"<data_id>\"}}]'",
    ]
  }
}
```

In this example, the `remote-exec` provisioner installs and configures the WAF on the remote instance.

### How to Prevent / Defend

#### Detection

To detect issues with provisioners, you can use logging and monitoring tools. For example, you can log the output of your provisioner scripts and monitor for errors or unexpected behavior.

#### Prevention

To prevent issues with provisioners, follow these best practices:

1. **Use Idempotent Scripts**: Ensure that your provisioner scripts are idempotent to avoid unintended side effects.
2. **Secure Credentials**: Securely manage your SSH keys and other sensitive information.
3. **Test Thoroughly**: Test your provisioner scripts thoroughly to ensure they work as expected.
4. **Use Version Control**: Use version control to track changes to your Terraform configurations and provisioner scripts.

#### Secure Coding Fixes

Here is an example of a vulnerable and secure version of a `remote-exec` provisioner script:

**Vulnerable Version**

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx",
    ]
  }
}
```

**Secure Version**

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx",
      "sudo systemctl enable nginx",
      "sudo systemctl start nginx",
    ]
  }
}
```

In the secure version, additional commands are added to ensure that the Nginx service is enabled and started.

### Conclusion

Provisioners are a powerful feature of Terraform that allow you to automate the setup and configuration of resources. By using provisioners effectively, you can ensure that your infrastructure is consistently configured across multiple environments. However, it is important to follow best practices to avoid potential pitfalls and ensure the security of your infrastructure.

### Practice Labs

To gain hands-on experience with Terraform provisioners, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve using Terraform provisioners.
- **OWASP Juice Shop**: A deliberately insecure web application that you can use to practice securing and configuring resources using Terraform provisioners.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that you can use to practice using Terraform provisioners.

By completing these labs, you can gain practical experience with Terraform provisioners and improve your skills in managing and securing infrastructure as code.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/09-Executing User Data Scripts with Terraform/00-Overview|Overview]] | [[02-Introduction to Remote Execution Provisioners in Terraform|Introduction to Remote Execution Provisioners in Terraform]]
