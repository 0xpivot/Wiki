---
course: API Security
topic: File Path Traversal
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is a file path traversal vulnerability in the context of APIs?**

A file path traversal vulnerability occurs when an application uses untrusted input to construct a file path without proper validation. This allows attackers to manipulate the file path to access arbitrary files on the server, potentially leading to unauthorized access to sensitive information such as configuration files, passwords, and other critical data.

**Q2. How can an attacker exploit a file path traversal vulnerability in an API?**

An attacker can exploit a file path traversal vulnerability by manipulating parameters that are used to construct file paths. For instance, by injecting `../` sequences into the input, an attacker can navigate outside the intended directory and access sensitive files. The attacker might attempt to read or write files in directories like `/etc/passwd`, which contains user account information, or other critical system files.

**Q3. Explain how to mitigate file path traversal vulnerabilities in an API.**

To mitigate file path traversal vulnerabilities, developers should:

1. **Validate Input**: Ensure that all user-supplied input is validated against a strict set of rules. Only allow characters that are expected and necessary for the operation.
   
2. **Use Whitelisting**: Implement a whitelist of allowed directories and filenames. Any input that does not match the whitelist should be rejected.
   
3. **Canonicalize Paths**: Before using the input to construct a file path, canonicalize the path to remove any `../` sequences or other path manipulations. This ensures that the path points to a location within the intended directory.
   
4. **Least Privilege Principle**: Run the application with the least privileges necessary to perform its tasks. This limits the damage that can be caused if a vulnerability is exploited.

**Q4. Provide an example of a recent real-world breach related to file path traversal vulnerabilities.**

One notable example is the 2019 breach of the popular open-source project Apache Struts. A vulnerability (CVE-2017-5638) was exploited, allowing attackers to execute arbitrary commands on the server through a file path traversal attack. This vulnerability was due to improper handling of user input in file paths, leading to remote code execution. Organizations that did not patch their systems were vulnerable to attacks that could result in full system compromise.

**Q5. How would you test for file path traversal vulnerabilities in an API?**

To test for file path traversal vulnerabilities, you can use the following methods:

1. **Manual Testing**: Try appending `../` sequences to parameters that are used to construct file paths. Check if the application allows you to access files outside the intended directory.

2. **Automated Tools**: Use automated tools like Burp Suite, OWASP ZAP, or Metasploit to scan for file path traversal vulnerabilities. These tools can automatically inject payloads and detect if the application is vulnerable.

3. **Penetration Testing**: Conduct a penetration test where you simulate an attacker's behavior to identify potential vulnerabilities. This includes attempting to read sensitive files or write to unexpected locations.

By combining these methods, you can effectively test for file path traversal vulnerabilities and ensure your API is secure.

---
<!-- nav -->
[[API Security/15-File Path Traversal/01-Background Concept API Perspective/02-File Path Traversal|File Path Traversal]] | [[API Security/15-File Path Traversal/01-Background Concept API Perspective/00-Overview|Overview]]
