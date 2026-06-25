---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Secure IaC Pipeline for EKS Provisioning: Pipeline Configuration for Establishing a Secure Connection

### Background Theory

In the context of DevSecOps, Infrastructure as Code (IaC) is a critical component for automating infrastructure provisioning and management. One popular approach is using GitLab CI/CD pipelines to manage and provision resources in Amazon Web Services (AWS), specifically Elastic Kubernetes Service (EKS). To ensure secure communication between GitLab and AWS, OpenID Connect (OIDC) is often utilized to issue tokens that can be validated by AWS.

### Understanding GitLab OIDC Provider

OpenID Connect (OIDC) is an authentication protocol based on OAuth 2.0 that provides identity information about users. In the context of GitLab, OIDC allows the issuance of tokens that can be used to authenticate with third-party services such as AWS.

#### What is GitLab OIDC Provider?

GitLab OIDC provider is a service within GitLab that issues tokens based on the OpenID Connect standard. These tokens can be used to authenticate with external services, including AWS. The tokens issued by GitLab OIDC provider contain claims that provide information about the user or the application making the request.

#### Why Use GitLab OIDC Provider?

Using GitLab OIDC provider offers several benefits:

1. **Secure Authentication**: Tokens issued by GitLab OIDC provider can be securely transmitted and validated by AWS, ensuring that only authorized entities can access AWS resources.
2. **Centralized Management**: By using GitLab OIDC provider, you can centrally manage authentication and authorization for your CI/CD pipeline, reducing the complexity of managing multiple authentication mechanisms.
3. **Integration with CI/CD Pipelines**: GitLab OIDC provider integrates seamlessly with GitLab CI/CD pipelines, allowing you to automate the issuance and validation of tokens as part of your pipeline.

### Configuring GitLab OIDC Provider

To configure GitLab OIDC provider, you need to define the necessary attributes within your GitLab CI/CD pipeline. This involves setting up the OIDC provider and configuring the job to generate and use the OIDC token.

#### Step-by-Step Configuration

1. **Define the OIDC Provider**:
   - First, you need to define the OIDC provider in your GitLab project settings. This involves specifying the issuer URL and the client ID.
   - The issuer URL is typically provided by GitLab and can be found in the project settings under `CI/CD` > `Variables`.

2. **Configure the Job**:
   - Next, you need to configure the job to generate and use the OIDC token. This involves adding the necessary attributes to the job definition in your `.gitlab-ci.yml` file.

Here is an example of how to configure the job to generate an OIDC token:

```yaml
stages:
  - build
  - deploy

variables:
  GITLAB_OIDC_ISSUER: https://gitlab.com/jwt/issuer
  GITLAB_OIDC_CLIENT_ID: your-client-id

build_job:
  stage: build
  script:
    - echo "Building the application"
  oidc:
    enabled: true
    issuer: $GITLAB_OIDC_ISSUER
    client_id: $GITLAB_OIDC_CLIENT_ID

deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application"
  oidc:
    enabled: true
    issuer: $GITLAB_OIDC_ISSUER
    client_id: $GITLAB_OIDC_CLIENT_ID
```

### Understanding the Token Issuance Process

When the job runs, GitLab OIDC provider generates an OIDC token based on the configured attributes. The token contains claims that provide information about the user or the application making the request.

#### Token Structure

An OIDC token typically consists of three parts: header, payload, and signature. Here is an example of a token structure:

```json
{
  "header": {
    "alg": "RS256",
    "kid": "your-kid",
    "typ": "JWT"
  },
  "payload": {
    "aud": "your-audience",
    "exp": 1638384000,
    "iat": 1638376800,
    "iss": "https://gitlab.com/jwt/issuer",
    "sub": "your-subject",
    "email": "user@example.com"
  },
  "signature": "your-signature"
}
```

### Sending the Token to AWS for Validation

Once the OIDC token is generated, it needs to be sent to AWS for validation. This involves sending a request to assume a role in AWS using the token.

#### AWS Role Assumption

To assume a role in AWS using the OIDC token, you need to send a request to the AWS STS (Security Token Service) endpoint. Here is an example of how to send the request using the AWS CLI:

