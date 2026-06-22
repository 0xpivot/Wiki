---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of using a sidecar container in a DevSecOps pipeline.**

The sidecar container pattern is used to run additional services alongside the main application container. In the context of DevSecOps, a sidecar container can be used to perform security scans on the main application container. This allows for automated security testing integrated into the continuous integration and delivery pipeline. By running a sidecar container, you can ensure that your application is scanned for vulnerabilities every time it is built or deployed, thus maintaining a high level of security throughout the development lifecycle.

**Q2. How would you configure a NICTO scan to minimize false positives?**

To minimize false positives in a NICTO scan, you can configure the tool to exclude certain plugins that tend to generate a large number of false positives. For example, in the lecture, the `sitefiles` plugin was disabled because it generated many false positives. Additionally, you can customize the scan settings to target specific areas of the application that are most likely to contain vulnerabilities. Here’s an example of how to disable the `sitefiles` plugin:

```bash
nmap --script=http-nikto.nse --script-args=nikto.exclude=sitefiles <target>
```

By carefully selecting and disabling plugins, you can reduce the number of false positives and focus on genuine security issues.

**Q3. Describe how to integrate a health check into a build pipeline to ensure the application is ready for scanning.**

Integrating a health check into a build pipeline ensures that the application is fully operational before security scans are performed. This can be done by adding a stage in the pipeline that performs a `curl` request to the application's endpoint until it returns a successful status code. Here’s an example of how this can be implemented in a Jenkins pipeline:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
        stage('Run Sidecar') {
            steps {
                sh 'docker run -d --name sidecar --network lab -p 3000:3000 myapp'
            }
        }
        stage('Health Check') {
            steps {
                script {
                    def status = 1
                    while (status != 0) {
                        status = sh(returnStatus: true, script: 'curl --fail http://localhost:3000')
                        sleep 5
                    }
                }
            }
        }
        stage('Security Scan') {
            steps {
                sh 'nmap --script=http-nikto.nse --script-args=nikto.exclude=sitefiles http://localhost:3000 > report.html'
            }
        }
        stage('Stop Sidecar') {
            steps {
                sh 'docker stop sidecar'
            }
        }
    }
}
```

In this example, the `Health Check` stage continuously attempts to reach the application until it responds successfully. Once the application is up and running, the `Security Scan` stage runs the NICTO scan.

**Q4. Explain why it is important to verify whether scan results are false positives or actual vulnerabilities.**

Verifying whether scan results are false positives or actual vulnerabilities is crucial because false positives can lead to wasted time and resources. False positives occur when the scanner incorrectly identifies a potential vulnerability that does not actually exist. On the other hand, actual vulnerabilities represent real security risks that need to be addressed. 

For example, in the lecture, the scanner identified an FTP directory that was accessible. Upon further investigation, it was confirmed that this was indeed a real vulnerability, as sensitive files were exposed. By verifying the results, you can prioritize fixing the actual vulnerabilities while ignoring the false positives, thereby improving the overall security posture of the application.

**Q5. How would you exploit a misconfigured XXSS HATP protection header?**

A misconfigured XXSS HATP (Cross-Site Scripting HTTP Anti-Protection) header can allow an attacker to inject malicious scripts into web pages viewed by other users. To exploit this, an attacker would typically craft a URL that includes the malicious script and send it to a victim. When the victim clicks on the link, the script executes within their browser, potentially stealing sensitive information or performing unauthorized actions.

Here’s an example payload that could be used to exploit a misconfigured XXSS HATP header:

```html
<script>alert('XSS');</script>
```

If the application does not properly sanitize user input, this script could be injected into a webpage and executed when the victim visits the page. To prevent such attacks, it is essential to configure the XXSS HATP header correctly and implement proper input validation and sanitization mechanisms.

**Q6. Discuss recent real-world examples where misconfigurations led to security breaches.**

One notable recent example is the Capital One data breach in 2019, where a misconfigured web application firewall (WAF) allowed an attacker to access sensitive customer data. The WAF was improperly configured, allowing the attacker to bypass intended security controls and gain unauthorized access to the data.

Another example is the Twitter hack in 2020, where attackers exploited a series of misconfigurations and social engineering tactics to gain access to high-profile accounts. The attackers were able to manipulate internal tools due to insufficient access controls and misconfigurations, leading to a significant breach of trust and security.

These examples highlight the importance of proper configuration and regular security audits to prevent such vulnerabilities from being exploited.

---
<!-- nav -->
[[05-Automating Infrastructure Security Testing|Automating Infrastructure Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/Demo Running Nikto and Using the Sidecar Testing Pattern/00-Overview|Overview]]
