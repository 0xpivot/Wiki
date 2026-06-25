---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up the Environment

Before diving into the automation process, let's set up the environment by creating two EC2 instances and tagging them appropriately.

### Creating EC2 Instances

To begin, navigate to the AWS Management Console and launch two EC2 instances. For simplicity, we will tag one instance with `name=dev` and the other with `name=prod`. Here’s a step-by-step guide:

1. **Log in to the AWS Management Console**.
2. **Navigate to the EC2 Dashboard**.
3. **Launch an Instance**:
    - Choose an Amazon Machine Image (AMI).
    - Select an instance type.
    - Configure instance details.
    - Add storage (EBS volumes).
    - Tag the instances:
        - For the first instance, add a tag with `Key=name` and `Value=dev`.
        - For the second instance, add a tag with `Key=name` and `Value=prod`.
    - Configure security group settings.
    - Review and launch the instances.

Once the instances are launched, they will start initializing. You can monitor their status in the EC2 dashboard.

### Understanding EC2 Volumes

When an EC2 instance is launched, an EBS volume is automatically created and attached to the instance. These volumes store the data for the instance. To ensure data persistence, it is essential to create snapshots of these volumes regularly.

---
<!-- nav -->
[[07-Monitoring and Logging|Monitoring and Logging]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/00-Overview|Overview]] | [[09-Understanding EC2 Instances and Volumes|Understanding EC2 Instances and Volumes]]