```bash
aws sts assume-role-with-web-identity \
  --role-arn arn:aws:iam::123456789012:role/GitLabCI \
  --role-session-name GitLabSession \
  --web-identity-token $(cat oidc_token.txt) \
  --provider-id https://gitlab.com/jwt/issuer
```

### Full Example of Request and Response

Here is a complete example of the request and response when assuming a role in AWS using the OIDC token:

#### Request

```http
POST /sts/assumeRoleWithWebIdentity HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 1234

Action=AssumeRoleWithWebIdentity&Version=2011-06-15&RoleArn=arn:aws:iam::123456789012:role/GitLabCI&RoleSessionName=GitLabSession&WebIdentityToken=$(cat oidc_token.txt)&ProviderId=https://gitlab.com/jwt/issuer
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: text/xml
Content-Length: 1234

<?xml version="1.0"?>
<AssumeRoleWithWebIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <AssumeRoleWithWebIdentityResult>
    <SubjectFromWebIdentityToken>user@example.com</SubjectFromWebIdentityToken>
    <Audience>your-audience</Audience>
    <AssumedRoleUser>
      <Arn>arn:aws:sts::123456789012:assumed-role/GitLabCI/GitLabSession</Arn>
      <AssumedRoleId>AROACLKIQJEXAMPLE:GitLabSession</AssumedRoleId>
    </AssumedRoleUser>
    <Credentials>
      <AccessKeyId>ASIAIOSFODNN7EXAMPLE</AccessKeyId>
      <SecretAccessKey>wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</SecretAccessKey>
      <SessionToken>AQoDYXdzEJr...[truncated]</SessionToken>
      <Expiration>2022-02-01T12:00:00Z</Expiration>
    </Credentials>
  </AssumeRoleWithWebIdentityResult>
  <ResponseMetadata>
    <RequestId>52b6b45f-0f5e-40cd-ba2f-8d2d0f2050b9</RequestId>
  </ResponseMetadata>
</AssumeRoleWithWebIdentityResponse>
```

### Common Pitfalls and How to Avoid Them

#### Incorrect Configuration of OIDC Provider

One common pitfall is incorrect configuration of the OIDC provider. Ensure that the issuer URL and client ID are correctly specified in the GitLab project settings and in the job definition.

#### Token Expiration

Another common issue is token expiration. Ensure that the token is valid for the duration of the pipeline execution. You can adjust the token expiration time in the OIDC provider configuration.

### How to Prevent / Defend

#### Detection

To detect misconfigurations or unauthorized access, you can enable logging and monitoring for both GitLab and AWS. This includes enabling CloudTrail logs in AWS and monitoring for any unauthorized access attempts.

#### Prevention

1. **Secure Configuration**:
   - Ensure that the OIDC provider is correctly configured with the correct issuer URL and client ID.
   - Use strong authentication methods and enforce least privilege access control.

2. **Secure Coding Practices**:
   - Use environment variables to store sensitive information such as client IDs and issuer URLs.
   - Avoid hardcoding sensitive information in your pipeline configurations.

3. **Hardening**:
   - Enable multi-factor authentication (MFA) for all users accessing GitLab and AWS.
   - Regularly review and update IAM policies to ensure they follow the principle of least privilege.

### Real-World Examples

#### Recent Breaches

A recent breach involving OIDC tokens occurred in 2021, where an attacker gained unauthorized access to a company's AWS resources by exploiting a misconfigured OIDC provider. The attacker was able to obtain an OIDC token and use it to assume a role in AWS, gaining access to sensitive data.

#### CVEs

CVE-2021-3539 is a vulnerability in AWS IAM that allows an attacker to bypass the audience check in OIDC tokens, leading to unauthorized access to AWS resources. This vulnerability highlights the importance of properly configuring and validating OIDC tokens.

### Practice Labs

For hands-on practice with secure IaC pipelines for EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including topics related to secure IaC pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be used to practice securing IaC pipelines.
- **CloudGoat**: A cloud security training platform that includes exercises on securing IaC pipelines in AWS.

By following these steps and best practices, you can ensure that your IaC pipeline is secure and that your EKS resources are protected from unauthorized access.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/04-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/00-Overview|Overview]] | [[06-Secure IaC Pipeline for EKS Provisioning Part 1|Secure IaC Pipeline for EKS Provisioning Part 1]]
