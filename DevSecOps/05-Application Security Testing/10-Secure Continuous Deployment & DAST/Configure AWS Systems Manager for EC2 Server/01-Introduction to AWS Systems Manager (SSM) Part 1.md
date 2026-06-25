---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is a powerful tool designed to help manage your Amazon Elastic Compute Cloud (EC2) instances, including configuration management, patch management, and remote command execution. SSM provides a unified console and API to manage your infrastructure efficiently and securely. This chapter will delve into configuring SSM for EC2 servers, explaining the necessary steps, underlying mechanisms, and security considerations.

### What is AWS Systems Manager?

AWS Systems Manager is a collection of capabilities that helps you automate operational tasks such as managing configurations, performing updates, and executing commands across your managed instances. It simplifies the process of maintaining and securing your infrastructure by providing a centralized interface for various management tasks.

#### Why Use AWS Systems Manager?

1. **Centralized Management**: SSM allows you to manage multiple EC2 instances from a single console, reducing the complexity of managing individual instances.
2. **Automation**: You can automate routine tasks like software patching, configuration changes, and command execution, saving time and reducing human error.
3. **Security**: SSM provides secure methods for accessing and managing your instances, ensuring that your infrastructure remains protected.

### Prerequisites for Using SSM

Before diving into the configuration process, ensure that your EC2 instances meet the following prerequisites:

1. **IAM Role**: Your EC2 instances must have an IAM role attached that grants permissions to use SSM.
2. **SSM Agent**: The SSM agent must be installed and running on your EC2 instances.
3. **Network Configuration**: Ensure that your instances can communicate with the SSM endpoint.

### Installing and Verifying the SSM Agent

The SSM agent is a lightweight daemon that runs on your EC2 instances and communicates with the SSM service. To verify that the SSM agent is installed and running, follow these steps:

1. **SSH Access**: Temporarily enable SSH access to your EC2 instance.
2. **Check SSM Agent Status**:
    ```sh
    sudo systemctl status amazon-ssm-agent
    ```

This command checks the status of the SSM agent service. If the agent is installed and running, you should see output similar to the following:

```plaintext
● amazon-ssm-agent.service - Amazon SSM Agent
   Loaded: loaded (/etc/systemd/system/amazon-ssm-agent.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2023-10-02 12:00:00 UTC; 1 day ago
 Main PID: 1234 (amazon-ssm-agent)
    Tasks: 5 (limit: 4915)
   Memory: 12.3M
   CGroup: /system.slice/amazon-ssm-agent.service
           └─1234 /usr/bin/amazon-ssm-agent
```

If the agent is not running, you can start it using the following command:

```sh
sudo systemctl start amazon-ssm-agent
```

To ensure the agent starts automatically on boot, enable it with:

```sh
sudo systemctl enable amazon-ssm-agent
```

### Configuring IAM Role for SSM

For SSM to function correctly, your EC2 instances must have an IAM role attached that grants the necessary permissions. Here’s how to configure the IAM role:

1. **Create an IAM Role**:
    - Navigate to the IAM console.
    - Click on "Roles" and then "Create role".
    - Choose "EC2" as the trusted entity.
    - Attach the `AmazonSSMManagedInstanceCore` policy to the role.

2. **Attach the IAM Role to Your EC2 Instance**:
    - Go to the EC2 console.
    - Select the instance and click on "Actions" > "Security" > "Modify IAM role".
    - Attach the IAM role you created.

### Network Configuration for SSM

Ensure that your EC2 instances can communicate with the SSM endpoint. This typically involves configuring security groups and network ACLs.

1. **Security Groups**:
    - Add rules to your security group to allow inbound traffic on port 443 (HTTPS) from the SSM endpoint.
    - Add rules to allow outbound traffic on port 443 to the SSM endpoint.

2. **Network ACLs**:
    - Ensure that your network ACLs allow inbound and outbound traffic on port 443.

### Verifying SSM Connectivity

Once the SSM agent is installed and the IAM role is configured, you can verify connectivity to the SSM service.

1. **Connect to the EC2 Instance via SSM**:
    - Open the SSM console.
    - Click on "Session Manager" and then "Start session".
    - Select your EC2 instance and click "Start session".

If the session starts successfully, it indicates that your instance is properly configured to use SSM.

### Common Pitfalls and How to Avoid Them

#### Pitfall 1: Incorrect IAM Role Permissions

**Problem**: If the IAM role attached to your EC2 instance does not have the necessary permissions, SSM operations may fail.

**Solution**: Ensure that the IAM role has the `AmazonSSMManagedInstanceCore` policy attached. You can also attach additional policies if needed.

#### Pitfall 2: Network Configuration Issues

**Problem**: If your EC2 instance cannot communicate with the SSM endpoint due to incorrect network settings, SSM operations will fail.

**Solution**: Verify that your security groups and network ACLs allow traffic on port 443 to and from the SSM endpoint.

### Real-World Example: Recent Breach Involving SSM Misconfiguration

In a recent breach, an organization experienced unauthorized access to their EC2 instances due to misconfigured SSM settings. The attackers were able to execute commands on the instances because the IAM role attached to the instances had excessive permissions.

