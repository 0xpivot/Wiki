---
course: DevSecOps
topic: Automating Third Party Libraries Security Testing
tags: [devsecops]
---

## Real-World Examples and Recent CVEs

### Example: CVE-2021-44228 (Log4j)

The Log4j vulnerability (CVE-2021-44228) is a critical remote code execution flaw that affects Apache Log4j versions 2.0-beta9 through 2.14.1. This vulnerability was widely exploited, leading to numerous breaches and attacks.

#### Impact

The Log4j vulnerability allowed attackers to execute arbitrary code on affected systems, leading to potential data theft, system compromise, and other severe consequences.

#### Mitigation

To mitigate the risk of the Log4j vulnerability, organizations should:

1. **Update Log4j**: Upgrade to the latest version of Log4j (2.15.0 or higher).
2. **Patch Management**: Implement a robust patch management process to ensure timely updates.
3. **Security Scanning**: Use tools like `Snyk` or `WhiteSource` to scan for vulnerabilities in third-party libraries.

### Example: CVE-2022-22965 (Spring Framework)

The Spring Framework vulnerability (CVE-2022-22965) is a critical remote code execution flaw that affects Spring Framework versions 5.3.0 through 5.3.17 and 5.2.0 through 5.2.19. This vulnerability allows attackers to execute arbitrary code on affected systems.

#### Impact

The Spring Framework vulnerability allowed attackers to execute arbitrary code on affected systems, leading to potential data theft, system compromise, and other severe consequences.

#### Mitigation

To mitigate the risk of the Spring Framework vulnerability, organizations should:

1. **Update Spring Framework**: Upgrade to the latest version of Spring Framework (5.3.18 or higher).
2. **Patch Management**: Implement a robust patch management process to ensure timely updates.
3. **Security Scanning**: Use tools like `Snyk` or `WhiteSource` to scan for vulnerabilities in third-party libraries.

---
<!-- nav -->
[[09-Pre-Commit Phase Scanning|Pre-Commit Phase Scanning]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/Third Party Libraries Scanners/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/Third Party Libraries Scanners/11-Conclusion|Conclusion]]
