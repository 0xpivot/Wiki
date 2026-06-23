---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what an information disclosure vulnerability is and provide an example.**

An information disclosure vulnerability occurs when a website unintentionally reveals sensitive information to its users. This information could include data about other users, personally identifiable information (PII), sensitive commercial or business data, or technical details about the website and its infrastructure. An example of an information disclosure vulnerability is having stack traces enabled in a production environment, which can reveal the frameworks and libraries used by the application. For instance, if a malformed string is entered in an input parameter field, it could output a stack trace revealing the use of the Faster XML Jackson Databind Library, which might be vulnerable to deserialization attacks leading to remote code execution.

**Q2. How can improper error and exception handling contribute to information disclosure vulnerabilities?**

Improper error and exception handling can contribute to information disclosure vulnerabilities by exposing detailed error messages that reveal internal system configurations or technologies used. For example, if stack traces are enabled in a production environment, an attacker can generate error messages that expose the frameworks and libraries used by the application. This information can help attackers tailor their attacks to exploit specific vulnerabilities associated with those technologies. Additionally, verbose error messages can reveal sensitive information such as database errors that disclose table names or query structures.

**Q3. Why is it important to use HTTPS instead of HTTP for transmitting sensitive information?**

Using HTTPS instead of HTTP is crucial for transmitting sensitive information because HTTPS encrypts the data exchanged between the client and the server, ensuring that it cannot be intercepted and read by unauthorized parties. With HTTP, the data is transmitted in plain text, making it vulnerable to interception by anyone on the same network. For example, if a user logs into an application over HTTP, their email address and password can be intercepted and read in clear text using tools like Wireshark. In contrast, HTTPS ensures that the data is encrypted, making it unreadable to anyone who intercepts it.

**Q4. How can storing user credentials in clear text pose a significant risk in the event of a data breach?**

Storing user credentials in clear text poses a significant risk in the event of a data breach because it allows anyone who gains access to the database to immediately read and use the credentials. This includes administrators, software developers, and attackers who might exploit a data breach. If credentials are stored in clear text, an attacker can simply read the credentials and use them to log into the application, potentially gaining access to sensitive information or performing unauthorized actions. Hashing passwords mitigates this risk by making it computationally infeasible for an attacker to reverse-engineer the clear text passwords from the hashes.

**Q5. Describe how the lack of salting in password hashing can lead to information disclosure vulnerabilities.**

The lack of salting in password hashing can lead to information disclosure vulnerabilities because it allows attackers to use precomputed hash tables (rainbow tables) to quickly find the corresponding plaintext passwords. Without salting, the same password will always produce the same hash, enabling attackers to create a table of hashes for common passwords. If a data breach occurs and the hashes are exposed, attackers can compare the hashes against their precomputed tables to find matches. Salting adds a unique random string to each password before hashing, ensuring that the same password produces different hashes each time. This significantly increases the time and computational effort required to crack the hashes, thereby reducing the risk of information disclosure.

**Q6. How can improper error messages contribute to information disclosure vulnerabilities?**

Improper error messages can contribute to information disclosure vulnerabilities by providing attackers with specific information about the application’s internal workings. For example, if a login page provides different error messages for incorrect usernames and incorrect passwords, an attacker can use this information to enumerate valid usernames in the application. Similarly, verbose error messages can reveal details about the backend technologies, such as the version of the web server or framework being used. To mitigate this risk, applications should use generic error messages that do not leak sensitive information about the backend system.

**Q7. What are some methods to prevent information disclosure vulnerabilities in web applications?**

To prevent information disclosure vulnerabilities in web applications, several methods can be employed:

1. **Awareness:** Ensure that all teams involved in developing the application are aware of what information is considered sensitive.
2. **Code Audits:** Regularly audit the code for potential information disclosure vulnerabilities as part of the QA or build processes.
3. **Generic Error Messages:** Use generic error messages that do not leak sensitive information about the backend technologies or data.
4. **Disable Debugging Features:** Ensure that any debugging or diagnostic features are disabled in the production environment.
5. **Review Third-Party Configurations:** Review all configuration settings for any third-party technologies used and disable any unnecessary features or settings.

By implementing these measures, developers can significantly reduce the risk of information disclosure vulnerabilities in their web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/25-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]]
