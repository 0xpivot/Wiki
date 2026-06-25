---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Repository for Code and Artifacts

### What Are They?

The **repository** is where the source code and built artifacts are stored. Typically, this includes version control systems like Git (GitHub, GitLab, Bitbucket) for source code and artifact repositories like Nexus, Artifactory, or Docker Hub for built artifacts.

### Why Are They Important?

Repositories provide a centralized location for storing and managing code and artifacts. This ensures that everyone on the team is working with the same version of the code and that artifacts are properly versioned and accessible.

### How Do They Work?

#### Source Code Repository

Source code repositories use version control systems to manage changes. Each commit represents a change in the codebase, and branches allow developers to work on features independently.

Example of a Git workflow:

```bash
# Clone the repository
git clone https://github.com/example/repo.git

# Create a new branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push the branch
git push origin feature/new-feature
```

#### Artifact Repository

Artifact repositories store built artifacts and provide versioning and access control. For example, using Nexus to store Maven artifacts:

```xml
<!-- pom.xml -->
<distributionManagement>
    <repository>
        <id>nexus</id>
        <url>http://localhost:8081/repository/maven-releases/</url>
    </repository>
    <snapshotRepository>
        <id>nexus</id>
        <url>http://localhost:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
</distributionManagement>
```

### Real-World Example: Recent Breach

In the Equifax data breach (CVE-2017-5638), attackers exploited a vulnerability in Apache Struts, which was due to outdated and unpatched versions of the software. This highlights the importance of maintaining up-to-date and properly versioned artifacts in repositories.

### How to Prevent / Defend

#### Secure Source Code Repositories

- **Use HTTPS**: Ensure that all communication with the repository is encrypted.
- **Two-factor authentication**: Enable two-factor authentication for repository access.
- **Regular audits**: Perform regular audits of repository permissions and access logs.

#### Secure Artifact Repositories

- **Version control**: Ensure that all artifacts are properly versioned and tagged.
- **Access control**: Limit access to artifact repositories to trusted personnel.
- **Regular updates**: Keep artifact repositories up to date with the latest security patches.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/06-Network Communication|Network Communication]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/08-Test Environment|Test Environment]]
