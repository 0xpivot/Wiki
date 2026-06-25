---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of using GitLab OIDC to securely access AWS resources from a GitLab CI pipeline.**

The process involves several key steps:

1. **Create a GitLabCI Role in AWS**: Define a role in AWS that has the necessary permissions to interact with AWS resources such as EKS clusters. This role should have a trust policy that allows GitLab to assume it.

2. **Configure Trust Policy**: The trust policy in AWS should allow GitLab to assume the role. This is achieved by specifying GitLab as a trusted entity in the trust policy.

3. **Use GitLab OIDC Provider**: GitLab acts as an OpenID Connect (OIDC) provider, issuing JSON Web Tokens (JWT) to authenticate requests. These tokens are used to prove the identity of the GitLab CI pipeline to AWS.

4. **Assume Role with Web Identity**: When the pipeline runs, it uses the `assume-role-with-web-identity` command from AWS Security Token Service (STS). This command takes the JWT issued by GitLab and assumes the role defined in AWS, providing temporary credentials to the pipeline.

5. **Execute Terraform Commands**: With the temporary credentials, the pipeline can execute Terraform commands to provision and manage AWS resources securely.

This method ensures that static AWS credentials are not stored in the pipeline, enhancing security by using temporary, role-based access.

**Q2. How does the use of short-lived tokens enhance security in a GitLab CI pipeline accessing AWS resources?**

Short-lived tokens enhance security in several ways:

1. **Limited Exposure Time**: Short-lived tokens reduce the window of opportunity for unauthorized access. If a token is compromised, it can only be used for a brief period before it expires.

2. **Role-Based Access Control**: Tokens are typically associated with specific roles that have limited permissions. This ensures that even if a token is compromised, the attacker’s access is restricted to the permissions granted to that role.

3. **Auditability**: Since tokens are short-lived, they can be easily audited and revoked if necessary. This helps in quickly mitigating any potential security breaches.

4. **Compliance**: Many compliance standards require the use of temporary credentials to limit exposure to sensitive systems. Short-lived tokens help meet these requirements.

For example, in the context of provisioning an EKS cluster, a short-lived token might be used to assume a role with permissions to create and manage the cluster. Once the operation is complete, the token expires, reducing the risk of long-term unauthorized access.

**Q3. Compare the use of SSM for deploying to EC2 instances with the use of GitLab OIDC for provisioning EKS clusters. What are the advantages of the latter approach?**

**SSM for EC2 Deployment**:
- **Limited Scope**: SSM is primarily designed for managing EC2 instances and related services like RDS.
- **Instance-Specific**: Requires the GitLab runner to run on an EC2 instance with an assigned IAM role.
- **Less Flexible**: Less flexible as it ties the deployment process to specific EC2 infrastructure.

**GitLab OIDC for EKS Clusters**:
- **Generic Approach**: Works for any AWS service, not just EC2 instances.
- **Flexible Infrastructure**: Can use shared runners or runners on any infrastructure, not tied to EC2.
- **Enhanced Security**: Uses short-lived tokens and role-based access control, reducing the risk of credential exposure.
- **Centralized Management**: Simplifies management by centralizing authentication and authorization processes.

Advantages of GitLab OIDC:
- **Broader Applicability**: Suitable for a wider range of AWS services beyond EC2.
- **Increased Flexibility**: Not dependent on specific AWS infrastructure.
- **Improved Security**: Reduces the risk of credential misuse through short-lived tokens and strict role definitions.

**Q4. How would you configure a trust policy in AWS to allow GitLab to assume a role? Provide an example of the trust policy JSON.**

To configure a trust policy in AWS that allows GitLab to assume a role, you need to specify GitLab as a trusted entity. Here is an example of how the trust policy JSON might look:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:<org>/<repo>:ref:refs/heads/<branch>"
        }
      }
    }
  ]
}
```

Replace `<account-id>` with your AWS account ID, and `<org>/<repo>:ref:refs/heads/<branch>` with the appropriate values for your GitLab repository and branch.

This trust policy specifies that the role can be assumed by a principal federated via the specified OIDC provider (`token.actions.githubusercontent.com`), with conditions ensuring that the request comes from a specific GitHub Actions workflow.

**Q5. Describe the steps involved in configuring a Terraform state to be hosted remotely in an S3 bucket for a GitLab CI pipeline.**

Configuring a Terraform state to be hosted remotely in an S3 bucket involves the following steps:

1. **Create an S3 Bucket**: Create an S3 bucket to store the Terraform state file. Ensure the bucket name is unique and follows AWS naming conventions.

2. **Set Up IAM Permissions**: Configure IAM permissions to allow the GitLab CI pipeline to read and write to the S3 bucket. This typically involves creating an IAM role with appropriate permissions and attaching it to the GitLab runner.

3. **Configure Terraform Backend**: Update the `backend` configuration in your `terraform.tf` file to point to the S3 bucket. For example:

   ```hcl
   terraform {
     backend "s3" {
       bucket = "<bucket-name>"
       key    = "<path-to-state-file>"
       region = "<aws-region>"
     }
   }
   ```

4. **Initialize Terraform**: Run `terraform init` in your pipeline to initialize the backend configuration and ensure Terraform is pointing to the correct S3 bucket.

5. **Run Terraform Commands**: Use the `terraform plan`, `terraform apply`, and other commands in your pipeline to manage your infrastructure. Ensure that the pipeline has the necessary credentials to access the S3 bucket.

By hosting the Terraform state in an S3 bucket, you centralize the state management, making it accessible to multiple pipelines and ensuring consistency across different environments.

**Q6. How does the use of a role in the GitLab CI pipeline prevent full admin access to the Kubernetes cluster?**

Using a role in the GitLab CI pipeline prevents full admin access to the Kubernetes cluster by leveraging temporary, role-based access control:

1. **Temporary Credentials**: The role assumes temporary credentials via the `assume-role-with-web-identity` command, which expire after a short period. This limits the exposure time for any potential unauthorized access.

2. **Role-Based Permissions**: The role is defined with specific permissions that are necessary for the pipeline tasks, rather than full admin access. This ensures that even if the role is compromised, the damage is limited to the actions allowed by the role.

3. **Pipeline Duration Limitation**: The role’s permissions are active only during the pipeline execution. Once the pipeline completes, the temporary credentials expire, effectively revoking access.

4. **Audit and Revocation**: The use of roles allows for easier auditing and revocation of access if necessary. This enhances security by providing a clear audit trail and quick response mechanisms in case of security incidents.

By using a role with limited permissions and temporary credentials, the GitLab CI pipeline ensures that the Kubernetes cluster remains secure and that full admin access is not granted to the pipeline, reducing the risk of unauthorized access and misuse.

---
<!-- nav -->
[[06-Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS|Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Using GitLab OIDC in AWS/00-Overview|Overview]]
