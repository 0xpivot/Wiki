---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS EC2 Instances

### What is an EC2 Instance?

An Amazon Elastic Compute Cloud (EC2) instance is a virtual server in Amazon Web Services (AWS) cloud. It allows you to run applications and services on virtual machines that are managed by AWS. Each EC2 instance runs an Amazon Machine Image (AMI), which is essentially a pre-configured template containing the operating system and additional software.

### Why Use EC2 Instances?

EC2 instances provide flexibility and scalability. You can easily scale up or down based on demand, and you only pay for the resources you use. This makes EC2 ideal for a wide range of applications, from web servers to data processing and machine learning tasks.

### How Does an EC2 Instance Work?

When you launch an EC2 instance, you specify several parameters, including the AMI, instance type, key pair, security groups, and more. These parameters determine the behavior and capabilities of your instance.

### Required Attributes for Creating an EC2 Instance

To create an EC2 instance, you need to specify several required attributes:

1. **AMI (Amazon Machine Image)**: The operating system and software that the instance will run.
2. **Instance Type**: The hardware specifications of the instance, such as CPU, memory, and storage.
3. **Key Pair**: A set of cryptographic keys used to securely access the instance.
4. **Security Group**: Rules that control inbound and outbound traffic to the instance.

### Example: Creating an EC2 Instance

Let's walk through the process of creating an EC2 instance step-by-step.

#### Step 1: Choose an AMI

The first step is to select an AMI. An AMI is a pre-configured template that includes the operating system and any additional software you need. For this example, we'll use the Amazon Linux AMI, which is optimized for use with AWS services.

```mermaid
graph TD;
    A[Choose AMI] --> B[Select Amazon Linux];
    B --> C[Launch Instance];
```

#### Step 2: Select an Instance Type

Next, you need to choose an instance type. Instance types define the hardware specifications of your instance, such as CPU, memory, and storage. For this example, we'll use the `t2.micro` instance type, which is a general-purpose instance type suitable for small workloads.

```mermaid
graph TD;
    A[Select Instance Type] --> B[t2.micro];
    B --> C[Launch Instance];
```

#### Step 3: Configure Key Pair

A key pair is a set of cryptographic keys used to securely access your instance. You can either create a new key pair or use an existing one. For this example, we'll create a new key pair named `my-key-pair`.

```mermaid
graph TD;
    A[Configure Key Pair] --> B[Create New Key Pair];
    B --> C[Name: my-key-pair];
    C --> D[Launch Instance];
```

#### Step 4: Set Up Security Groups

Security groups are rules that control inbound and outbound traffic to your instance. For this example, we'll create a new security group named `my-security-group` and allow inbound traffic on ports 22 (SSH) and 8080 (HTTP).

```mermaid
graph TD;
    A[Set Up Security Groups] --> B[Create New Security Group];
    B --> C[Name: my-security-group];
    C --> D[Inbound Rule: SSH (Port 22)];
    D --> E[Inbound Rule: HTTP (Port 8080)];
    E --> F[Launch Instance];
```

#### Step 5: Launch the Instance

Once you've configured all the necessary settings, you can launch the instance. After launching, you can monitor the instance status in the EC2 dashboard.

```mermaid
graph TD;
    A[Launch Instance] --> B[Monitor Status];
    B --> C[Instance Running];
```

### Complete Example: Creating an EC2 Instance

Here's a complete example of creating an EC2 instance using the AWS Management Console:

1. **Navigate to the EC2 Dashboard**:
   - Open the AWS Management Console and navigate to the EC2 service.

2. **Launch an Instance**:
   - Click on "Launch Instance".

3. **Choose an AMI**:
   - Select the Amazon Linux AMI.

4. **Select an Instance Type**:
   - Choose the `t2.micro` instance type.

5. **Configure Instance Details**:
   - Leave the default settings for now.

6. **Add Storage**:
   - Accept the default storage settings.

7. **Tag Instance**:
   - Add a tag with key `Name` and value `MyAppServer`.

8. **Configure Security Group**:
   - Create a new security group named `my-security-group`.
   - Add inbound rules for SSH (port 22) and HTTP (port 8080).

