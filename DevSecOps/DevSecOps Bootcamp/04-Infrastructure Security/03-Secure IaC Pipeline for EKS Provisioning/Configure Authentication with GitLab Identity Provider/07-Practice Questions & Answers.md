---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of using GitLab as an Identity Provider for AWS authentication.**

The purpose of using GitLab as an Identity Provider (IdP) for AWS authentication is to enable secure and automated access to AWS resources from GitLab pipelines without needing to manage long-term static credentials. By leveraging GitLab's OpenID Connect (OIDC) provider, GitLab can issue temporary credentials to AWS, allowing the pipeline to perform actions such as provisioning infrastructure via Terraform. This approach enhances security by ensuring that credentials are temporary and tied to the pipeline execution context, reducing the risk of credential exposure and misuse.

**Q2. How would you configure a GitLab pipeline to retrieve temporary AWS credentials using GitLab's OIDC provider?**

To configure a GitLab pipeline to retrieve temporary AWS credentials using GitLab's OIDC provider, follow these steps:

1. **Create a Role in AWS:**
   - Go to the IAM console in AWS.
   - Create a new role for the GitLab OIDC provider.
   - Select "Web Identity" and choose "GitLab.com" as the provider.
   - Define the audience (client ID) and thumbprint for the OIDC provider.
   - Attach the necessary policies to the role to grant permissions for the tasks the pipeline will perform (e.g., `AdministratorAccess` for full access).

2. **Configure GitLab Pipeline:**
   - In your GitLab project, go to the CI/CD settings and add a new variable named `AWS_ROLE_ARN` with the value being the ARN of the role created in AWS.
   - Use the `aws-cli` Docker image in your `.gitlab-ci.yml` file to interact with AWS.
   - Use the `aws sts assume-role-with-web-identity` command to retrieve temporary credentials.

Here is an example `.gitlab-ci.yml` snippet:

```yaml
stages:
  - build

variables:
  AWS_ROLE_ARN: "arn:aws:iam::123456789012:role/GitLabCI"

build:
  stage: build
  image: amazon/aws-cli
  script:
    - aws sts assume-role-with-web-identity --role-arn $AWS_ROLE_ARN --role-session-name GitLabSession --web-identity-token $(curl -s https://gitlab.com/api/v4/jwt/user | jq -r .token)
```

This script retrieves a JWT token from GitLab and uses it to assume the role in AWS, obtaining temporary credentials.

**Q3. Why is it important to use temporary credentials in GitLab pipelines for AWS interactions?**

Using temporary credentials in GitLab pipelines for AWS interactions is crucial for several reasons:

1. **Security:** Temporary credentials reduce the risk of long-term credential exposure. If a credential is compromised, it is only valid for a limited time, minimizing potential damage.
   
2. **Least Privilege Principle:** Temporary credentials can be scoped to provide just enough permissions to complete the task at hand, adhering to the least privilege principle. This minimizes the attack surface and reduces the impact of a breach.

3. **Auditability:** Temporary credentials make it easier to track and audit access to AWS resources. Each set of credentials is tied to a specific pipeline run, making it straightforward to trace actions back to the pipeline that executed them.

4. **Compliance:** Many compliance standards require the use of temporary credentials for automated systems. Using temporary credentials helps meet these requirements and ensures that the organization remains compliant.

**Q4. What recent real-world examples demonstrate the importance of secure authentication mechanisms in DevOps pipelines?**

One notable example is the incident involving the Travis CI service in 2019. A vulnerability in the Travis CI system exposed secrets stored in environment variables, including AWS access keys and other sensitive information. This led to unauthorized access to AWS accounts and the potential compromise of infrastructure managed by the affected projects.

In this case, using temporary credentials and secure authentication mechanisms such as GitLab's OIDC provider would have mitigated the risk. The temporary nature of the credentials would have limited the exposure even if they were leaked, and the use of OIDC would have ensured that the credentials were tightly controlled and validated by the IdP.

Another example is the SolarWinds supply chain attack in 2020, where attackers gained access to the build pipeline and inserted malicious code into software updates. Secure authentication mechanisms, including the use of temporary credentials and multi-factor authentication, could have helped detect and prevent such unauthorized access.

**Q5. How does the use of GitLab's OIDC provider enhance the security of GitLab pipelines interacting with AWS?**

The use of GitLab's OIDC provider enhances the security of GitLab pipelines interacting with AWS in several ways:

1. **Temporary Credentials:** The OIDC provider issues temporary credentials that are valid only for the duration of the pipeline run. Once the pipeline completes, the credentials are no longer usable, reducing the window of opportunity for an attacker to exploit them.

2. **Federated Identity:** The OIDC provider allows GitLab to act as a trusted identity provider, issuing tokens that are validated by AWS. This federated identity model ensures that only authenticated GitLab users can assume the role and access AWS resources.

3. **Auditing and Logging:** Each request to assume the role is logged, providing a clear audit trail of who accessed the resources and when. This makes it easier to detect and respond to unauthorized access attempts.

4. **Least Privilege Access:** The role assigned to the pipeline can be scoped to provide only the minimum necessary permissions required to perform the tasks. This limits the potential damage if the credentials are compromised.

By leveraging GitLab's OIDC provider, organizations can ensure that their pipelines interact securely with AWS, reducing the risk of unauthorized access and improving overall security posture.

---
<!-- nav -->
[[06-Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning|Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Configure Authentication with GitLab Identity Provider/00-Overview|Overview]]
