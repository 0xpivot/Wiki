---
course: DevSecOps
topic: Designing DevSecOps for Test, Release, and Operate SDLC Phases
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the importance of testing security certificates during the deploy phase?**

Testing security certificates during the deploy phase is crucial to ensure that all Transport Layer Security (TLS) certificates are valid, within their expiration dates, and issued correctly. This step is necessary because different environments may use different types of certificates, and verifying their validity helps prevent man-in-the-middle attacks and other security breaches. Tools like SSL Labs can be used to test and grade the security of TLS configurations.

**Q2. How does application hardening reduce the risk of security breaches during the deploy phase?**

Application hardening reduces the risk of security breaches by minimizing the attack surface area. By hardening servers and applications, unnecessary services and features are disabled, default settings are secured, and vulnerabilities are mitigated. This makes it harder for attackers to find and exploit weaknesses. Using pre-hardened images from trusted sources, such as those certified by the Center for Internet Security (CIS), further enhances security by ensuring that the base system is already configured securely.

**Q3. Explain how to use SSL Labs to test the security of your website’s TLS certificates.**

To use SSL Labs to test the security of your website’s TLS certificates, follow these steps:

1. Go to the SSL Labs website: https://www.ssllabs.com/ssltest/
2. Enter the URL of your website into the provided field.
3. Click the "Submit" button to start the test.
4. SSL Labs will analyze the certificate and provide a detailed report including a letter grade (A-F) and specific details about the security configuration.

For example, if you were to test `RichardHarper.com`, SSL Labs would provide a comprehensive analysis of the TLS configuration, including the certificate chain, protocol support, cipher strength, and more.

**Q4. What are some benefits of using pre-hardened images from the Amazon Marketplace during the deploy phase?**

Using pre-hardened images from the Amazon Marketplace during the deploy phase offers several benefits:

1. **Reduced Attack Surface**: Pre-hardened images come with unnecessary services and features disabled, which minimizes the potential entry points for attackers.
2. **Compliance**: Many pre-hardened images adhere to industry standards such as the Center for Internet Security (CIS) benchmarks, ensuring that the images meet best practices for security.
3. **Time-Saving**: Instead of manually hardening each server or application, pre-hardened images save time and effort by providing a secure baseline configuration out-of-the-box.
4. **Consistency**: Using pre-hardened images ensures consistency across multiple deployments, making it easier to maintain a uniform security posture.

Examples of pre-hardened images include the CIS Red Hat Enterprise Linux 7 hardened image and the Microsoft Windows Server 2016 hardened image.

**Q5. How can you integrate the selection of pre-hardened images into your deployment scripts?**

Integrating the selection of pre-hardened images into your deployment scripts involves specifying the appropriate AMI (Amazon Machine Image) ID in your automation tool. Here’s an example using AWS CloudFormation:

```yaml
Resources:
  WebServer:
    Type: 'AWS::EC2::Instance'
    Properties:
      ImageId: ami-0c94855ba95c71c99 # Example of a CIS-hardened AMI
      InstanceType: t2.micro
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
```

In this example, the `ImageId` property specifies the AMI ID of a CIS-hardened image. By using this approach, you can ensure that every instance launched through your deployment scripts starts with a hardened configuration, reducing the attack surface area.

**Q6. Why is it important to regularly re-evaluate and update the hardening configurations of your deployed systems?**

Regularly re-evaluating and updating the hardening configurations of your deployed systems is important because:

1. **New Vulnerabilities**: New vulnerabilities are discovered frequently, and regular updates help mitigate these risks.
2. **Changing Threat Landscape**: The threat landscape evolves, and new attack vectors emerge. Regular evaluations ensure that your defenses remain effective against current threats.
3. **Software Updates**: Software updates often include security patches and improvements. Ensuring that your hardening configurations align with these updates helps maintain a secure environment.
4. **Compliance Requirements**: Compliance requirements may change over time, necessitating updates to your hardening configurations to stay compliant.

For example, the recent Log4j vulnerability (CVE-2021-44228) highlighted the importance of keeping software updated and re-evaluating configurations to address newly discovered vulnerabilities.

---
<!-- nav -->
[[02-Testing Security Certificates in the Deploy Phase|Testing Security Certificates in the Deploy Phase]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/03-Designing DevSecOps for Test, Release, and Operate SDLC Phases/01-DevSecOps in the Deploy Phase/00-Overview|Overview]]