9. **Review and Launch**:
   - Review the instance configuration and click "Launch".

10. **Select Key Pair**:
    - Create a new key pair named `my-key-pair`.

11. **Launch the Instance**:
    - Click "Launch Instances".

### Full Raw HTTP Request and Response

Here's an example of the full HTTP request and response for creating an EC2 instance using the AWS SDK:

```http
POST / HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-west-2/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=7b0b5c9b95d9d7c5f7e9c3c7d7f7e9c3c7d7f7e9c3c7d7f7e9c3c7d7f7e9c3c7
X-Amz-Date: 20230401T120000Z
Content-Length: 1234

Action=RunInstances&ImageId=ami-0abcdef1234567890&InstanceType=t2.micro&MinCount=1&MaxCount=1&KeyName=my-key-pair&SecurityGroupIds=sg-0abcdef1234567890&TagSpecifications=ResourceType%3Dinstance%2CTags%3D%5B%7BKey%3DName%2CValue%3DMyAppServer%7D%5D
```

```http
HTTP/1.1 200 OK
Content-Type: text/xml
Content-Length: 1234
Date: Mon, 01 Apr 2023 12:00:00 GMT

<?xml version="1.0" encoding="UTF-8"?>
<RunInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <reservation>
    <reservationId>r-0abcdef1234567890</reservationId>
    <ownerId>123456789012</ownerId>
    <requesterId>123456789012</requesterId>
    <groupSet/>
    <instancesSet>
      <item>
        <instanceId>i-0abcdef1234567890</instanceId>
        <imageId>ami-0abcdef1234567890</imageId>
        <instanceState>
          <code>0</code>
          <name>pending</name>
        </instanceState>
        <privateDnsName>ip-10-0-1-42.ec2.internal</privateDnsName>
        <amiLaunchIndex>0</amiLaunchIndex>
        <productCodes/>
        <instanceType>t2.micro</instanceType>
        <launchTime>2023-04-01T12:00:00Z</launchTime>
        <placement>
          <availabilityZone>us-west-2a</availabilityZone>
          <groupName/>
          <tenancy>default</tenancy>
        </placement>
        <monitoring>
          <state>disabled</state>
        </monitoring>
        <subnetId>subnet-0abcdef1234567890</subnetId>
        <vpcId>vpc-0abcdef1234567890</vpcId>
        <privateIpAddress>10.0.1.42</privateIpAddress>
        <sourceDestCheck>true</sourceDestCheck>
        <groupSet>
          <item>
            <groupId>sg-0abcdef1234567890</groupId>
            <groupName>my-security-group</groupName>
          </item>
        </groupSet>
        <stateReason>
          <code>pending</code>
          <message>Scheduled for launch at 2023-04-01T12:00:00Z</message>
        </stateReason>
        <architecture>x86_64</architecture>
        <rootDeviceType>ebs</rootDeviceType>
        <rootDeviceName>/dev/sda1</rootDeviceName>
        <blockDeviceMapping>
          <item>
            <deviceName>/dev/sda1</deviceName>
            <ebs>
              <volumeId>vol-0abcdef1234567890</volumeId>
              <status>attaching</status>
              <attachTime>2023-04-01T12:00:00Z</attachTime>
              <deleteOnTermination>true</deleteOnTermination>
            </ebs>
          </item>
        </blockDeviceMapping>
        <virtualizationType:hvm</virtualizationType>
        <tagSet>
          <item>
            <key>Name</key>
            <value>MyAppServer</value>
          </item>
        </tagSet>
        <hypervisor:xen</hypervisor>
        <networkInterfaceSet>
          <item>
            <networkInterfaceId>eni-0abcdef1234567890</networkInterfaceId>
            <subnetId>subnet-0abcdef1234567890</subnetId>
            <vpcId>vpc-0abcdef1234567890</vpcId>
            <description/>
            <ownerId>123456789012</ownerId>
            <status>in-use</status>
            <privateIpAddress>10.0.1.42</privateIpAddress>
            <sourceDestCheck>true</sourceDestCheck>
            <groups>
              <item>
                <groupId>sg-0abcdef1234567890</groupId>
                <groupName>my-security-group</groupName>
              </item>
            </groups>
            <attachment>
              <attachmentId>eni-attach-0abcdef1234567890</attachmentId>
              <deviceIndex>0</deviceIndex>
              <status>attaching</status>
              <attachTime>2023-04-01T12:00:00Z</attachTime>
              <deleteOnTermination>true</deleteOnTermination>
            </attachment>
            <privateIpAddresses>
              <item>
                <privateIpAddress>10.0.1.42</privateIpAddress>
                <primary>true</primary>
              </item>
            </privateIpAddresses>
          </item>
        </networkInterfaceSet>
        <ebsOptimized>false</ebsOptimized>
        <enaSupport:true</enaSupport>
        <capacityReservationSpecification>
          <capacityReservationPreference>open</capacityReservationPreference>
        </capacityReservationSpecification>
      </item>
    </instancesSet>
  </reservation>
</RunInstancesResponse>
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect AMI Selection**: Choosing the wrong AMI can lead to compatibility issues and unnecessary overhead.
2. **Insufficient Instance Type**: Using an instance type that does not meet your workload requirements can result in performance issues.
3. **Security Group Misconfiguration**: Incorrectly configuring security groups can expose your instance to unauthorized access.
4. **Key Pair Management**: Losing access to your key pair can lock you out of your instance.

#### Best Practices

1. **Use Optimized AMIs**: Choose AMIs that are optimized for your specific use case.
2. **Select Appropriate Instance Types**: Choose instance types that match your workload requirements.
3. **Secure Your Instances**: Use security groups to restrict access to your instances.
4. **Manage Key Pairs Carefully**: Store your key pairs securely and avoid losing them.

### How to Prevent / Defend

#### Detection

1. **Monitor Instance Usage**: Use AWS CloudWatch to monitor CPU usage, disk I/O, and network traffic.
2. **Audit Security Group Changes**: Enable AWS CloudTrail to track changes to security groups.

#### Prevention

1. **Use IAM Roles**: Attach IAM roles to your instances to grant permissions securely.
2. **Enable EBS Encryption**: Encrypt your EBS volumes to protect sensitive data.
3. **Regularly Update Software**: Keep your AMIs and software up-to-date to patch vulnerabilities.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
Resources:
  MyAppServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890
      InstanceType: t2.micro
      KeyName: my-key-pair
      SecurityGroupIds:
        - sg-0abcdef1234567890
      Tags:
        - Key: Name
          Value: MyAppServer
```

