---
course: DevSecOps
topic: Automating Third Party Libraries Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why is it important to regularly test for outdated and insecure third-party libraries in your application?**

Regularly testing for outdated and insecure third-party libraries is crucial because the security landscape evolves rapidly. Even if your application's codebase remains unchanged, the security of third-party libraries can degrade over time due to newly discovered vulnerabilities. For example, the MD5 hashing algorithm, once considered secure, is now considered broken. Similarly, third-party libraries may contain vulnerabilities that can compromise the security of your application. Regular testing helps identify and mitigate these risks, ensuring that your application remains secure.

**Q2. How do third-party library scanners work?**

Third-party library scanners operate by first downloading lists of known vulnerabilities from various sources, such as vendors and centralized organizations. These scanners then fingerprint the libraries used in the application by generating a list of all components. They match these components against the vulnerability lists. If a match is found, the scanner alerts the user. A good scanner uses multiple up-to-date sources for vulnerability reports and can parse manifests or bills of materials to get detailed information about the versions of the libraries in use.

**Q3. What are some characteristics of a good third-party library scanner?**

A good third-party library scanner should:

1. Use multiple up-to-date sources for vulnerability reports to ensure comprehensive coverage.
2. Be able to fingerprint a wide range of frameworks and understand different versions to accurately detect vulnerabilities.
3. Parse manifests or bills of materials to obtain detailed information about the versions of the libraries in use.
4. Generate alerts for outdated and insecure libraries and provide an overview of all components in use.
5. Function asynchronously, allowing periodic scans independent of changes in the codebase.

**Q4. Where can you deploy or use third-party library scanners in the software development lifecycle?**

Third-party library scanners can be deployed or used in several phases of the software development lifecycle:

1. **Build Phase:** Scanning can occur when the automation or build server retrieves code from the repository, fingerprints it, and matches it against known vulnerabilities.
2. **Artifact Storage Phase:** Scanning can be performed when artifacts are pushed to a registry or stored on an artifact server.
3. **Pre-Commit Phase:** Some integrated development environments (IDEs) can scan for outdated third-party libraries before code is committed, preventing insecure code from being checked into the repository.

**Q5. Why is it recommended to perform periodic scans rather than scanning immediately after every commit?**

Periodic scans are recommended because immediate scans after every commit can muddy the results. For example, if a developer makes a change and checks in the code, the scanner might detect an issue with a third-party library that is unrelated to the recent change. This can lead to confusion and unnecessary delays in the development process. By performing periodic scans asynchronously, you can clearly attribute build failures to specific issues, such as third-party vulnerabilities, without interfering with the continuous integration and deployment processes.

**Q6. Explain how the OASP Dependency Check tool works and its role in identifying vulnerabilities in third-party libraries.**

OASP Dependency Check is an open-source tool designed to detect publicly disclosed vulnerabilities in third-party libraries used in applications. It works by:

1. Downloading lists of known vulnerabilities from various sources.
2. Fingerprinting the libraries used in the application.
3. Matching the fingerprinted libraries against the vulnerability lists.
4. Generating alerts for any matches found.

By integrating OASP Dependency Check into the build or deployment pipeline, developers can proactively identify and address vulnerabilities in third-party libraries, thereby enhancing the overall security posture of their applications.

**Q7. Provide an example of a recent breach or CVE related to third-party library vulnerabilities and explain how it could have been prevented with proper scanning.**

One notable example is the Log4j vulnerability (CVE-2021-44228), which affected the widely-used Apache Log4j logging utility. This vulnerability allowed attackers to execute arbitrary code on vulnerable servers, leading to numerous breaches across various industries. Proper scanning with tools like OASP Dependency Check could have identified the presence of the vulnerable Log4j version in applications and alerted developers to update to a secure version. Regular scanning would have helped organizations stay ahead of such vulnerabilities, reducing the risk of exploitation.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/Third Party Libraries Scanners/11-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/Third Party Libraries Scanners/00-Overview|Overview]]
