---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Adding Tags to Resources

Tags are metadata labels that you can assign to AWS resources. They consist of a key-value pair and can be used to categorize and manage resources more effectively.

### What Are Tags?

Tags are user-defined metadata that can be applied to AWS resources. Each tag consists of a key and a value. For example, you might use a tag like `Environment: Production` to identify resources that belong to your production environment.

### Why Use Tags?

Tags help you organize and manage your AWS resources efficiently. They can be used for various purposes, such as:

- **Cost Allocation:** Tagging resources allows you to track costs associated with specific projects or departments.
- **Access Control:** You can use tags to enforce access control policies based on resource attributes.
- **Automation:** Tags can be used to trigger automated actions, such as backups or scaling operations.

### Syntax of Tags

When adding tags to a resource, the syntax typically looks like this:

```json
{
  "Key": "Environment",
  "Value": "Production"
}
```

However, when using tags as filters, the syntax changes slightly. For example:

```json
{
  "Name": "tag-key",
  "Values": ["Environment"]
}
```

### Differences Between Adding Tags and Using Them as Filters

When adding tags to a resource, you specify the key and value directly. However, when using tags as filters, you need to specify the `Name` and `Values`. This difference is important to understand to avoid confusion.

### Example Code: Adding Tags to a Resource

Here’s an example of how to add a tag to an EBS volume using the AWS CLI:

```bash
aws ec2 create-tags --resources vol-0123456789abcdef0 --tags Key=Environment,Value=Production
```

### Example Code: Filtering Resources by Tags

To filter resources by tags, you would use a different syntax:

```bash
aws ec2 describe-volumes --filters Name=tag-key,Values=Environment Name=tag-value,Values=Production
```

### Common Pitfalls

One common pitfall is confusing the syntax for adding tags versus using them as filters. Always double-check the syntax to ensure you are using the correct format.

### How to Prevent / Defend

To prevent issues related to incorrect tag usage, always validate the syntax before executing commands. Additionally, use tools like the AWS Management Console to visually verify the tags applied to resources.

---
<!-- nav -->
[[02-Introduction to EC2 Instances and Volume Snapshots|Introduction to EC2 Instances and Volume Snapshots]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/18-Recovering EC2 Instances Using Volume Snapshots/00-Overview|Overview]] | [[04-Attaching the New Volume to an EC2 Instance|Attaching the New Volume to an EC2 Instance]]
