---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities are a class of security issues that arise due to flaws in the application's business rules or processes. These vulnerabilities often stem from incorrect assumptions about user behavior or incomplete validation of input data. Unlike traditional vulnerabilities such as SQL injection or cross-site scripting (XSS), business logic vulnerabilities are more subtle and harder to detect because they rely on the correct functioning of the application's core logic.

### What Are Business Logic Vulnerabilities?

Business logic vulnerabilities occur when an attacker manipulates the application's business rules to achieve unintended outcomes. These vulnerabilities can result in financial losses, data breaches, or other severe consequences. The key aspect of these vulnerabilities is that they exploit the application's intended functionality rather than a specific coding error.

#### Why Do They Matter?

Business logic vulnerabilities matter because they can have significant real-world impacts. For instance, an attacker might exploit a flaw in an e-commerce site's purchase process to obtain goods without paying. Such vulnerabilities can also lead to unauthorized access to sensitive information or manipulation of critical business processes.

### How Do They Work Under the Hood?

To understand how business logic vulnerabilities work, consider the following scenario: An e-commerce site allows users to apply discount codes during checkout. If the application does not properly validate the discount code or the user's eligibility, an attacker could potentially apply a large discount to their purchases, resulting in financial loss for the business.

#### Example Scenario: Infinite Money Logic Flaw

In the context of the "Infinite Money Logic Flaw" lab, the application has a flaw in its purchasing workflow. Specifically, the application does not correctly validate the payment process, allowing an attacker to purchase items without making a valid payment. This flaw can be exploited to obtain goods without paying, leading to financial losses for the business.

### Real-World Examples

Recent real-world examples of business logic vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the Shopify platform allowed attackers to manipulate the checkout process and obtain goods without paying. This flaw was due to improper validation of the payment process.
- **CVE-2020-14774**: A vulnerability in the WooCommerce plugin for WordPress allowed attackers to bypass the payment process and obtain goods without paying. This flaw was due to improper validation of the payment status.

These examples highlight the importance of thorough validation and proper implementation of business logic in applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/00-Overview|Overview]] | [[02-Business Logic Vulnerabilities Infinite Money Logic Flaw|Business Logic Vulnerabilities Infinite Money Logic Flaw]]
