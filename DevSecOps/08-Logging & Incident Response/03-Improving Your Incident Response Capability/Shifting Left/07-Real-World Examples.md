---
course: DevSecOps
topic: Improving Your Incident Response Capability
tags: [devsecops]
---

## Real-World Examples

### Example: CVE-2021-44228 (Log4Shell)

CVE-2021-44228, also known as Log4Shell, is a critical vulnerability in the Apache Log4j library. This vulnerability allowed attackers to execute arbitrary code on affected systems, leading to widespread exploitation.

#### Impact

Log4Shell affected millions of systems worldwide, including major organizations such as Apple, Tesla, and Microsoft. The vulnerability was exploited to gain unauthorized access to systems, steal sensitive data, and deploy malware.

#### Prevention

To prevent similar vulnerabilities in the future, organizations should:

- **Keep Dependencies Updated**: Regularly update dependencies to ensure that they are patched against known vulnerabilities.
- **Use Dependency Checkers**: Integrate dependency checkers into the build process to identify and address vulnerable dependencies.
- **Implement Security Controls**: Implement security controls such as network segmentation and intrusion detection systems to detect and mitigate attacks.

#### Example: Dependency Checker Integration

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Dependency Check') {
            steps {
                sh 'dependency-check --project "My Project" --scan .'
            }
        }
    }
}
```

In this example, the Jenkins pipeline integrates a dependency checker (`Dependency-Check`) to scan the project's dependencies for vulnerabilities during the build stage.

### Example: SolarWinds Supply Chain Attack

The SolarWinds supply chain attack is one of the most significant cyberattacks in recent history. The attack involved the compromise of SolarWinds' software development infrastructure, leading to the distribution of malicious updates to thousands of customers.

#### Impact

The SolarWinds attack affected numerous organizations, including government agencies, technology companies, and financial institutions. The attackers gained unauthorized access to systems, stole sensitive data, and conducted espionage activities.

#### Prevention

To prevent similar supply chain attacks in the future, organizations should:

- **Implement Secure Development Practices**: Follow secure development practices to ensure that the software development process is secure.
- **Use Software Bill of Materials (SBOM)**: Maintain a software bill of materials to track the components used in the software and ensure that they are secure.
- **Conduct Third-Party Risk Assessments**: Conduct regular third-party risk assessments to identify and mitigate risks associated with third-party vendors.

#### Example: SBOM Maintenance

```json
{
  "components": [
    {
      "name": "SolarWinds.Orion.Core.BusinessLayer",
      "version": "2020.2.0.1514",
      "licenses": ["MIT"],
      "dependencies": [
        {
          "name": "Newtonsoft.Json",
          "version": "12.0.3"
        },
        {
          "name": "System.Net.Http",
          "version": "4.3.4"
        }
      ]
    }
  ]
}
```

In this example, the software bill of materials (SBOM) tracks the components used in the software and ensures that they are secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/Shifting Left/06-Incorporating Security in DevOps Pipeline|Incorporating Security in DevOps Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/Shifting Left/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/Shifting Left/08-Shifting Left Improving Your Incident Response Capability|Shifting Left Improving Your Incident Response Capability]]
