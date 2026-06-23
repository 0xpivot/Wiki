---
course: API Security
topic: Billion Laugh Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what a Billion Laughs attack is and how it works.**

A Billion Laughs attack, also known as a Quine attack, is a type of Denial of Service (DoS) attack that exploits the XML entity expansion feature. It works by creating a recursive XML entity that expands exponentially, consuming significant amounts of memory and CPU resources on the server. For example, the initial entity might be defined as `<!ENTITY lol "lol">`, and subsequent entities recursively expand this definition, such as `<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">`. This recursive expansion can quickly grow to enormous sizes, leading to resource exhaustion and potentially crashing the server.

**Q2. How can you identify if an application is vulnerable to a Billion Laughs attack?**

To identify if an application is vulnerable to a Billion Laughs attack, you need to check if the application processes XML input and if it allows entity expansion without proper restrictions. You can test this by sending a crafted XML payload that includes recursive entity definitions. If the server consumes excessive resources or crashes, it indicates a vulnerability. Additionally, you should verify the content type of the request, ensuring it is set to `application/xml` or another XML-compatible type.

**Q3. What measures can be taken to prevent Billion Laughs attacks?**

To prevent Billion Laughs attacks, several measures can be implemented:

1. **Disable Entity Expansion**: Ensure that the XML parser used by the application does not allow entity expansion. Most modern parsers provide options to disable this feature.
   
2. **Limit Entity Expansion Depth**: If disabling entity expansion is not possible, limit the depth of entity expansion to a reasonable level. This prevents exponential growth from occurring.

3. **Set Maximum Entity Size**: Configure the XML parser to enforce a maximum entity size. This helps prevent large entity expansions from consuming excessive resources.

4. **Input Validation**: Validate all incoming XML data to ensure it does not contain malicious entity definitions. Use regular expressions or other validation techniques to filter out suspicious patterns.

5. **Use Secure Libraries**: Utilize secure XML parsing libraries that are designed to handle such attacks. Libraries like `Defuse` for PHP or `XMLSecurity` for Java offer enhanced security features.

**Q4. How would you exploit a Billion Laughs vulnerability in a REST API?**

To exploit a Billion Laughs vulnerability in a REST API, follow these steps:

1. **Identify the Endpoint**: Determine which endpoint processes XML input. This could be a POST or GET request that accepts XML data.

2. **Craft the Payload**: Create an XML payload with recursive entity definitions. For example:
   ```xml
   <!DOCTYPE lolz [
     <!ENTITY lol "lol">
     <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
     <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
     ...
     <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
   ]>
   <root>&lol9;</root>
   ```

3. **Send the Request**: Send the crafted XML payload to the identified endpoint using a tool like Postman or curl. Set the `Content-Type` header to `application/xml`.

4. **Monitor the Response**: Observe the server’s response. If the server crashes or becomes unresponsive, the attack was successful.

**Q5. Reference a recent real-world example of a Billion Laughs attack and explain how it occurred.**

One notable example of a Billion Laughs attack occurred in 2017 with the Apache Struts framework. A vulnerability (CVE-2017-5638) allowed attackers to exploit a flaw in the Jakarta Multipart parser, which did not properly restrict entity expansion in XML payloads. This led to a series of high-profile breaches, including the Equifax data breach, where attackers exploited this vulnerability to gain unauthorized access to sensitive data.

In this case, the attackers sent specially crafted XML payloads to the vulnerable Struts application, causing the server to expand entities recursively and consume vast amounts of memory and CPU resources. This resulted in a denial of service condition, allowing the attackers to bypass security controls and access internal systems.

To prevent such attacks, organizations should keep their software up-to-date with the latest security patches and implement the preventive measures mentioned earlier.

---
<!-- nav -->
[[03-Billion Laugh Attack Understanding and Mitigating XML External Entity (XXE) Vulnerabilities|Billion Laugh Attack Understanding and Mitigating XML External Entity (XXE) Vulnerabilities]] | [[API Security/21-Billion Laugh Attack/02-Billion Laugh Attack Refer XXE Expansion/00-Overview|Overview]]
