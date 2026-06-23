---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning

### Introduction to Secure IaC Pipelines

Infrastructure as Code (IaC) is a practice where infrastructure is defined using code rather than physical hardware configurations. This approach allows for automation, consistency, and version control of infrastructure changes. In the context of DevSecOps, ensuring that the IaC pipeline is secure is crucial to prevent unauthorized access, misconfigurations, and other vulnerabilities.

In this section, we will focus on configuring a secure IaC pipeline for provisioning Amazon Elastic Kubernetes Service (EKS). Specifically, we will delve into the configuration required to establish a secure connection to AWS services using AWS Security Token Service (STS).

### Understanding AWS Security Token Service (STS)

AWS Security Token Service (STS) provides temporary security credentials for AWS services. These credentials can be used to authenticate and authorize access to AWS resources. STS supports several operations, including `AssumeRole`, `GetSessionToken`, and `WebIdentityToken`.

#### `AssumeRole` vs `WebIdentityToken`

- **`AssumeRole`**: This operation allows you to assume an IAM role and obtain temporary security credentials. Typically, this requires an existing set of AWS credentials (access key and secret key) to initiate the assumption process.
  
- **`WebIdentityToken`**: This operation allows you to assume an IAM role using a web identity provider, such as an OpenID Connect (OIDC) provider. This method does not require pre-existing AWS credentials, making it more suitable for scenarios where credentials are not available or should not be stored.

### Configuring the IaC Pipeline

To configure a secure IaC pipeline for EKS provisioning, we need to ensure that the pipeline can securely interact with AWS services using STS. We will use the `assume-role-with-web-identity` operation to achieve this.

#### Step-by-Step Configuration

1. **Define the Multi-Line Command Syntax**:
   In YAML, multi-line commands can be defined using the `|` character. This allows us to write complex commands across multiple lines while ensuring they are interpreted as a single command.

```yaml
script:
  - |
    aws sts assume-role-with-web-identity \
      --role-arn arn:aws:iam::123456789012:role/my-role \
      --role-session-name my-session \
      --web-identity-token-file /path/to/token \
      --provider-id https://oidc-provider.example.com
```

- **Explanation**:
  - `--role-arn`: Specifies the ARN of the IAM role to assume.
  - `--role-session-name`: A unique identifier for the session.
  - `--web-identity-token-file`: Path to the file containing the web identity token.
  - `--provider-id`: URL of the OIDC provider.

2. **Understanding the Command**:
   The `assume-role-with-web-identity` command uses a web identity token to assume an IAM role. This token is typically obtained from an OIDC provider, which authenticates the user and issues a token.

### Real-World Example: Recent Breaches and CVEs

Recent breaches involving misconfigured IAM roles and insufficient authentication mechanisms highlight the importance of securing IaC pipelines. For instance, the Capital One breach in 2019 was partly due to misconfigured IAM roles, allowing unauthorized access to sensitive data.

#### CVE Example: CVE-2020-14779

CVE-2020-14779 involved a vulnerability in AWS IAM where certain permissions could be exploited to gain unauthorized access to resources. This underscores the need for strict access controls and secure IaC practices.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Enable detailed logging for IAM activities and monitor for unusual patterns.
- **CloudTrail**: Use AWS CloudTrail to log API calls and monitor for unauthorized actions.

#### Prevention

- **Least Privilege Principle**: Ensure IAM roles have the minimum necessary permissions.
- **IAM Policies**: Define strict policies that limit access to only required resources.

#### Secure Coding Fixes

**Vulnerable Code**:

```yaml
script:
  - |
    aws sts assume-role \
      --role-arn arn:aws:iam::123456789012:role/my-role \
      --role-session-name my-session \
      --profile my-profile
```

**Secure Code**:

```yaml
script:
  - |
    aws sts assume-role-with-web-identity \
      --role-arn arn:aws:iam::123456789012:role/my-role \
      --role-session-name my-session \
      --web-identity-token-file /path/to/token \
      --provider-id https://oidc-provider.example.com
```

### Complete Example: Full HTTP Request and Response

#### HTTP Request

```http
POST / HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/sts/aws4_request, SignedHeaders=host;x-amz-date, Signature=0b5d673d9bedf6fa0f2e2814108f459e40bbc831b42bd40b7f1b8f5a3c0f3f6b
X-Amz-Date: 20230401T000000Z

Action=AssumeRoleWithWebIdentity&Version=2011-06-15&RoleArn=arn:aws:iam::123456789012:role/my-role&RoleSessionName=my-session&WebIdentityTokenFile=/path/to/token&ProviderId=https://oidc-provider.example.com
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/xml
Content-Length: 1234
Date: Sun, 01 Apr 2023 00:00:00 GMT

<?xml version="1.0"?>
<AssumeRoleWithWebIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <AssumeRoleWithWebIdentityResult>
    <SubjectFromWebIdentityToken>example@example.com</SubjectFromWebIdentityToken>
    <Audience>https://oidc-provider.example.com</Audience>
    <AssumedRoleUser>
      <Arn>arn:aws:sts::123456789012:assumed-role/my-role/example@example.com</Arn>
      <AssumedRoleId>AROACLKIQJMPEXAMPLE:example@example.com</AssumedRoleId>
    </AssumedRoleUser>
    <Credentials>
      <AccessKeyId>ASIAIOSFODNN7EXAMPLE</AccessKeyId>
      <SecretAccessKey>wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</SecretAccessKey>
      <SessionToken>AQoDYXdzEJr...[truncated]</SessionToken>
      <Expiration>2023-04-01T01:00:00Z</Expiration>
    </Credentials>
  </AssumeRoleWithWebIdentityResult>
  <ResponseMetadata>
    <RequestId>5255c1ae-48ff-11e2-a24a-d9ae921c90e5</RequestId>
  </
```

### Mermaid Diagrams

#### Sequence Diagram: Assume Role with Web Identity

```mermaid
sequenceDiagram
  participant Pipeline as Pipeline
  participant STS as AWS STS
  participant OIDC as OIDC Provider
  participant EKS as EKS

  Pipeline->>STS: AssumeRoleWithWebIdentity
  STS->>OIDC: ValidateToken
  OIDC-->>STS: TokenValidated
  STS-->>Pipeline: Credentials
  Pipeline->>EKS: ProvisionResources
```

### Hands-On Labs

For practical experience with secure IaC pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers some aspects of secure IaC.
- **OWASP Juice Shop**: While primarily a web application security lab, it can be adapted to demonstrate secure IaC practices.
- **Kubernetes Goat**: Provides hands-on experience with Kubernetes security, including IaC practices.

These labs provide a comprehensive environment to practice and reinforce the concepts discussed in this chapter.

### Conclusion

Establishing a secure IaC pipeline for EKS provisioning involves careful configuration and adherence to best practices. By understanding the nuances of AWS STS and implementing secure coding practices, you can significantly reduce the risk of unauthorized access and ensure the integrity of your infrastructure.

---
<!-- nav -->
[[09-Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning Part 2|Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning Part 2]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/11-Practice Questions & Answers|Practice Questions & Answers]]
