---
tags: [owasp, standards, framework, vapt]
difficulty: intermediate
module: "57 - OWASP Frameworks and Standards"
topic: "57.09 OWASP Dependency-Check"
---

# OWASP Dependency-Check

## 1. Introduction to Dependency-Check and SCA
**OWASP Dependency-Check** is a prominent, open-source Software Composition Analysis (SCA) tool. Its primary function is to identify project dependencies and check if there are any known, publicly disclosed vulnerabilities associated with them.

Modern applications are rarely built from scratch; they rely heavily on third-party open-source libraries and frameworks. If one of these dependencies has a known vulnerability (a CVE), the application inherits that vulnerability. This risk is addressed in the OWASP Top 10 as "Vulnerable and Outdated Components."

Dependency-Check solves this by deeply analyzing applications, building an inventory of components, and querying vulnerability databases.

---

## 2. Dependency-Check Architecture & Workflow

The following ASCII diagram shows how Dependency-Check processes an application, extracts metadata, correlates with databases, and generates a report.

```text
+---------------------+
|   Application Code  |
|  & Build Manifests  | (pom.xml, package.json, requirements.txt)
+---------+-----------+
          |
          v
+-------------------------------------------------------------+
|               OWASP Dependency-Check Engine                 |
|                                                             |
|  1. [Evidence Collection]                                   |
|      (Parses manifests, extracts JAR/DLL metadata, hashes)  |
|               |                                             |
|               v                                             |
|  2. [CPE Identification]                                    |
|      (Maps evidence to Common Platform Enumeration format)  |
|               |                                             |
|               v                                             |
|  3. [Vulnerability Database Correlation]                    |
|      (Queries local/remote NVD, Sonatype OSS Index, etc.)   |
+-------------------------+-----------------------------------+
          |               ^
          | Updates       | Fetches CVE/CVS scores
          v               v
+---------------------+ +-------------------------------------+
| Local H2 Database   | | External Vulnerability Databases    |
| (NVD Mirror Cache)  | | (NVD, GitHub Advisories, OSS Index) |
+---------------------+ +-------------------------------------+
          |
          v
+-------------------------------------------------------------+
|                      Report Generation                      |
|  [ HTML Report ]   [ XML Report ]   [ JSON Report ]         |
|  (Human Readable)  (SonarQube)      (Custom Tooling)        |
+-------------------------------------------------------------+
```

---

## 3. How Dependency-Check Works

### 3.1 Analyzers
Dependency-Check uses specialized analyzers to inspect different types of files:
*   **Archive Analyzers:** Inspects ZIP, TAR, WAR, and EAR files to find nested dependencies.
*   **Language-Specific Analyzers:**
    *   *Java:* Inspects JAR manifests, `pom.xml` (Maven), `build.gradle` (Gradle).
    *   *JavaScript/Node.js:* Inspects `package.json`, `package-lock.json`, `yarn.lock`.
    *   *Python:* Inspects `requirements.txt`, `setup.py`.
    *   *.NET:* Inspects DLL and EXE metadata, `packages.config`.
    *   *Ruby:* Inspects `Gemfile.lock`.

### 3.2 Evidence Collection and CPE Generation
The tool extracts "evidence" (vendor names, product names, versions) from files. It uses this evidence to construct a **Common Platform Enumeration (CPE)** string.
Example: `cpe:2.3:a:apache:struts:2.3.31:*:*:*:*:*:*:*`

### 3.3 Database Matching
Dependency-Check compares the generated CPEs against the **National Vulnerability Database (NVD)** hosted by NIST. If a match is found, the tool extracts the associated CVE numbers, CVSS scores, and mitigation guidance.

---

## 4. Installation and Usage Examples

Dependency-Check can be run via CLI, built into build tools (Maven/Gradle), or integrated into CI/CD pipelines.

