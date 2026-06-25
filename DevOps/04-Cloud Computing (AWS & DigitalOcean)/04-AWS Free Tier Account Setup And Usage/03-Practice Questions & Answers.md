---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What steps are required to create an AWS Free Tier account?**

To create an AWS Free Tier account, you need to complete several steps:
1. Visit the AWS website and click on the "Create a Free Account" button.
2. Fill out the registration form with your personal details, including your address and contact information.
3. Provide a valid credit card for verification purposes. Note that AWS may charge your card for any usage beyond the free tier limits.
4. Review and accept the AWS terms and conditions.
5. Once your account is created, you can start using the free tier services listed in the AWS documentation.

**Q2. What are the key services included in the AWS Free Tier?**

The AWS Free Tier includes a variety of services, but some of the most important ones are:
- **EC2 (Elastic Compute Cloud)**: You can run one micro instance for one year at no cost. This is useful for testing and development purposes.
- **S3 (Simple Storage Service)**: You can store and retrieve up to 5 GB of data for free, along with 20,000 GET requests and 2,000 PUT, COPY, POST, or LIST requests per month.
- **RDS (Relational Database Service)**: While not used in this course, you can create a single instance of a MySQL or PostgreSQL database for free.
- **Always Free Resources**: These include basic services like IAM (Identity and Access Management), VPC (Virtual Private Cloud), Route 53, and others that do not incur charges.

**Q3. How can you ensure you are only using free tier eligible resources in AWS?**

To ensure you are only using free tier eligible resources in AWS, follow these steps:
1. When creating an EC2 instance, look for the "Free Tier Eligible" tag in the instance type selection. Choose an instance type that is labeled as such.
2. Use the free tier eligible storage options, such as the S3 bucket, within the specified limits.
3. Regularly review your AWS console to monitor usage and ensure you are not exceeding the free tier limits.
4. Utilize AWS Cost Explorer to track your spending and identify any charges outside the free tier.

**Q4. What should you do to avoid unexpected charges while using AWS Free Tier?**

To avoid unexpected charges while using AWS Free Tier, you should:
1. **Monitor Your Usage**: Regularly check your AWS console to ensure you are not exceeding the free tier limits.
2. **Clean Up Unused Resources**: Delete any resources you no longer need, such as EC2 instances, S3 buckets, and other services.
3. **Understand Pricing**: Familiarize yourself with the pricing structure for different AWS services. Use the AWS Simple Monthly Calculator to estimate potential costs.
4. **Set Budget Alerts**: Configure budget alerts in AWS to notify you when you approach or exceed certain spending thresholds.

**Q5. How can you determine which AWS resources are costing you money?**

To determine which AWS resources are costing you money, you can:
1. **Use AWS Cost Explorer**: This tool provides detailed reports on your monthly spending, broken down by service, usage type, and more.
2. **Review Billing Details**: Check your AWS billing dashboard for detailed breakdowns of your monthly charges.
3. **Enable Detailed Billing Reports**: Set up detailed billing reports to receive CSV files that contain line-item details of your usage and costs.
4. **Set Up Budgets and Alerts**: Create budgets in AWS to automatically alert you when your spending exceeds a certain threshold.

**Q6. Explain why it is important to clean up unused resources in AWS.**

Cleaning up unused resources in AWS is important for several reasons:
1. **Cost Control**: Unused resources can accumulate charges over time, even if they are not actively being used. By cleaning up these resources, you can avoid unnecessary expenses.
2. **Security**: Unused resources can pose security risks if they are not properly managed. Removing them reduces the attack surface and minimizes the risk of unauthorized access.
3. **Resource Management**: Keeping your AWS environment tidy helps you manage your resources more effectively. It makes it easier to track what you are using and to allocate resources efficiently.
4. **Compliance**: In many cases, compliance requirements mandate that unused resources be removed to maintain a secure and efficient environment.

---
<!-- nav -->
[[02-AWS Free Tier Account Setup and Usage|AWS Free Tier Account Setup and Usage]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/04-AWS Free Tier Account Setup And Usage/00-Overview|Overview]]
