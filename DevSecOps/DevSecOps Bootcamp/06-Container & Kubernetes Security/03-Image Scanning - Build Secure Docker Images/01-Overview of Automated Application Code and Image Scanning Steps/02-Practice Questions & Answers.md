---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What are the primary steps involved in securing the deployment environment using AWS EC2?**

The primary steps involved in securing the deployment environment using AWS EC2 include:

1. **IAM Role Configuration**: Ensure that EC2 instances are launched with the appropriate IAM roles that provide least privilege access to other AWS services.
2. **Security Groups**: Configure security groups to control inbound and outbound traffic to the EC2 instances. This involves setting up rules that allow only necessary ports and protocols.
3. **Network Access Control Lists (ACLs)**: Use Network ACLs to further restrict traffic at the subnet level.
4. **Encryption**: Enable encryption for data at rest using EBS volumes and for data in transit using SSL/TLS.
5. **Logging and Monitoring**: Set up CloudWatch logging and monitoring to track the health and performance of EC2 instances.
6. **Patch Management**: Regularly apply security patches and updates to the operating system and applications running on EC2 instances.
7. **Instance Metadata Service Version 2 (IMDSv2)**: Use IMDSv2 to securely retrieve instance metadata, reducing the risk of unauthorized access.

**Q2. How can you ensure that Docker images used in your deployment pipeline are secure?**

To ensure that Docker images used in your deployment pipeline are secure, follow these steps:

1. **Use Trusted Sources**: Only pull images from trusted sources such as official repositories or private registries.
2. **Image Scanning**: Integrate automated tools like Clair, Trivy, or Snyk into your CI/CD pipeline to scan Docker images for known vulnerabilities.
3. **Least Privilege Principle**: Run containers with the minimum set of permissions required to perform their tasks.
4. **Regular Updates**: Keep the base images and dependencies up-to-date by regularly rebuilding and re-scanning the images.
5. **Immutable Infrastructure**: Adopt immutable infrastructure principles where containers are replaced rather than updated in place, ensuring consistency and security.
6. **Content Trust**: Utilize Docker Content Trust to verify the integrity and authenticity of images.

**Q3. Explain how you would configure security groups in AWS EC2 to protect your deployment environment.**

To configure security groups in AWS EC2 to protect your deployment environment, follow these steps:

1. **Create Security Group**: Create a new security group for your EC2 instances within the VPC.
2. **Inbound Rules**: Define inbound rules to allow traffic only from trusted IP addresses or other security groups. For example, allow SSH (port 22) from your office IP address and HTTP/HTTPS (ports 80/443) from anywhere.
3. **Outbound Rules**: By default, all outbound traffic is allowed. You can modify this to restrict traffic to specific destinations if needed.
4. **Attach Security Group**: Attach the created security group to the EC2 instances.
5. **Review and Update**: Periodically review and update the security group rules to reflect any changes in your network architecture or security policies.

Here’s an example of creating a security group using the AWS CLI:

```bash
aws ec2 create-security-group --group-name my-sg --description "My security group"
aws ec2 authorize-security-group-ingress --group-id sg-1234567890abcdef0 --protocol tcp --port 22 --cidr 192.168.1.0/24
aws ec2 authorize-security-group-ingress --group-id sg-1234567890abcdef0 --protocol tcp --port 80 --cidr 0.0.0.0/0
```

**Q4. Why is it important to use immutable infrastructure when deploying applications on AWS EC2?**

Using immutable infrastructure when deploying applications on AWS EC2 is important because it enhances security and reliability. Here's why:

1. **Consistency**: Immutable infrastructure ensures that every deployment is consistent, as each new version of the application is deployed as a new instance rather than updating existing ones. This reduces the risk of configuration drift.
2. **Rollback**: In case of issues, rolling back to a previous version is straightforward since you simply replace the new instances with the old ones.
3. **Security**: Since instances are not modified after deployment, they are less likely to be compromised. Any changes require redeploying the entire instance, which can be audited and controlled.
4. **Scalability**: Scaling becomes simpler as you can add or remove identical instances without worrying about inconsistencies between them.
5. **Auditability**: With immutable infrastructure, every change leaves a clear audit trail, making it easier to track and manage changes over time.

**Q5. What recent real-world examples highlight the importance of securing Docker images in the deployment pipeline?**

Recent real-world examples that highlight the importance of securing Docker images in the deployment pipeline include:

1. **CVE-2019-14287**: This vulnerability affected Kubernetes and allowed attackers to execute arbitrary commands on the host machine through a misconfigured Docker socket. Ensuring Docker images are scanned for vulnerabilities and properly configured can help mitigate such risks.
2. **Container Security Incidents**: Several high-profile breaches have been attributed to unsecured Docker images containing known vulnerabilities or malicious code. For example, the Equifax breach in 2017 was partly due to an unpatched Apache Struts library in their web application, which could have been mitigated by regular image scanning and patch management.

These incidents underscore the need for continuous monitoring and securing of Docker images throughout the deployment pipeline.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/01-Overview of Automated Application Code and Image Scanning Steps/01-Overview of Automated Application Code and Image Scanning Steps|Overview of Automated Application Code and Image Scanning Steps]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/01-Overview of Automated Application Code and Image Scanning Steps/00-Overview|Overview]]
