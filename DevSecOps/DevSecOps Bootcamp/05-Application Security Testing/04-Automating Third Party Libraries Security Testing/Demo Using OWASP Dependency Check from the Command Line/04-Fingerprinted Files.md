---
course: DevSecOps
topic: Automating Third Party Libraries Security Testing
tags: [devsecops]
---

## Fingerprinted Files

- File 1: No known vulnerabilities
- File 2: No known vulnerabilities
- ...
```

### Adding a Vulnerable Library

To demonstrate the tool’s effectiveness, let’s introduce a known vulnerable library.

#### Downloading a Vulnerable Version

```bash
curl -O https://example.com/jcurry-1.9.0.jar
```

This command downloads a vulnerable version of the JCurry library.

### Re-running the Scan

After introducing the vulnerable library, re-run the OWASP Dependency Check command:

```bash
docker run --rm -v $(pwd):/src owasp/dependency-check:5.3.0 --project MyProject --scan /src --out /src/report
```

### Analyzing the New Report

The new report should now indicate the presence of a known vulnerability in the JCurry library.

#### Example Vulnerability Report

```markdown
# Report Summary

- **Project Name**: MyProject
- **Dependencies Scanned**: 101
- **Known Vulnerabilities Found**: 1

---
<!-- nav -->
[[03-Automating Third-Party Libraries Security Testing Using OWASP Dependency Check|Automating Third-Party Libraries Security Testing Using OWASP Dependency Check]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/Demo Using OWASP Dependency Check from the Command Line/00-Overview|Overview]] | [[05-Vulnerable Dependencies|Vulnerable Dependencies]]
