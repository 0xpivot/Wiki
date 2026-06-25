---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Remediation Actions for Non-Compliant Resources

If a resource is found to be non-compliant, remediation actions can be taken to bring it into compliance. This can be done manually or through automated processes.

### Manual Remediation

Manual remediation involves identifying the non-compliant resource and taking corrective actions to bring it into compliance. This can be done using the AWS Management Console or CLI.

#### Example Manual Remediation

1. **Identify Non-Compliant Resource**:
    - Navigate to the AWS Config console.
    - Identify the non-compliant resource.

2. **Take Corrective Actions**:
    - Take corrective actions to bring the resource into compliance.

### Automated Remediation

Automated remediation involves using AWS Config and other services to automatically correct non-compliant resources. This can be done using AWS Lambda functions and other services.

#### Example Automated Remediation

1. **Create a Lambda Function**:
    - Navigate to the AWS Lambda console.
    - Create a new Lambda function to correct non-compliant resources.

2. **Trigger the Lambda Function**:
    - Trigger the Lambda function when a non-compliant resource is identified.

### Example Lambda Function for Automated Remediation

```python
import boto3

def lambda_handler(event, context):
    config = boto3.client('config')
    
    # Get the non-compliant resource
    non_compliant_resource = event['detail']['resource-id']
    
    # Take corrective actions
    config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': 'AWS::EKS::Cluster',
                'ComplianceResourceId': non_compliant_resource,
                'ComplianceType': 'COMPLIANT',
                'Annotation': 'Resource is now compliant'
            }
        ],
        ResultToken=event['resultToken']
    )
```

### Pitfalls and Common Mistakes

1. **Incorrect Remediation Actions**: Ensure that remediation actions are correctly defined to accurately reflect the desired compliance status.
2. **Insufficient Monitoring**: Regularly monitor the compliance status of resources to ensure that they remain compliant.
3. **Incorrect Rule Definitions**: Ensure that compliance rules are correctly defined to accurately reflect the desired compliance status.

### How to Prevent / Defend

1. **Regular Audits**: Conduct regular audits to ensure that resources are compliant.
2. **Automated Monitoring**: Use AWS Config and CloudWatch Events to automatically monitor the compliance status of resources.
3. **Remediation Actions**: Implement automated remediation actions to correct any issues detected during monitoring.

### Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of proper remediation actions. For example, the Equifax breach in 2017 demonstrated the critical role of remediation actions in detecting and responding to security incidents.

### Conclusion

By implementing Compliance as Code for EKS clusters, organizations can ensure that their clusters adhere to compliance rules and are properly monitored. This approach reduces the risk of non-compliance and enhances overall security.

---
<!-- nav -->
[[10-Hands-On Practice Labs|Hands-On Practice Labs]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/12-Practice Questions & Answers|Practice Questions & Answers]]
