---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Pitfalls and Common Mistakes

### Pitfall: Ignoring Security Checks

One common mistake is ignoring security checks altogether. This can lead to vulnerabilities being deployed to production, potentially compromising the security of the application.

### How to Prevent / Defend

#### Detection

- **Automated Security Scans**: Use tools like RetireJS, OWASP ZAP, and others to scan for vulnerabilities.
- **Logging and Monitoring**: Implement logging and monitoring to detect and respond to security incidents.

#### Prevention

- **Secure Coding Practices**: Follow secure coding guidelines to minimize vulnerabilities.
- **Regular Updates**: Keep dependencies and libraries up to date to patch known vulnerabilities.

#### Secure Code Fix

**Vulnerable Code**

```javascript
// Vulnerable code
const express = require('express');
const app = express();

app.get('/', function(req, res) {
    res.send('Hello World!');
});

app.listen(3000);
```

**Fixed Code**

```javascript
// Fixed code
const express = require('express');
const app = express();
const helmet = require('helmet');

app.use(helmet());

app.get('/', function(req, res) {
    res.send('Hello World!');
});

app.listen(3000);
```

### Configuration Hardening

#### Example: AWS ECR Configuration

Ensure that ECR is configured securely by enabling encryption and setting appropriate permissions.

```yaml
# Example ECR Configuration
---
Resources:
  MyECRRepository:
    Type: 'AWS::ECR::Repository'
    Properties:
      RepositoryName: 'juice-shop'
      ImageTagMutability: 'MUTABLE'
      ImageScanningConfiguration:
        ScanOnPush: true
```

### Detection and Response

#### Example: AWS CloudTrail

Use AWS CloudTrail to monitor API calls made to ECR and other AWS services. This helps in detecting unauthorized access and suspicious activities.

```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDOQEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/example-user",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
  },
  "eventTime": "2023-01-01T12:00:00Z",
  "eventSource": "ecr.amazonaws.com",
  "eventName": "PutImage",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "192.0.2.0",
  "userAgent": "aws-sdk-java/2.17.1 Linux/5.4.0-103-generic OpenJDK_64-Bit_Server_VM/11.0.11+9/11.0.11+9 java/11.0.11 vendor/Oracle_Corporation",
  "requestParameters": {
    "registryId": "123456789012",
    "repositoryName": "juice-shop",
    "imageManifest": "<base64-encoded-manifest>",
    "imageTag": "latest"
  },
  "responseElements": null,
  "requestID": "12345678-1234-1234-1234-123456789012",
  "eventID": "12345678-1234-1234-1234-123456789012",
  "readOnly": false,
  "resources": [
    {
      "ARN": "arn:aws:ecr:us-east-1:123456789012:repository/juice-shop",
      "accountId": "123456789012",
      "type": "AWS::ECR::Repository"
    }
  ],
  "sharedEventID": "12345678-1234-1234-1234-123456789012",
  "vpcEndpointId": "vpce-1234567890abcdef"
}
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide practical experience in setting up CD pipelines and integrating security checks.

---
<!-- nav -->
[[13-Mermaid Diagrams|Mermaid Diagrams]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[15-Real-World Examples and Recent CVEs|Real-World Examples and Recent CVEs]]
