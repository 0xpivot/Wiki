---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the role of AWS Config in enabling compliance and governance practices.**

AWS Config provides a detailed view of the resources associated with an AWS account, including how they are configured, how they are related to one another, and how these configurations and relationships have changed over time. This allows organizations to maintain a comprehensive audit trail and ensure that their infrastructure adheres to specific compliance policies. By monitoring changes and maintaining a historical record, AWS Config helps in identifying deviations from established norms, thereby supporting governance and compliance efforts.

**Q2. How would you use CloudWatch to monitor and enforce compliance policies related to S3 buckets?**

To monitor and enforce compliance policies related to S3 buckets using CloudWatch, you can create a CloudWatch alarm that triggers when a specific event occurs, such as an S3 bucket being made publicly accessible. You can set up a CloudWatch Events rule to watch for changes to S3 bucket permissions. When the rule detects a change that violates the compliance policy (e.g., making an S3 bucket public), it can trigger an action, such as sending an alert via email or invoking a Lambda function to automatically correct the misconfiguration. Here’s an example of how to set up a Lambda function to handle this:

```python
import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = event['detail']['requestParameters']['bucketName']
    
    # Check if the bucket is public
    acl = s3.get_bucket_acl(Bucket=bucket_name)
    for grant in acl['Grants']:
        if grant['Grantee'].get('Type') == 'Group' and grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
            # Revoke public access
            s3.put_bucket_acl(
                Bucket=bucket_name,
                ACL='private'
            )
            print(f"Public access revoked for {bucket_name}")
```

This Lambda function checks if the bucket is public and, if so, revokes public access by setting the ACL to private.

**Q3. What are some open-source tools that can be used alongside native cloud service provider tools for compliance and governance?**

One popular open-source tool is Cloud Custodian. Cloud Custodian is a powerful policy engine that allows you to define and enforce policies across multiple cloud providers, including AWS. It supports a wide range of actions, such as tagging resources, managing IAM roles, and ensuring compliance with security best practices. Cloud Custodian can be integrated with CI/CD pipelines to automate policy enforcement and compliance checks.

Another open-source tool is Terraform, which can be used to manage infrastructure as code. By defining infrastructure in code, you can enforce compliance policies through version control and automated testing.

**Q4. How does the integration of incident response into DevSecOps practices support compliance and governance?**

Integrating incident response into DevSecOps practices supports compliance and governance by automating the detection and response to security incidents. This ensures that compliance policies are enforced in real-time and that any deviations are quickly identified and addressed. By leveraging tools like AWS Config and CloudWatch, you can create a continuous feedback loop that monitors compliance status and triggers corrective actions when necessary. This approach helps maintain a secure and compliant environment by combining security practices with development and operations processes.

**Q5. Provide an example of how recent real-world breaches could have been mitigated using native cloud service provider tools like AWS Config and CloudWatch.**

Consider the Capital One breach in 2019, where an attacker gained unauthorized access to sensitive customer data stored in S3 buckets. If Capital One had implemented proper monitoring and enforcement using AWS Config and CloudWatch, the breach could have been mitigated. Specifically, they could have set up CloudWatch alarms to detect and respond to unauthorized access attempts or misconfigurations of S3 buckets. Additionally, AWS Config could have been used to maintain a historical record of resource configurations, allowing for quick identification and remediation of any deviations from compliance policies. By automating these processes, organizations can reduce the risk of data breaches and ensure ongoing compliance with regulatory requirements.

---
<!-- nav -->
[[03-Native Cloud Service Provider Tools for Compliance as Code|Native Cloud Service Provider Tools for Compliance as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/02-Native CSP Tools/00-Overview|Overview]]