##### Fixed Code

```yaml
Resources:
  MyAppServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890
      InstanceType: t2.micro
      KeyName: my-key-pair
      SecurityGroupIds:
        - Ref: MySecurityGroup
      BlockDeviceMappings:
        - DeviceName: /dev/sda1
          Ebs:
            VolumeSize: 8
            VolumeType: gp2
            DeleteOnTermination: true
            Encrypted: true
      Tags:
        - Key: Name
          Value: MyAppServer
  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for MyAppServer
      VpcId: vpc-0abcdef1234567890
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0
```

### Real-World Examples

#### Recent CVEs and Breaches

1. **CVE-2021-3539**: A vulnerability in the AWS SDK for Java allowed attackers to execute arbitrary code on EC2 instances.
2. **Breaches**: In 2022, several companies experienced breaches due to misconfigured security groups, allowing unauthorized access to their EC2 instances.

### Practice Labs

For hands-on practice with EC2 instances, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on securing EC2 instances.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.
- **WebGoat**: An interactive web security training application provided by OWASP.

These labs provide practical experience in setting up and securing EC2 instances, helping you to apply the concepts learned in this chapter.

---
<!-- nav -->
[[07-Introduction to AWS EC2 Instances and Terraform Configuration|Introduction to AWS EC2 Instances and Terraform Configuration]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[09-Introduction to Infrastructure as Code (IaC)|Introduction to Infrastructure as Code (IaC)]]