**Example**:
- **Vulnerable IAM Policy**:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }
    ```
- **Secure IAM Policy**:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:*",
                    "ec2messages:*",
                    "cloudwatch:PutMetricData",
                    "cloudwatch:GetMetricData",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:DescribeAlarms",
                    "cloudwatch:PutMetricAlarm",
                    "cloudwatch:DeleteAlarms",
                    "cloudwatch:SetAlarmState",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                    "logs:GetLogEvents",
                    "logs:FilterLogEvents",
                    "logs:TestMetricFilter",
                    "logs:PutRetentionPolicy",
                    "logs:DeleteLogGroup",
                    "logs:DeleteLogStream",
                    "logs:DescribeMetricFilters",
                    "logs:PutMetricFilter",
                    "logs:DeleteMetricFilter",
                    "logs:DescribeSubscriptionFilters",
                    "logs:PutSubscriptionFilter",
                    "logs:DeleteSubscriptionFilter",
                    "logs:DescribeLogGroups",
                    "logs:DescribeQueries",
                    "logs:GetQueryResults",
                    "logs:StartQuery",
                    "logs:StopQuery",
                    "logs:DeleteQueryDefinition",
                    "logs:DescribeQueryDefinitions",
                    "logs:PutQueryDefinition",
                    "logs:UpdateQueryDefinition",
                    "logs:TagLogGroup",
                    "logs:UntagLogGroup",
                    "logs:DescribeTags",
                    "logs:AssociateKmsKey",
                    "logs:DisassociateKmsKey",
                    "logs:DescribeExportTasks",
                    "logs:CreateExportTask",
                    "logs:CancelExportTask",
                    "logs:DescribeMetricFilters",
                    "logs:PutMetricFilter",
                    "logs:DeleteMetricFilter",
                    "logs:DescribeSubscriptionFilters",
                    "logs:PutSubscriptionFilter",
                    "logs:DeleteSubscriptionFilter",
                    "logs:DescribeLogGroups",
                    "logs:DescribeQueries",
                    "logs:GetQueryResults",
                    "logs:StartQuery",
                    "logs:StopQuery",
                    "logs:DeleteQueryDefinition",
                    "logs:DescribeQueryDefinitions",
                    "logs:PutQueryDefinition",
                    "logs:UpdateQueryDefinition",
                    "logs:TagLogGroup",
                    "logs:UntagLogGroup",
                    "logs:DescribeTags",
                    "logs:AssociateKmsKey",
                    "logs:DisassociateKmsKey",
                    "logs:DescribeExportTasks",
                    "logs:CreateExportTask",
                    "logs:CancelExportTask"
                ],
                "Resource": "*"
            }
        ]
    }
    ```

### How to Prevent / Defend Against SSM Misconfigurations

#### Detection

1. **Audit IAM Roles**: Regularly audit the IAM roles attached to your EC2 instances to ensure they have the minimum necessary permissions.
2. **Monitor SSM Activity**: Use CloudTrail to monitor SSM activity and detect any unauthorized actions.

#### Prevention

1. **Least Privilege Principle**: Follow the least privilege principle when assigning permissions to IAM roles.
2. **Network Segmentation**: Use network segmentation to limit the exposure of your EC2 instances to the SSM endpoint.

#### Secure Coding Fixes

1. **IAM Role Configuration**:
    - **Vulnerable Code**:
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                }
            ]
        }
        ```
    - **Secure Code**:
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ssm:*",
                        "ec2messages:*",
                        "cloudwatch:PutMetricData",
                        "cloudwatch:GetMetricData",
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                        "cloudwatch:DescribeAlarms",
                        "cloudwatch:PutMetricAlarm",
                        "cloudwatch:DeleteAlarms",
                        "cloudwatch:SetAlarmState",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:DescribeLogStreams",
                        "logs:GetLogEvents",
                        "logs:FilterLogEvents",
                        "logs:TestMetricFilter",
                        "logs:PutRetentionPolicy",
                        "logs:DeleteLogGroup",
                        "logs:DeleteLogStream",
                        "logs:DescribeMetricFilters",
                        "logs:PutMetricFilter",
                        "logs:DeleteMetricFilter",
                        "logs:DescribeSubscriptionFilters",
                        "logs:PutSubscriptionFilter",
                        "logs:DeleteSubscriptionFilter",
                        "logs:DescribeLogGroups",
                        "logs:DescribeQueries",
                        "logs:GetQueryResults",
                        "logs:StartQuery",
                        "logs:StopQuery",
                        "logs:DeleteQueryDefinition",
                        "logs:DescribeQueryDefinitions",
                        "logs:PutQueryDefinition",
                        "logs:UpdateQueryDefinition",
                        "logs:TagLogGroup",
                        "logs:UntagLogGroup",
                        "logs:DescribeTags",
                        "logs:AssociateKmsKey",
                        "logs:DisassociateKmsKey",
                        "logs:DescribeExportTasks",
                        "logs:CreateExportTask",
                        "logs:CancelExportTask"
                    ],
                    "Resource": "*"
                }
            ]
        }
        ```

### Conclusion

Configuring AWS Systems Manager for EC2 servers is a critical step in managing and securing your infrastructure. By following the steps outlined in this chapter, you can ensure that your instances are properly configured to use SSM, reducing the risk of unauthorized access and improving overall security.

### Practice Labs

To gain hands-on experience with configuring AWS Systems Manager, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a range of labs focused on web application security, including some that touch on AWS security practices.
- **CloudGoat**: A cloud security training platform that includes scenarios for configuring and securing AWS resources, including SSM.

By completing these labs, you can reinforce your understanding of the concepts covered in this chapter and gain practical experience with AWS Systems Manager.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/02-Introduction to AWS Systems Manager (SSM)|Introduction to AWS Systems Manager (SSM)]]
