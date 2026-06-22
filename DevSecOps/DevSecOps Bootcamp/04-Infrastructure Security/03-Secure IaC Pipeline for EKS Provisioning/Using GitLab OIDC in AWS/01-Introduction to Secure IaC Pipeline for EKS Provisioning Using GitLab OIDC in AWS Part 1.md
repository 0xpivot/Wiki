---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS

In the realm of DevSecOps, ensuring the security of Infrastructure as Code (IaC) pipelines is paramount. This chapter delves into the process of securely provisioning Amazon Elastic Kubernetes Service (EKS) clusters using GitLab's OpenID Connect (OIDC) integration with AWS. By leveraging GitLab OIDC, we can establish a trust relationship between GitLab and AWS, allowing us to assume roles within AWS without the need for dedicated EC2 servers as GitLab runners.

### What is GitLab OIDC?

OpenID Connect (OIDC) is an authentication protocol built on top of OAuth 2.0. It provides a way for clients to verify the identity of users based on the authentication performed by an authorization server, as well as to obtain basic profile information about the user in an interoperable and REST-like fashion. In the context of GitLab, OIDC allows GitLab to act as an identity provider (IdP) that can issue tokens to authenticate and authorize access to AWS resources.

### Why Use GitLab OIDC with AWS?

Using GitLab OIDC with AWS offers several advantages:

1. **Decoupling**: It decouples the GitLab runners from AWS infrastructure, allowing you to use shared runners or runners hosted on your own infrastructure.
2. **Security**: It enhances security by enabling fine-grained access control through IAM roles and policies.
3. **Flexibility**: It provides flexibility in managing access to AWS resources, especially in multi-tenant environments.

### How Does GitLab OIDC Work with AWS?

To establish a trust relationship between GitLab and AWS, we need to configure AWS to trust the identities issued by GitLab's OIDC provider. This involves creating an IAM role in AWS that trusts the GitLab OIDC provider and configuring GitLab to issue JWT tokens during pipeline execution.

#### Step-by-Step Process

1. **Create an IAM Role in AWS**:
    - Define the trust relationship policy to trust the GitLab OIDC provider.
    - Attach necessary permissions to the role.

2. **Configure GitLab to Issue JWT Tokens**:
    - Set up the OIDC provider in GitLab.
    - Configure the pipeline to use the OIDC provider to issue JWT tokens.

3. **Assume the IAM Role in the Pipeline**:
    - Use the JWT token to assume the IAM role within the pipeline.

### Detailed Configuration Steps

#### Creating an IAM Role in AWS

1. **Define the Trust Relationship Policy**:
    - Navigate to the IAM console in AWS.
    - Create a new IAM role.
    - Choose the type of trusted entity as "Web Identity".
    - Select "GitLab" as the identity provider.
    - Specify the URL of the GitLab OIDC provider (e.g., `https://gitlab.com/jwks`).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/gitlab.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc:aud": "https://token.actions.githubusercontent.com",
          "oidc:sub": "repo:ORG_NAME/REPO_NAME:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

2. **Attach Necessary Permissions**:
    - Attach the required IAM policies to the role.
    - Ensure the role has the necessary permissions to manage EKS clusters.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*",
        "ec2:*",
        "iam:*",
        "cloudformation:*",
        "autoscaling:*",
        "elasticloadbalancing:*",
        "route53:*",
        "acm:*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Configuring GitLab to Issue JWT Tokens

1. **Set Up the OIDC Provider in GitLab**:
    - Navigate to the GitLab settings.
    - Enable the OIDC provider.
    - Configure the provider to issue JWT tokens.

2. **Configure the Pipeline to Use the OIDC Provider**:
    - Modify the `.gitlab-ci.yml` file to include the OIDC provider configuration.

```yaml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - echo "Deploying to AWS using OIDC"
    - aws sts assume-role-with-web-identity --role-arn arn:aws:iam::ACCOUNT_ID:role/GitLabOIDCRole --web-identity-token $(curl -s -H "Authorization: Bearer $CI_JOB_JWT_V2" https://gitlab.com/api/v4/jwt/validate) --role-session-name GitLabSession
  only:
    - main
```

### Assumptions and Pitfalls

1. **Assuming the IAM Role in the Pipeline**:
    - Ensure the pipeline has the necessary environment variables set.
    - Validate the JWT token before assuming the role.

2. **Pitfalls**:
    - Incorrect configuration of the trust relationship policy.
    - Missing permissions attached to the IAM role.
    - Misconfiguration of the OIDC provider in GitLab.

### Real-World Examples and Recent Breaches

Recent breaches involving misconfigured IAM roles and permissions highlight the importance of proper configuration and validation. For example, the breach at Capital One in 2019 was partly due to misconfigured IAM roles and permissions. Ensuring that IAM roles are properly configured and that the trust relationship is correctly established can help prevent such breaches.

### How to Prevent / Defend

#### Detection

1. **Monitor IAM Role Usage**:
    - Use AWS CloudTrail to monitor IAM role usage.
    - Set up alerts for unauthorized access attempts.

2. **Audit IAM Policies**:
    - Regularly audit IAM policies to ensure they are least privilege.
    - Use AWS IAM Access Analyzer to identify potential issues.

#### Prevention

1. **Least Privilege Principle**:
    - Ensure IAM roles have the minimum necessary permissions.
    - Use IAM policies to restrict access to specific resources.

2. **Regular Audits**:
    - Perform regular audits of IAM roles and policies.
    - Use tools like AWS IAM Access Analyzer to identify potential issues.

#### Secure Coding Fixes

1. **Vulnerable Code Example**:
    - A pipeline that assumes an IAM role without proper validation.

```yaml
deploy:
  stage: deploy
  script:
    - aws sts assume-role-with-web-identity --role-arn arn:aws:iam::ACCOUNT_ID:role/GitLabOIDCRole --web-identity-token $(curl -s -H "Authorization: Bearer $CI_JOB_JWT_V2" https://gitlab.com/api/v4/jwt/validate) --role-session-name GitLabSession
```

2. **Secure Code Example**:
    - A pipeline that validates the JWT token before assuming the role.

```yaml
deploy:
  stage: deploy
  script:
    - curl -s -H "Authorization: Bearer $CI_JOB_JWT_V2" https://gitlab.com/api/v4/jwt/validate | jq '.valid'
    - if [ $? -eq 0 ]; then
        aws sts assume-role-with-web-identity --role-arn arn:aws:iam::ACCOUNT_ID:role/GitLabOIDCRole --web-identity-token $(curl -s -H "Authorization: Bearer $CI_JOB_JWT_V2" https://gitlab.com/api/v4/jwt/validate) --role-session-name GitLabSession
      else
        echo "JWT token is invalid"
      fi
```

### Conclusion

By leveraging GitLab OIDC with AWS, we can establish a secure and flexible trust relationship for provisioning EKS clusters. Proper configuration and validation are crucial to preventing unauthorized access and ensuring the security of the IaC pipeline. Regular audits and least privilege principles should be followed to maintain a secure environment.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on securing IaC pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing secure coding techniques.
- **CloudGoat**: A cloud security training platform that includes scenarios for securing IaC pipelines in AWS.

These labs provide practical experience in securing IaC pipelines and can help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Using GitLab OIDC in AWS/00-Overview|Overview]] | [[02-Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 2|Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 2]]
