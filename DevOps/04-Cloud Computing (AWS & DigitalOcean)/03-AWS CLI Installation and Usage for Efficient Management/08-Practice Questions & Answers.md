---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the benefits of using AWS CLI over the AWS Management Console.**

Using AWS CLI offers several advantages over the AWS Management Console:

1. **Automation**: Scripts can automate repetitive tasks, reducing manual effort and minimizing human errors.
2. **Efficiency**: CLI commands can be executed much faster than navigating through a GUI, especially for bulk operations.
3. **Consistency**: Scripts ensure consistent execution of tasks across environments, making it ideal for CI/CD pipelines.
4. **Flexibility**: CLI allows for greater flexibility in scripting and integrating with other tools and services.
5. **Programmatic Access**: CLI enables programmatic access to AWS services, which is essential for applications that require dynamic resource management.

**Q2. How do you install AWS CLI on macOS? Provide the necessary commands.**

To install AWS CLI on macOS, you can use Homebrew. Follow these steps:

1. Ensure Homebrew is installed. If not, install it with:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Update Homebrew:
   ```bash
   brew update
   ```
3. Install AWS CLI:
   ```bash
   brew install awscli
   ```

**Q3. What are the steps to configure AWS CLI with your AWS credentials?**

Configuring AWS CLI involves setting up your AWS access key ID and secret access key. Here’s how to do it:

1. Run the `aws configure` command:
   ```bash
   aws configure
   ```
2. Enter your AWS Access Key ID when prompted.
3. Enter your AWS Secret Access Key when prompted.
4. Specify the default region name (e.g., `us-west-2`).
5. Set the default output format (e.g., `json`).

Alternatively, you can set these values directly using environment variables or by editing the `~/.aws/credentials` and `~/.aws/config` files.

**Q4. How would you create a new EC2 instance using AWS CLI, including specifying the security group and key pair?**

To create a new EC2 instance using AWS CLI, you need to specify the AMI ID, instance type, key pair, security group, and subnet. Here’s an example command:

```bash
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --count 1 \
    --instance-type t2.micro \
    --key-name my-key-pair \
    --security-group-ids sg-0123456789abcdef0 \
    --subnet-id subnet-0123456789abcdef0
```

Replace `ami-0abcdef1234567890`, `sg-0123456789abcdef0`, and `subnet-0123456789abcdef0` with the appropriate values for your setup.

**Q5. How can you filter and query EC2 instances using AWS CLI?**

You can use the `describe-instances` command with filters and queries to retrieve specific information about EC2 instances. Here’s an example:

```bash
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].[InstanceId,InstanceType]'
```

This command retrieves the instance IDs and types of all running instances.

**Q6. How do you create a new IAM user and assign a policy to it using AWS CLI?**

Creating a new IAM user and assigning a policy involves several steps:

1. Create the user:
   ```bash
   aws iam create-user --user-name my-new-user
   ```
2. Attach a policy to the user:
   ```bash
   aws iam attach-user-policy \
       --user-name my-new-user \
       --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
   ```

Replace `my-new-user` with the desired username and adjust the policy ARN as needed.

**Q7. How can you switch between different AWS users when using AWS CLI?**

Switching between different AWS users can be done using environment variables or by reconfiguring the CLI:

1. Using environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=<access_key_id>
   export AWS_SECRET_ACCESS_KEY=<secret_access_key>
   export AWS_DEFAULT_REGION=<region>
   ```

2. Reconfigure the CLI:
   ```bash
   aws configure set aws_access_key_id <access_key_id>
   aws configure set aws_secret_access_key <secret_access_key>
   aws configure set default.region <region>
   ```

Replace `<access_key_id>`, `<secret_access_key>`, and `<region>` with the appropriate values for the desired user.

**Q8. What are the steps to delete an EC2 instance and associated resources using AWS CLI?**

Deleting an EC2 instance and associated resources involves several steps:

1. Terminate the instance:
   ```bash
   aws ec2 terminate-instances --instance-ids i-0123456789abcdef0
   ```
2. Delete the key pair:
   ```bash
   aws ec2 delete-key-pair --key-name my-key-pair
   ```
3. Delete the security group:
   ```bash
   aws ec2 delete-security-group --group-id sg-01122334455667788
   ```

Replace `i-0123456789abcdef0`, `my-key-pair`, and `sg--01122334455667788` with the appropriate values for your setup.

**Q9. How can you create a new IAM group and add a user to it using AWS CLI?**

Creating a new IAM group and adding a user involves the following steps:

1. Create the group:
   ```bash
   aws iam create-group --group-name my-new-group
   ```
2. Add a user to the group:
   ```bash
   aws iam add-user-to-group --user-name my-user --group-name my-new-group
   ```

Replace `my-new-group` and `my-user` with the appropriate names for your setup.

**Q10. How can you create a new IAM policy and attach it to a group using AWS CLI?**

Creating a new IAM policy and attaching it to a group involves the following steps:

1. Create the policy:
   ```bash
   aws iam create-policy \
       --policy-name my-policy \
       --policy-document file://path/to/my-policy.json
   ```
2. Attach the policy to the group:
   ```bash
   aws iam attach-group-policy \
       --group-name my-group \
       --policy-arn arn:aws:iam::<account-id>:policy/my-policy
   ```

Replace `my-policy`, `my-group`, and `<account-id>` with the appropriate values for your setup.

---
<!-- nav -->
[[07-User Permission Grouping in AWS IAM|User Permission Grouping in AWS IAM]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/03-AWS CLI Installation and Usage for Efficient Management/00-Overview|Overview]]
