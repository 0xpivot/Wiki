---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.08 Code Repository Intelligence GitHub GitLab Search"
---

# 85.08 Code Repository Intelligence GitHub GitLab Search

## Introduction to Code Repository Intelligence

In the modern software development lifecycle, code repositories like GitHub, GitLab, and Bitbucket are ubiquitous. Consequently, they have also become critical hunting grounds for Cyber Threat Intelligence (CTI) analysts. Threat Actors (TAs), varying from amateur script kiddies to state-sponsored Advanced Persistent Threats (APTs), utilize these platforms extensively. 

Code Repository Intelligence involves systematically searching, analyzing, and monitoring these platforms to uncover adversary tooling, detect exposed corporate secrets, track malware development lifecycles, and de-anonymize threat actor personas. Because these platforms are built around version control (Git), they preserve a permanent, cryptographically sound history of changes, allowing analysts to uncover "deleted" mistakes made by adversaries.

## Why Threat Actors Leverage Code Repositories

Adversaries use public code repositories for several operational purposes:
1. **Malware Hosting and Staging:** TAs frequently use GitHub as a highly trusted, reliable content delivery network (CDN) to host primary and secondary payloads. Because traffic to `raw.githubusercontent.com` is generally allowed in corporate environments, it easily bypasses network web filters.
2. **Command and Control (C2) Infrastructure:** TAs leverage GitHub Issues, Gists, and repository files as dead-drop resolvers or actual C2 channels. A compromised endpoint might fetch its instructions by reading the latest commit in a specific repository.
3. **Tool Development and Forking:** Many adversaries do not write tools from scratch; they fork open-source offensive tools (e.g., Mimikatz, BloodHound, custom C2 frameworks) and modify them. Tracking these forks can reveal a TA's capabilities.
4. **Accidental Exposure (OPSEC Failures):** TAs occasionally commit configuration files containing hardcoded credentials, IP addresses of their C2 servers, or personal identifiable information (PII) before realizing their mistake and deleting them.

## Advanced Searching and Dorking on GitHub

GitHub provides powerful advanced search operators that analysts use to pinpoint specific intelligence amidst millions of repositories. This process is often referred to as "GitHub Dorking."

### Core Search Operators
- `org:companyname` or `user:username` - Restricts searches to a specific entity.
- `repo:username/reponame` - Searches within a specific repository.
- `extension:ext` - Filters by file type (e.g., `extension:pem`, `extension:json`, `extension:ps1`).
- `path:folder` - Searches within a specific directory structure.
- `language:go` - Filters by programming language, useful when tracking specific malware families known to be written in Go or Rust.

### Examples of CTI GitHub Dorks
- **Finding exposed C2 configurations:** `extension:json "port": "443" "sleep": "60" "jitter"`
- **Hunting for hardcoded AWS Keys:** `AKIA[0-9A-Z]{16} extension:txt`
- **Finding malicious PowerShell stagers:** `language:powershell "Net.WebClient" "DownloadString" "raw.githubusercontent"`
- **Tracking Cobalt Strike usage:** `extension:profile "set sleeptime" "set useragent"`

## Git History Analysis: Finding the "Deleted"

One of the most critical concepts in code repository intel is understanding the Git object model. When a user "deletes" a file and commits the change, the file is removed from the *current state* of the repository, but the historical commit containing the file remains accessible forever.

- **Commit History:** Analysts review the commit log (`git log`) to find points in time where a TA might have pushed development data instead of production data.
- **Diff Analysis:** By analyzing the differences between commits (`git diff`), analysts can see exactly what evasion techniques a TA is adding to their malware over time.
- **Accidental Commits:** If a TA accidentally commits a `.env` file with their personal email or an API key, deletes it in the next commit, the analyst simply browses to the specific hash of the previous commit to retrieve the data.

## Real-World Attack Scenario

### Uncovering an APT's Infrastructure via a Forgotten Repo

