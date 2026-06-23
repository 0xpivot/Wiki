---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Pitfalls and Best Practices

### Common Mistakes

1. **Misconfigured Security Groups**: Failing to properly configure security groups can lead to unauthorized access.
2. **Exposed Private Keys**: Losing control of the private key associated with your EC2 instance can compromise security.
3. **Unsecured Docker Repositories**: Using unsecured Docker repositories can expose your application to vulnerabilities.

### Best Practices

1. **Use Strong Security Groups**: Ensure that security groups are configured to allow only necessary traffic.
2. **Protect Private Keys**: Securely store and manage private keys associated with EC2 instances.
3. **Use Secure Docker Repositories**: Use secure and trusted Docker repositories to avoid vulnerabilities.

### How to Prevent / Defend

#### Detection

1. **Monitor Security Groups**: Regularly review and audit security group configurations to ensure they are correctly set.
2. **Monitor Network Traffic**: Use AWS CloudWatch and VPC Flow Logs to monitor network traffic and detect unusual activity.

#### Prevention

1. **Use IAM Roles**: Assign IAM roles to EC2 instances to control access to AWS resources.
2. **Enable SSH Key Rotation**: Regularly rotate SSH keys to minimize the risk of exposure.

#### Secure Coding Fixes

1. **Vulnerable Code**:
    ```bash
    ssh -i "my-key-pair.pem" ec2-user@<public-ip-address>
    ```
2. **Fixed Code**:
    ```bash
    ssh -i "my-key-pair.pem" ec2-user@<public-ip-address> -o "StrictHostKeyChecking=no"
    ```

#### Configuration Hardening

1. **IAM Policy Example**:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeInstances",
                    "ec2:RunInstances"
                ],
                "Resource": "*"
            }
        ]
    }
    ```

2. **Security Group Configuration**:
    ```json
    {
        "IpPermissions": [
            {
                "FromPort": 80,
                "ToPort": 80,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0"
                    }
                ]
            }
        ]
    }
    ```

---
<!-- nav -->
[[13-Key Pairs in AWS EC2|Key Pairs in AWS EC2]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/15-Deploying Web Applications Using EC2 Instances/00-Overview|Overview]] | [[15-Practice Labs|Practice Labs]]
