---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Local Exec Provisioner in Terraform

In the context of DevOps automation, Terraform is a powerful tool used to manage infrastructure as code. One of the key features of Terraform is the ability to use provisioners, which allow you to run scripts or commands on your managed resources after they are created. The `local-exec` provisioner is particularly useful when you want to execute a command locally on the machine where the Terraform apply command is being run.

### What is a Provisioner?

A provisioner in Terraform is a mechanism that allows you to run scripts or commands on your managed resources. These scripts can be used to configure the resource, install software, or perform any other task necessary to set up the resource correctly. There are several types of provisioners available in Terraform, including:

- **Local-exec**: Executes a command locally on the machine where the Terraform apply command is being run.
- **Remote-exec**: Executes a command remotely on the resource being managed.
- **File**: Copies files to the resource being managed.
- **Shell**: Runs shell commands on the resource being managed.

### Why Use Local-exec Provisioner?

The `local-exec` provisioner is particularly useful when you want to execute a command locally on the machine where the Terraform apply command is being run. This can be useful in scenarios where you need to interact with the local environment, such as executing a script or command that modifies the local system or interacts with local services.

In the context of this lecture, we are using the `local-exec` provisioner to execute an Ansible playbook locally on the machine where the Terraform apply command is being run. This allows us to automate the setup of the server using both Terraform and Ansible.

### How Does Local-exec Work?

The `local-exec` provisioner works by executing a specified command on the local machine where the Terraform apply command is being run. The command is specified using the `command` attribute within the `local-exec` provisioner block.

Here is an example of how to use the `local-exec` provisioner in a Terraform configuration:

```hcl
resource "null_resource" "example" {
  provisioner "local-exec" {
    command = "echo 'Hello, World!'"
  }
}
```

In this example, the `local-exec` provisioner is used to execute the `echo 'Hello, World!'` command on the local machine. This command will be executed after the `null_resource` is created.

### Example: Using Local-exec to Execute an Ansible Playbook

Let's consider a more complex example where we use the `local-exec` provisioner to execute an Ansible playbook. Suppose we have an Ansible playbook located at `/path/to/playbook/deploy_docker.yml`. We want to execute this playbook using the `local-exec` provisioner in our Terraform configuration.

Here is how you can achieve this:

```hcl
resource "null_resource" "ansible_playbook" {
  provisioner "local-exec" {
    command = "ansible-playbook /path/to/playbook/deploy_docker.yml"
  }
}
```

In this example, the `local-exec` provisioner is used to execute the `ansible-playbook` command with the specified playbook path. This command will be executed on the local machine where the Terraform apply command is being run.

### Handling Long Paths and Complex Commands

When dealing with long paths and complex commands, it is important to ensure that the command is properly formatted and that all necessary paths are correctly specified. In the given transcript, the path to the Ansible playbook is specified as `Ansible folder, and then deploy Docker, new user.net`. This path is quite long and may not be easily readable or maintainable.

To handle this, you can use variables in your Terraform configuration to store the path to the playbook. This makes the configuration more readable and maintainable. Here is an example of how to use variables to store the path to the playbook:

```hcl
variable "ansible_playbook_path" {
  default = "/path/to/playbook/deploy_docker.yml"
}

resource "null_resource" "ansible_playbook" {
  provisioner "local-exec" {
    command = "ansible-playbook ${var.ansible_playbook_path}"
  }
}
```

In this example, the path to the playbook is stored in a variable called `ansible_playbook_path`. This variable is then used in the `command` attribute of the `local-exec` provisioner. This makes the configuration more readable and maintainable.

### Pitfalls and Best Practices

When using the `local-exec` provisioner, there are several pitfalls and best practices to keep in mind:

1. **Ensure the Command Works Locally**: Make sure that the command you are executing works correctly on the local machine where the Terraform apply command is being run. Test the command outside of Terraform to ensure it behaves as expected.

2. **Use Variables for Paths**: Use variables to store paths and other configuration details. This makes the configuration more readable and maintainable.

3. **Handle Errors Gracefully**: Ensure that the command handles errors gracefully. You can use conditional statements or error handling mechanisms in the command to handle errors appropriately.

4. **Secure the Environment**: Ensure that the local environment where the command is being executed is secure. Avoid executing commands that could potentially harm the local system or expose sensitive information.

### Real-World Examples and Recent CVEs

While the `local-exec` provisioner itself does not directly relate to specific CVEs or breaches, it is important to understand the potential security implications of executing commands locally. For example, if the command being executed is not properly validated or sanitized, it could potentially be exploited to execute arbitrary code on the local machine.

One recent example of a security issue related to command execution is the CVE-2021-44228, also known as Log4Shell. This vulnerability allowed attackers to execute arbitrary code on systems using the Apache Log4j library. While this vulnerability is not directly related to the `local-exec` provisioner, it highlights the importance of ensuring that any command being executed is properly validated and sanitized.

### How to Prevent / Defend

To prevent and defend against potential security issues when using the `local-exec` provisioner, follow these best practices:

1. **Validate and Sanitize Inputs**: Ensure that any inputs to the command are properly validated and sanitized. Avoid using untrusted input directly in the command.

2. **Use Least Privilege**: Run the command with the least privilege necessary. Avoid running the command with elevated privileges unless absolutely necessary.

3. **Monitor and Audit**: Monitor and audit the execution of the command. Use logging and monitoring tools to track the execution of the command and detect any suspicious activity.

4. **Secure the Environment**: Ensure that the local environment where the command is being executed is secure. Use security best practices to protect the local system from potential threats.

### Conclusion

The `local-exec` provisioner in Terraform is a powerful tool that allows you to execute commands locally on the machine where the Terraform apply command is being run. By using the `local-exec` provisioner, you can automate the setup of your server using both Terraform and Ansible. However, it is important to follow best practices and security guidelines to ensure that the command is executed securely and effectively.

### Practice Labs

For hands-on practice with Terraform and Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover web application security, including some that involve using Terraform and Ansible.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice various security techniques, including infrastructure as code with Terraform and Ansible.
- **DVWA (Damn Vulnerable Web Application)**: Another deliberately insecure web application that can be used to practice various security techniques, including infrastructure as code with Terraform and Ansible.

These labs provide a practical way to apply the concepts learned in this lecture and gain hands-on experience with Terraform and Ansible.

---
<!-- nav -->
[[01-Introduction to Automating Server Setup with Terraform and Ansible|Introduction to Automating Server Setup with Terraform and Ansible]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/03-Automating Server Setup with Terraform and Ansible/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/03-Automating Server Setup with Terraform and Ansible/03-Automating Server Setup with Terraform and Ansible|Automating Server Setup with Terraform and Ansible]]
