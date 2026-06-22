---
course: API Security
topic: Information Disclosure
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is information disclosure in the context of API security?**

Information disclosure in API security refers to vulnerabilities that allow sensitive data to be leaked unintentionally. This can include details about the underlying technology stack, configuration settings, or other internal system information. Such leaks can be exploited to gain insights into the architecture and potentially facilitate further attacks.

**Q2. How can you identify an information disclosure vulnerability through API responses?**

To identify an information disclosure vulnerability through API responses, you should carefully examine the data returned by various API endpoints. Look for unexpected details such as version numbers, server configurations, or internal paths. For example, a response might inadvertently reveal the version of a database being used, which could be critical information for an attacker trying to exploit known vulnerabilities in that specific version.

**Q3. Explain how triggering errors can help in discovering information disclosure vulnerabilities.**

Triggering errors can help in discovering information disclosure vulnerabilities because error messages often contain detailed information about the internal workings of the application. By intentionally causing errors, you may receive responses that expose sensitive data. For instance, a stack trace might reveal file paths, function names, or even parts of the source code, all of which can provide valuable information to an attacker.

**Q4. How can system information retrieval be exploited as an information disclosure vulnerability?**

System information retrieval can be exploited as an information disclosure vulnerability when an API endpoint returns details about the underlying operating system, software versions, or other configuration settings. An attacker can use this information to tailor their attacks more effectively. For example, if an API reveals that a server is running an outdated version of Apache, the attacker can search for known vulnerabilities in that version and attempt to exploit them.

**Q5. Provide a recent real-world example of an information disclosure vulnerability and explain its impact.**

A recent example of an information disclosure vulnerability is CVE-2021-26084, which affected the WordPress REST API. This vulnerability allowed attackers to retrieve sensitive information about users, including usernames and email addresses, by making specific API requests. The impact was significant because this information could be used for targeted phishing attacks or to gain unauthorized access to user accounts. The vulnerability was patched quickly, but it highlights the importance of securing APIs against information disclosure risks.

---
<!-- nav -->
[[API Security/16-Information Disclosure/01-Briefing Information Disclosure/02-Information Disclosure in APIs|Information Disclosure in APIs]] | [[API Security/16-Information Disclosure/01-Briefing Information Disclosure/00-Overview|Overview]]
