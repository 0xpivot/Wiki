---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What are the main differences between creating and managing DigitalOcean Droplets and AWS EC2 instances?**

The main differences between creating and managing DigitalOcean Droplets and AWS EC2 instances include:

- **Key Pair Management**: In AWS, you need to manage key pairs explicitly, either by selecting an existing key pair or creating a new one. This key pair is used to SSH into the instances. In contrast, DigitalOcean allows you to provide your own SSH key during the creation process, simplifying the setup.
  
- **Instance Configuration**: AWS provides a more extensive configuration interface, allowing you to customize various aspects of the instance such as security groups, IAM roles, and network settings. DigitalOcean offers a simpler, streamlined configuration process but still provides essential options like choosing the region and size of the droplet.

- **User Management**: By default, AWS EC2 instances use a specific user (e.g., `ec2-user`), while DigitalOcean typically uses the `root` user unless specified otherwise. This means you need to specify the correct user when configuring SSH access in tools like Ansible.

- **DNS Names**: AWS provides DNS names for each instance, which can be used in the Ansible hosts file alongside IP addresses. DigitalOcean primarily uses IP addresses, although custom domain names can be added through DigitalOcean's DNS management.

**Q2. How do you configure SSH access to AWS EC2 instances using Ansible?**

To configure SSH access to AWS EC2 instances using Ansible, follow these steps:

1. **Create Key Pair**: When launching the EC2 instances, create or select a key pair. Download the private key file (`.pem`).

2. **Modify Key Permissions**: Ensure the private key file has strict permissions (`chmod 400 key.pem`).

3. **Configure Ansible Inventory**: Add the EC2 instances to the Ansible inventory file. Use the public DNS names or IP addresses of the instances.

    ```yaml
    [EC2]
    ec2-instance-1-public-dns
    ec2-instance-2-public-dns
    ```

4. **Set Up User and Key File**: Define the user and key file in the Ansible inventory file.

    ```yaml
    [EC2:vars]
    ansible_user=ec2-user
    ansible_ssh_private_key_file=/path/to/key.pem
    ```

5. **Test Connection**: Use Ansible to test the connection to the instances.

    ```bash
    ansible all -m ping -i inventory.yml
    ```

**Q3. Why is it important to install Python 3 on EC2 instances for Ansible operations?**

It is important to install Python 3 on EC2 instances for Ansible operations because:

- **Compatibility**: Many modern Ansible modules and plugins require Python 3. Using Python 3 ensures compatibility with the latest features and improvements in Ansible.

- **Security**: Python 2 reached its end-of-life in January 2020, meaning it no longer receives security updates. Running Ansible with Python 2 can expose your environment to potential security risks.

- **Functionality**: Some advanced Ansible functionalities and modules may not work correctly or at all with Python 2. Installing Python 3 ensures full support for these features.

To install Python 3 on an EC2 instance, you can use the package manager appropriate for your Linux distribution. For example, on Amazon Linux, you can use `yum`:

```bash
sudo yum install python3
```

After installation, you can verify the Python version:

```bash
python3 --version
```

**Q4. How would you troubleshoot and resolve the warning related to the Python interpreter when using Ansible with EC2 instances?**

To troubleshoot and resolve the warning related to the Python interpreter when using Ansible with EC2 instances, follow these steps:

1. **Check Python Version**: Verify the Python version being used by Ansible on the target instances.

    ```bash
    ansible all -m raw -a 'python --version' -i inventory.yml
    ```

2. **Install Python 3**: If Python 3 is not installed, install it using the appropriate package manager for your Linux distribution.

    ```bash
    sudo yum install python3
    ```

3. **Override Python Interpreter in Ansible Inventory**: Specify the Python interpreter in the Ansible inventory file to ensure Ansible uses Python 3.

    ```yaml
    [EC2:vars]
    ansible_python_interpreter=/usr/bin/python3
    ```

4. **Test Connection Again**: Re-run the Ansible command to ensure the warning is resolved.

    ```bash
    ansible all -m ping -i inventory.yml
    ```

By following these steps, you can ensure that Ansible operates smoothly with the correct Python interpreter on your EC2 instances.

**Q5. Explain how to terminate and remove EC2 instances after completing your tasks.**

To terminate and remove EC2 instances after completing your tasks, follow these steps:

1. **Log Out from Instances**: Ensure you are logged out of any active sessions on the EC2 instances.

2. **Terminate Instances via AWS Console**:
   - Go to the EC2 Dashboard in the AWS Management Console.
   - Select the instances you want to terminate.
   - Click on the "Actions" menu, then select "Instance State" > "Terminate".

3. **Verify Termination**:
   - Check the instance status in the console to confirm they are terminated.
   - Once terminated, the instances will no longer incur charges.

4. **Clean Up Resources**:
   - Remove the instances from your Ansible inventory file.
   - Delete any associated key pairs if they are no longer needed.

By following these steps, you can effectively manage and clean up your EC2 resources, ensuring that you do not incur unnecessary costs and maintain a tidy environment.

---
<!-- nav -->
[[02-Introduction to DigitalOcean Droplets and AWS EC2 Instances|Introduction to DigitalOcean Droplets and AWS EC2 Instances]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/11-Comparing Digital Ocean Droplets with AWS EC2 Instances/00-Overview|Overview]]
