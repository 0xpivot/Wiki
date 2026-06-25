---
course: DevSecOps
topic: Understanding Automated Security Testing
tags: [devsecops]
---

## Understanding Automated Security Testing

### Definition of Vulnerability

A **vulnerability** is a weakness in a system, application, or infrastructure that can be exploited by an attacker to cause harm. This weakness could be a bug in the code, a misconfiguration, or a flaw in the design. What distinguishes a vulnerability from a general weakness is the potential for exploitation. A vulnerability is a specific type of weakness that can be leveraged by an attacker to gain unauthorized access, steal data, or disrupt services.

#### Why Does This Matter?

Understanding the distinction between a general weakness and a vulnerability is crucial because it helps prioritize security efforts. Not all weaknesses are exploitable, but those that are can lead to significant security breaches. By identifying and addressing vulnerabilities, organizations can reduce their exposure to cyber threats.

### Automated Vulnerability Scanners

Automated vulnerability scanners are tools designed to identify known vulnerabilities in systems, applications, and networks. These scanners perform a series of steps to detect vulnerabilities:

1. **Fingerprinting Assets**: The scanner identifies and characterizes the assets in the environment.
2. **Ingesting Known Vulnerabilities**: The scanner retrieves a list of known vulnerabilities from various sources.
3. **Comparing Assets with Vulnerabilities**: The scanner checks if the identified assets match any known vulnerabilities.

#### How It Works Under the Hood

Let's break down each step in detail:

1. **Fingerprinting Assets**:
    - **Checksums on Source Code**: One method of fingerprinting is to compute checksums (hashes) of the source code. This allows the scanner to uniquely identify the codebase.
    - **Network Scanning**: For network assets, the scanner may perform port scans, service identification, and OS detection.
    - **Container Scanning**: For container images, the scanner may inspect the image layers and metadata.

2. **Ingesting Known Vulnerabilities**:
    - **Sources**: The scanner contacts databases such as the National Vulnerability Database (NVD), Common Vulnerabilities and Exposures (CVE), and vendor-specific databases.
    - **Data Format**: The data is often in formats like JSON or XML, containing details about the vulnerability, such as CVE ID, description, severity, and affected versions.

3. **Comparing Assets with Vulnerabilities**:
    - **Matching**: The scanner compares the fingerprints of the assets with the known vulnerabilities. If a match is found, the scanner reports the vulnerability.

#### Real-World Example: CVE-2021-44228 (Log4j)

One of the most significant vulnerabilities in recent years is **CVE-2021-44228**, also known as the Log4j vulnerability. This vulnerability affects the Apache Log4j logging library, allowing attackers to execute arbitrary code on affected systems.

```mermaid
sequenceDiagram
    participant Scanner
    participant NVD
    participant Asset
    Scanner->>NVD: Retrieve CVE-2021-44228 details
    NVD-->>Scanner: CVE-2021-44228 details
    Scanner->>Asset: Check for Log4j version
    Asset-->>Scanner: Log4j version 2.14.1
    Scanner-->>Scanner: Compare with CVE-2021-44228
    Scanner-->>Scanner: Vulnerability detected
```

### Types of Automated Vulnerability Scanners

There are several types of automated vulnerability scanners, each tailored to specific environments:

1. **Network Vulnerability Scanners**:
    - **Example**: Nessus, OpenVAS
    - **Functionality**: Scans network devices, servers, and endpoints for known vulnerabilities.
    - **Real-World Example**: In the Equifax breach (CVE-2017-5638), a network vulnerability scanner could have detected the unpatched Apache Struts server.

2. **Container Vulnerability Scanners**:
    - **Example**: Clair, Trivy
    - **Functionality**: Scans container images for known vulnerabilities.
    - **Real-World Example**: The Docker Hub incident (CVE-2021-29449) could have been mitigated by a container vulnerability scanner.

### Pitfalls and Common Mistakes

While automated vulnerability scanners are powerful tools, they are not infallible. Here are some common pitfalls and mistakes:

1. **False Positives/Negatives**:
    - **False Positives**: The scanner may report a vulnerability that does not exist.
    - **False Negatives**: The scanner may miss a vulnerability that does exist.
    - **Mitigation**: Regularly update the scanner's database and manually verify reported vulnerabilities.

