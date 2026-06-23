---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why version control history can lead to information disclosure vulnerabilities.**

Version control systems such as Git store the complete history of changes made to a project, including every commit, branch, and merge. If sensitive information, such as passwords or API keys, were committed to the repository at any point in time, even if subsequently removed, that information remains in the history. An attacker who gains access to the version control history can use tools to recover this sensitive data, leading to potential security breaches.

**Q2. How would you exploit version control history to retrieve sensitive information?**

To exploit version control history, an attacker would follow these steps:

1. Identify a version control endpoint or repository accessible through the application.
2. Clone or download the version control history using tools like `git clone` or `wget`.
3. Use version control tools such as `git log`, `git show`, or `gitk` to browse through the commit history.
4. Search for sensitive information such as passwords, API keys, or configuration settings that might have been committed and later removed.
5. Once the sensitive information is found, the attacker can use it to gain unauthorized access to the system.

For example, if an attacker finds a commit where an admin password was removed, they can revert to that commit to retrieve the password.

**Q3. Why is it important to clean up version control history before making it public?**

Cleaning up version control history is crucial before making it public to prevent the exposure of sensitive information. Even if sensitive data has been removed in recent commits, older commits may still contain this data. If the repository is made public, anyone can access the full history and extract the sensitive information. This can lead to security breaches, unauthorized access, and other serious consequences.

To clean up the history, developers should use tools like `git filter-branch` or `BFG Repo-Cleaner` to remove sensitive data from all commits. Additionally, they should ensure that sensitive information is never committed in the first place by using `.gitignore` files and environment variables.

**Q4. How would you configure a version control system to prevent accidental disclosure of sensitive information?**

To prevent accidental disclosure of sensitive information in a version control system, you can take the following steps:

1. **Use `.gitignore` Files**: Add files containing sensitive information to the `.gitignore` file to prevent them from being tracked by Git.
   
   ```plaintext
   # Example .gitignore file
   *.log
   *.tmp
   config/*.json
   ```

2. **Environment Variables**: Store sensitive information such as API keys, passwords, and database credentials in environment variables rather than hardcoding them into the source code.

3. **Pre-commit Hooks**: Implement pre-commit hooks to check for sensitive information in the code before committing. For example, you can use a tool like `git-secrets` to scan for patterns that match sensitive information.

4. **Regular Audits**: Regularly audit the version control history to identify and remove any sensitive information that may have been accidentally committed.

5. **Access Controls**: Restrict access to the version control repository to only those who need it. Use role-based access controls to limit permissions.

6. **Educate Developers**: Educate developers about the risks of committing sensitive information and the importance of securing their development environments.

**Q5. What recent real-world examples demonstrate the risk of information disclosure through version control history?**

One notable example is the breach involving Tesla's Autopilot code. In 2019, Tesla's internal version control system was compromised, and attackers gained access to sensitive code related to the Autopilot feature. Although the exact details of how the breach occurred were not fully disclosed, it highlights the importance of securing version control systems and cleaning up sensitive information from the history.

Another example is the exposure of AWS credentials in a GitHub repository. In 2019, a developer accidentally committed AWS credentials to a public GitHub repository. The credentials were later used to launch a crypto-mining attack, resulting in significant financial losses for the affected organizations.

These incidents underscore the importance of maintaining strict controls over version control systems and ensuring that sensitive information is not inadvertently committed to the repository.

---
<!-- nav -->
[[02-Information Disclosure in Version Control History|Information Disclosure in Version Control History]] | [[Web Security (PortSwigger)/17-Information Disclosure/06-Lab 5 Information disclosure in version control history/00-Overview|Overview]]