**The Setup:**
A CTI analyst is researching a new, sophisticated backdoor written in Go, attributed to a suspected nation-state actor. Reverse engineering reveals a unique, hardcoded user-agent string: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) APT-Custom-Dropper-v1.2`.

**The Investigation:**
1. The analyst uses this exact string as a GitHub search query: `"APT-Custom-Dropper-v1.2" extension:go`.
2. The search yields a single hit in a repository named `Project-X-Tools` owned by a seemingly random user account `DevOps-Ninja-99`.
3. The repository contains the source code for the backdoor. However, the TA had scrubbed the C2 IP addresses from the current version of the code.
4. The analyst clones the repository locally and reviews the commit history (`git log -p`).
5. Five commits prior, the analyst finds a commit message titled "testing network connectivity." In this commit, the C2 server IP `203.0.113.55` is hardcoded in the source.
6. Furthermore, by inspecting the Git configuration of that specific commit (`git show --format="%an <%ae>"`), the analyst extracts the author's email: `alexey.dev@yandex.ru`, a critical pivot point for SOCMINT attribution.

## Architecture & Investigation Flow Diagram

```text
+-----------------------+
|  Malware Sample       |
|  (Extract Unique      |
|   Strings/Functions)  |
+-----------+-----------+
            |
            | 1. GitHub Advanced Search / Dorking
            v
+-----------------------+       +------------------------+
|  GitHub Platform      |       |   Malicious Repo       |
|  Search: "Unique_Str" |------>|   User: DevOps-Ninja   |
+-----------+-----------+       +-----------+------------+
                                            |
                                            | 2. Clone locally & Analyze Git History
                                            v
                                +------------------------+
                                |  Historical Commit     |
                                |  Hash: a1b2c3d4e5f6    |
                                +-----------+------------+
                                            |
            +-------------------------------+-------------------------------+
            |                                                               |
            v                                                               v
+-----------------------+                                       +-----------------------+
|  Exposed C2 Infra     |                                       |  Author Identity      |
|  Hardcoded IP found   |                                       |  Email extracted from |
|  in old commit.       |                                       |  git config.          |
+-----------------------+                                       +-----------------------+
```

## Tools for Code Repository OSINT

1. **Gitrob / TruffleHog:** Automated tools designed to scan repositories (and their entire commit history) for high-entropy strings, API keys, passwords, and tokens.
2. **Gitleaks:** A fast, reliable SAST tool for detecting hardcoded secrets in git repositories. Often used defensively, but powerful for CTI analysts analyzing TA repos.
3. **Shhgit:** A tool that monitors the public GitHub event stream in real-time to find secrets and sensitive files as soon as they are committed.
4. **GitHub REST API:** Analysts script Python tools to automate the extraction of follower networks, stargazers, and organization structures to map out TA networks.

## Monitoring and Defensive Actions

Organizations must apply these exact same techniques against their own infrastructure to ensure they are not leaking data.
- **Continuous Monitoring:** Implement automated scanning (like GitHub Advanced Security or custom TruffleHog pipelines) on all internal and public corporate repositories to block commits containing secrets.
- **Brand Monitoring:** Search public GitHub for corporate API keys, internal subdomains, or proprietary code snippets to detect insider threats or compromised developer accounts.

## Chaining Opportunities
- **[[07 - Social Media Intelligence SOCMINT on Threat Actors]]** - Taking the email address or username found in a Git commit and pivoting to Twitter, Telegram, or underground forums.
- **[[09 - Tracking Pastebin and Ghostbin Leaks]]** - TAs often host the initial download stager on Pastebin, which then executes a script to pull the main payload from a GitHub repository.
- **[[06 - Tracking Malicious SSL TLS Certificates]]** - Finding `.pem` or `.key` files accidentally committed to a repository, allowing the analyst to fingerprint the TA's encrypted traffic.

## Related Notes
- [[01 - OSINT Fundamentals and Methodology]]
- [[10 - Email OSINT and Data Breach Search HaveIBeenPwned DeHashed]]
- [[12 - Automating OSINT Workflows]]