2. **Outdated Databases**:
    - **Problem**: Using outdated vulnerability databases can lead to missed detections.
    - **Mitigation**: Ensure the scanner is regularly updated with the latest vulnerability data.

3. **Configuration Issues**:
    - **Problem**: Incorrect configuration can limit the scanner's effectiveness.
    - **Mitigation**: Follow best practices for configuring the scanner and review the documentation.

### How to Prevent / Defend

To effectively prevent and defend against vulnerabilities detected by automated scanners, follow these steps:

1. **Regular Scanning**:
    - **Frequency**: Perform regular scans to catch new vulnerabilities.
    - **Tooling**: Use tools like Nessus, OpenVAS, Clair, and Trivy.

2. **Patch Management**:
    - **Update**: Keep all systems and applications up-to-date with the latest patches.
    - **Automation**: Use automation tools to manage patching processes.

3. **Secure Coding Practices**:
    - **Training**: Train developers in secure coding practices.
    - **Code Reviews**: Implement regular code reviews to catch vulnerabilities early.

4. **Configuration Hardening**:
    - **Best Practices**: Follow security best practices for configuring systems and applications.
    - **Tools**: Use tools like CIS Benchmarks for configuration hardening.

### Complete Example: Network Vulnerability Scan

Here is a complete example of a network vulnerability scan using Nessus:

#### Full HTTP Request and Response

```http
POST /api/1/scans HTTP/1.1
Host: nessus.example.com
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/json

{
    "uuid": "12345678-1234-1234-1234-1234567890ab",
    "settings": {
        "launch_now": true,
        "targets": ["192.168.1.0/24"],
        "plugins": {
            "exploit": {
                "enabled": false
            }
        }
    }
}
```

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: application/json

{
    "scan_id": 1,
    "name": "Network Scan",
    "status": "running"
}
```

#### Expected Result

The scan will run and report any vulnerabilities found in the specified network range.

### Complete Example: Container Vulnerability Scan

Here is a complete example of a container vulnerability scan using Trivy:

#### Full Command and Output

```bash
trivy image --severity CRITICAL,HIGH myregistry/myimage:latest
```

```plaintext
2023-03-20T12:00:00Z    INFO    Detecting OS packages in myregistry/myimage:latest...
2023-03-20T12:00:00Z    INFO    Number of language-specific files: 0
2023-03-20T12:00:00Z    INFO    Detecting Alpine vulnerabilities...
2023-03-20T12:00:00Z    INFO    Checking for updates of the DB...
2023-03-20T12:00:00Z    INFO    Found 1 vulnerability

myregistry/myimage:latest (alpine:3.14)
-------------------------------------------------------------------------------
Total: 1 (CRITICAL: 1, HIGH: 0, MEDIUM: 0, LOW: 0, UNKNOWN: 0)

+--------------------------+------------------+----------+-------------------+--------------------------------+
| VULNERABILITY            | SEVERITY         | STATUS   | PACKAGE           | FIXED IN                       |
+--------------------------+------------------+----------+-------------------+--------------------------------+
| CVE-2021-44228           | CRITICAL         |          | log4j             | 2.15.0                        |
+--------------------------+------------------+----------+-------------------+--------------------------------+

2023-03-20T12:00:00Z    INFO    Completed in 1.00s
```

#### Expected Result

The scan will report any critical or high-severity vulnerabilities found in the specified container image.

### Hands-On Labs

For hands-on practice with automated security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for web application security testing.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **CloudGoat**: A set of labs for practicing cloud security on AWS.
- **Pacu**: A framework for automating security assessments on AWS.

These labs provide practical experience in identifying and mitigating vulnerabilities, reinforcing the concepts learned in this chapter.

### Conclusion

Automated vulnerability scanners are essential tools in the DevSecOps toolkit. They help identify known vulnerabilities in systems, applications, and networks, enabling organizations to take proactive measures to mitigate risks. By understanding the mechanics of these scanners and implementing best practices, organizations can significantly enhance their security posture.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/Types of Security Testing/03-Understanding Automated Security Testing Third-Party Library Scanners|Understanding Automated Security Testing Third-Party Library Scanners]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/Types of Security Testing/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/Types of Security Testing/05-Vulnerability Scanners|Vulnerability Scanners]]
