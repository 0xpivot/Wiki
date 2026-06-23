---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Creating an EKS Role Using IAM

### What is EKS?

EKS stands for Elastic Kubernetes Service. It is a managed service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane. EKS provides a highly available and scalable Kubernetes control plane that is fully managed by AWS.

### Why Create an EKS Role?

When you create an EKS cluster, you need to provide an IAM role that has the necessary permissions to interact with various AWS services. This role is used by the EKS control plane to manage resources such as EC2 instances, ELBs, and Auto Scaling groups.

### Steps to Create an EKS Role

1. **Navigate to IAM Console**: Open the AWS Management Console and navigate to the IAM section.
2. **Create a New Role**: Click on "Roles" and then "Create role".
3. **Select Trusted Entity**: Choose "AWS service" as the trusted entity.
4. **Choose EKS Service**: Select "Elastic Kubernetes Service" as the service that will use this role.
5. **Attach Policy**: Attach the "AmazonEKSClusterPolicy" to the role. This policy grants the necessary permissions for the EKS control plane to manage resources.
6. **Name the Role**: Provide a name for the role, such as "eks-cluster-role".
7. **Review and Create**: Review the settings and create the role.

### Detailed Example

Let's walk through the process of creating an EKS role step-by-step:

1. **Navigate to IAM Console**:
   - Open the AWS Management Console.
   - Navigate to the IAM section.

2. **Create a New Role**:
   - Click on "Roles" in the left-hand menu.
   - Click on "Create role".

3. **Select Trusted Entity**:
   - Under "Trusted entity type", select "AWS service".
   - Click "Next: Permissions".

4. **Choose EKS Service**:
   - In the "Use case" section, select "Elastic Kubernetes Service".
   - Click "Next: Tags".

5. **Attach Policy**:
   - In the "Permissions" section, search for "AmazonEKSClusterPolicy".
   - Select the policy and click "Next: Review".

6. **Name the Role**:
   - Provide a name for the role, such as "eks-cluster-role".
   - Optionally, add tags for better organization.

7. **Review and Create**:
   - Review the settings and click "Create role".

### Full Raw HTTP Request and Response

Here is an example of the HTTP request and response for creating an IAM role via the AWS CLI:

```http
POST / HTTP/1.1
Host: iam.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/iam/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5fbd6c702c6b922c18f4f2d41c95d450de4c9c7b2f3c4d50120e2e5a737e4b
X-Amz-Date: 20150101T000000Z
Content-Length: 123

Action=CreateRole&RoleName=eks-cluster-role&AssumeRolePolicyDocument={"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":["eks.amazonaws.com"]},"Action":["sts:AssumeRole"]}]}&PolicyArn=arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 123

{
  "Role": {
    "Path": "/",
    "RoleName": "eks-cluster-role",
    "RoleId": "AROAEXAMPLE1234567890",
    "Arn": "arn:aws:iam::123456789012:role/eks-cluster-role",
    "CreateDate": "2023-01-01T00:00:00Z",
    "AssumeRolePolicyDocument": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": [
              "eks.amazonaws.com"
            ]
          },
          "Action": [
            "sts:AssumeRole"
          ]
        }
      ]
    }
  }
}
```

### Pitfalls of Creating an EKS Role

- **Incorrect Permissions**: Ensure that the attached policy grants the necessary permissions. Incorrect permissions can lead to issues with the EKS control plane.
- **Role Naming**: Use descriptive names for roles to avoid confusion. Avoid generic names like "role1" or "role2".

### How to Prevent / Defend Against EKS Role Risks

#### Detection

- **CloudTrail Logs**: Monitor API calls related to IAM and EKS using CloudTrail logs.
- **IAM Access Advisor**: Use IAM Access Advisor to track which services are being accessed by the role.

#### Prevention

- **Least Privilege Principle**: Attach only the necessary policies to the role.
- **Regular Audits**: Perform regular audits of IAM roles and policies to ensure they remain secure.

#### Secure Coding Fix

**Vulnerable Code:**
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

**Fixed Code:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "elasticloadbalancing:*",
        "autoscaling:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Conclusion

Creating an IAM role for an EKS cluster is a critical step in setting up a secure and functional Kubernetes environment on AWS. By following the steps outlined above and adhering to best practices, you can ensure that your EKS cluster operates smoothly and securely. Always remember to monitor and audit your IAM roles regularly to maintain the highest level of security.

### Practice Labs

For hands-on practice with IAM and EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on IAM and EKS setup.
- **OWASP Juice Shop**: Provides a comprehensive environment for practicing IAM and EKS configurations.
- **DVWA (Damn Vulnerable Web Application)**: Useful for understanding IAM and EKS in a practical context.
- **WebGoat**: Another excellent resource for learning about IAM and EKS security.

By completing these labs, you can gain a deeper understanding of IAM and EKS and apply your knowledge in real-world scenarios.

---
<!-- nav -->
[[10-Creating an EKS Cluster Manually Using AWS Management Console|Creating an EKS Cluster Manually Using AWS Management Console]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/29-Manual EKS Cluster Creation Using AWS Console/00-Overview|Overview]] | [[12-EKS Cluster Creation Using AWS Console|EKS Cluster Creation Using AWS Console]]
