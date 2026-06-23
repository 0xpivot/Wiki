---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the workflow for using infrastructure scanners as described in the lecture.**

The workflow for using infrastructure scanners involves several key steps:
1. Start the scanner application as a sidecar, ensuring that the testing environment closely resembles the production environment.
2. Perform the actual scanning of the application or infrastructure.
3. Filter out false positives from the scan results.
4. Formally configure the scanner to ensure it provides useful and accurate results.

This process helps identify security misconfigurations before the application is deployed to production, enhancing overall security.

**Q2. Why is it important to start the scanner application as a sidecar and ensure the testing environment resembles production?**

Starting the scanner application as a sidecar and ensuring the testing environment closely resembles the production environment is crucial because it allows for more accurate and reliable security assessments. By mimicking the production setup, you can detect potential security issues that might arise in the actual deployment environment, thereby reducing the risk of vulnerabilities being overlooked.

**Q3. How do you handle false positives when using infrastructure scanners?**

Handling false positives is a critical part of using infrastructure scanners effectively. Here’s how you can manage them:

1. **Initial Scan**: Run the initial scan and gather all the results.
2. **Review Results**: Carefully review the scan results to identify which alerts are likely to be false positives.
3. **Manual Verification**: Manually verify the identified false positives by checking the configuration or behavior of the system.
4. **Configure Scanner**: Adjust the scanner settings to exclude known false positives in future scans.
5. **Iterative Process**: Repeat the process iteratively until the number of false positives is minimized.

For example, in the demo with NICTO, significant time was spent removing false positives and tweaking the scanner settings to improve accuracy.

**Q4. What are the advantages of infrastructure scanning, and what are its limitations?**

Advantages of infrastructure scanning include:
- **Early Detection**: Identifies security misconfigurations before the application is deployed to production.
- **Compatibility**: Most web interfaces can be scanned, making it broadly applicable.
- **Proactive Security**: Helps in proactively addressing security issues rather than reacting to breaches.

Limitations include:
- **User Sessions**: Scanning user sessions is more challenging compared to anonymous access.
- **False Positives**: Requires significant effort to filter out false positives.
- **Configuration Complexity**: Achieving useful results often requires extensive configuration and tuning.

**Q5. How does trialability impact the adoption of infrastructure scanners in a development pipeline?**

Trialability refers to how easy it is to integrate and try out infrastructure scanners in a development pipeline. While it is moderately easy to add such scanners to a pipeline, achieving useful results typically requires substantial time and effort. This includes configuring the scanner properly, filtering out false positives, and fine-tuning the scanner settings. Therefore, while the initial integration may be straightforward, the full realization of benefits demands ongoing investment and optimization.

**Q6. Provide recent real-world examples of how infrastructure scanning could have prevented security breaches.**

Recent real-world examples where infrastructure scanning could have helped prevent security breaches include:

- **CVE-2021-21972**: A vulnerability in the Apache Log4j library led to widespread exploitation. Regular infrastructure scanning could have detected misconfigurations or outdated software components, potentially mitigating the impact of such vulnerabilities.
- **SolarWinds Supply Chain Attack (CVE-2020-1014)**: This attack involved the compromise of SolarWinds software, affecting numerous organizations. Infrastructure scanning could have flagged suspicious configurations or unauthorized changes in network devices, helping to detect and respond to such attacks earlier.

In both cases, proactive scanning and monitoring could have provided early warnings, enabling quicker remediation actions.

---
<!-- nav -->
[[01-Workflow for Using Infrastructure Scanners|Workflow for Using Infrastructure Scanners]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/06-Workflow and Conclusion of Infrastructure Scanning/00-Overview|Overview]]