### 4.1 CLI Usage
Running a scan on a directory containing application source code and libraries:
```bash
dependency-check.sh --project "MyWebApp" --scan /path/to/source --format HTML --format JSON --out /path/to/reports
```
*Key Flags:*
*   `--project`: The name of the project.
*   `--scan`: Path to analyze.
*   `--format`: Output formats (HTML, XML, CSV, JSON).
*   `--nvdApiKey`: Highly recommended; use an API key from NIST to speed up database updates and avoid rate limiting.
*   `--failOnCVSS`: Fails the build if a vulnerability with a score equal to or greater than the specified value is found (e.g., `--failOnCVSS 7.0`).

### 4.2 Maven Integration
Adding Dependency-Check to a `pom.xml` to run during the `verify` phase:
```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.owasp</groupId>
      <artifactId>dependency-check-maven</artifactId>
      <version>8.3.1</version>
      <executions>
        <execution>
          <goals>
            <goal>check</goal>
          </goals>
        </execution>
      </executions>
      <configuration>
        <failBuildOnCVSS>7.0</failBuildOnCVSS>
        <suppressionFiles>
          <suppressionFile>project-suppression.xml</suppressionFile>
        </suppressionFiles>
      </configuration>
    </plugin>
  </plugins>
</build>
```

### 4.3 CI/CD Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    stages {
        stage('Build & SCA Scan') {
            steps {
                sh 'mvn clean verify'
            }
        }
    }
    post {
        always {
            dependencyCheckPublisher pattern: 'target/dependency-check-report.xml'
        }
    }
}
```

---

## 5. False Positives and Suppression

Due to the heuristic nature of evidence collection, Dependency-Check occasionally misidentifies a library, resulting in a false positive.

### Handling False Positives:
1.  Review the HTML report to identify the incorrect CPE.
2.  Use the "Suppress" button in the HTML report to generate XML suppression rules.
3.  Add the generated XML to a `suppression.xml` file.

**Example Suppression XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<suppressions xmlns="https://jeremylong.github.io/DependencyCheck/dependency-suppression.1.3.xsd">
    <suppress>
        <notes><![CDATA[
            False positive: This internal library 'spring-utils-custom-1.0.jar' is being mistaken 
            for the official Spring Framework, triggering CVE-2022-22965.
        ]]></notes>
        <gav regex="true">^com\.internal\.utils:spring-utils-custom:.*$</gav>
        <cve>CVE-2022-22965</cve>
    </suppress>
</suppressions>
```

---

## 6. Optimization and Database Mirroring

Downloading the NVD database during every CI pipeline run is extremely slow and can lead to IP bans from NIST.
**Best Practices:**
1.  **Centralized Database:** Set up a centralized relational database (e.g., PostgreSQL or MySQL) to host the NVD data. Configure all CI runners to point to this central database rather than fetching from NIST directly.
2.  **Caching Data Directory:** If using the default H2 database, cache the Dependency-Check data directory between pipeline executions.
3.  **Use NVD API Key:** Always supply an NVD API key to prevent rate limiting.

---

## 7. Chaining Opportunities

While Dependency-Check is a defensive tool, understanding SCA is crucial for attackers:
*   **Supply Chain Reconnaissance:** Attackers use similar tools to scan public repositories or extracted web application archives (WAR/APK files) to identify outdated components.
*   **Vulnerability Chaining:** If Dependency-Check reveals an application uses an outdated version of Jackson (a Java JSON parser), an attacker might chain this with an exposed API endpoint that accepts JSON, leading to Insecure Deserialization (RCE).
*   **Log4Shell (CVE-2021-44228):** Dependency-Check is directly used to hunt down nested dependencies of Log4j deep within fat JARs that would be missed by simple grep commands.

---

## 8. Related Notes
*   [[06 - OWASP SAMM Software Assurance Maturity Model]] - Relates to the Secure Build practice.
*   [[09 - Vulnerable and Outdated Components]]
*   [[08 - OWASP Cheat Sheet Series Key Sheets]]
*   [[03 - Injection]]
