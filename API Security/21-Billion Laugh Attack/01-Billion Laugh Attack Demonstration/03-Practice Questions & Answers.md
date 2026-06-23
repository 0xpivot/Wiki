---
course: API Security
topic: Billion Laugh Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what a Billion Laughs attack is and how it works.**

A Billion Laughs attack, also known as a quadratic blowup attack, exploits the way XML parsers handle entity references. In this attack, an attacker creates a large number of nested entities in an XML document. When the XML parser tries to resolve these entities, it consumes a significant amount of memory and CPU resources, potentially leading to a denial-of-service (DoS) condition. The name comes from the original proof-of-concept attack which used the text "lol" repeated many times.

**Q2. How would you exploit a system vulnerable to a Billion Laughs attack using an API?**

To exploit a system vulnerable to a Billion Laughs attack via an API, you would craft an XML payload containing deeply nested entities. Here’s an example of such a payload:

```xml
<!DOCTYPE lolz [
  <!ENTITY a "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa">
  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
  <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
  <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;">
  <!ENTITY e "&d;&d;&d;&d;&d;&d;&d;&d;">
  <!ENTITY f "&e;&e;&e;&e;&e;&e;&e;&e;">
]>
<f>
```

This payload defines several entities that reference each other, resulting in exponential expansion when parsed. You would send this payload to the API endpoint that accepts XML input, causing the server to consume excessive resources.

**Q3. Why is converting an API request from JSON to XML necessary to perform a Billion Laughs attack?**

Converting an API request from JSON to XML is necessary because JSON does not support entity references, which are essential for performing a Billion Laughs attack. XML, however, supports entity references, allowing for the creation of deeply nested structures that can be exploited to exhaust server resources. By converting the request to XML, you enable the use of these entity references to carry out the attack.

**Q4. What recent real-world examples or CVEs illustrate the impact of Billion Laughs attacks?**

One notable example is CVE-2019-14546, which affected the Apache Struts framework. This vulnerability allowed attackers to exploit the XML parser used by the framework to execute a Billion Laughs attack. The attack could lead to a denial-of-service condition, making the server unresponsive due to excessive resource consumption. This highlights the importance of securing XML parsers against such attacks.

**Q5. How can an organization protect its systems from Billion Laughs attacks?**

To protect systems from Billion Laughs attacks, organizations can take several measures:

1. **Limit Entity Expansion**: Configure XML parsers to limit the depth and size of entity expansions. This can prevent the exponential growth of data that leads to resource exhaustion.

2. **Use Secure XML Parsers**: Employ XML parsers that are designed to mitigate such attacks, such as those that provide built-in protections against entity expansion attacks.

3. **Input Validation**: Implement strict validation of incoming XML data to ensure it does not contain malicious entity definitions.

4. **Rate Limiting and Throttling**: Apply rate limiting and throttling mechanisms to detect and mitigate unusual traffic patterns that may indicate an ongoing attack.

By implementing these strategies, organizations can significantly reduce their exposure to Billion Laughs attacks and other similar vulnerabilities.

---
<!-- nav -->
[[02-Billion Laugh Attack|Billion Laugh Attack]] | [[API Security/21-Billion Laugh Attack/01-Billion Laugh Attack Demonstration/00-Overview|Overview]]
