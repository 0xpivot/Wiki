---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a low-level logic flaw in web applications.**

A low-level logic flaw refers to a vulnerability that arises due to incorrect or insufficient validation of user inputs or internal logic processes. These flaws often occur when the application fails to properly handle edge cases or unexpected inputs, leading to unintended behavior. For example, in the lab described, the application failed to validate the quantity of items added to the cart, allowing an attacker to manipulate the purchase process to buy items for an unintended price.

**Q2. How would you exploit a low-level logic flaw in a purchasing workflow similar to the one described in the lab?**

To exploit a low-level logic flaw in a purchasing workflow, follow these steps:

1. Identify the parameters that are not properly validated, such as the quantity of items.
2. Use tools like Burp Suite to intercept and modify HTTP requests.
3. Test the application with various input values to determine the limits of validation.
4. Exploit the lack of validation by sending large numbers of items to the cart.
5. Monitor the application's response to identify any unusual behavior, such as negative numbers or overflow conditions.
6. Calculate the necessary quantities to achieve a desired outcome, such as reducing the total cost to within available store credit.
7. Combine different items to adjust the total cost to a manageable positive value.
8. Place the order once the total cost is within the acceptable range.

For instance, in the lab, the application accepted a quantity of 99 but rejected 100. By repeatedly adding 99 jackets, the total cost eventually became negative. Further calculations allowed the attacker to reduce the total cost to within the available store credit.

**Q3. Why is it important to validate user inputs in web applications, especially in financial transactions?**

Validating user inputs is crucial in web applications, particularly in financial transactions, to prevent various types of attacks and ensure the integrity of the system. Here are several reasons why input validation is essential:

1. **Prevent Financial Losses**: Incorrect or malicious inputs can lead to unauthorized transactions, resulting in financial losses for the company or customers.
2. **Maintain Data Integrity**: Proper validation ensures that data stored in the database remains accurate and consistent, preventing issues like data corruption.
3. **Avoid Logical Flaws**: Insufficient validation can expose logical flaws in the application, allowing attackers to manipulate workflows and achieve unintended outcomes.
4. **Enhance Security**: Validated inputs help mitigate common security threats such as SQL injection, cross-site scripting (XSS), and buffer overflows.

For example, in the lab, the lack of proper validation on the quantity parameter allowed an attacker to manipulate the purchasing workflow, leading to a significant reduction in the total cost of the transaction.

**Q4. How can you configure Burp Suite to effectively test for low-level logic flaws in a web application?**

To effectively test for low-level logic flaws using Burp Suite, follow these steps:

1. **Intercept Requests**: Use the Proxy tool to intercept HTTP requests and responses.
2. **Modify Parameters**: Use the Repeater tool to modify specific parameters, such as the quantity of items in a shopping cart.
3. **Use Intruder**: Utilize the Intruder tool to automate the testing of various input values. Configure Intruder to send a large number of requests with different payloads.
4. **Monitor Responses**: Observe the application’s responses to identify any unusual behavior, such as error messages, unexpected results, or changes in the application state.
5. **Resource Pool Management**: Set up a resource pool to control the rate of requests and avoid overwhelming the server, which can help in identifying subtle issues.

For instance, in the lab, the Intruder tool was used to repeatedly add 99 jackets to the cart, eventually causing the total cost to become negative due to the lack of proper validation.

**Q5. Explain how recent real-world examples, such as CVEs or breaches, illustrate the importance of addressing low-level logic flaws.**

Recent real-world examples highlight the critical nature of addressing low-level logic flaws in web applications. For instance:

- **CVE-2021-21972**: This vulnerability in the Microsoft Exchange Server allowed attackers to bypass authentication and execute arbitrary commands. The flaw arose due to improper validation of certain parameters, illustrating the importance of robust input validation to prevent unauthorized access and command execution.
- **Equifax Breach (2017)**: The breach involved a vulnerability in Apache Struts, where improper validation of user inputs led to remote code execution. This incident underscores the need for thorough validation to prevent attackers from exploiting logical flaws to gain unauthorized access to sensitive information.

These examples demonstrate that low-level logic flaws can have severe consequences, including data breaches, financial losses, and reputational damage. Addressing these flaws through rigorous input validation and comprehensive testing is essential to maintaining the security and integrity of web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/06-Lab 5 Low level logic flaw/04-Understanding the Lab Environment|Understanding the Lab Environment]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/06-Lab 5 Low level logic flaw/00-Overview|Overview]]
