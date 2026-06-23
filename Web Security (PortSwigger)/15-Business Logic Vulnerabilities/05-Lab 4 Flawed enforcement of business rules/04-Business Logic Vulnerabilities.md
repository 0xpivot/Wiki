---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Business Logic Vulnerabilities

### Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when an application fails to enforce the intended business rules correctly. These vulnerabilities can lead to significant financial losses, data breaches, and other severe consequences. In this section, we will explore a specific scenario involving flawed enforcement of business rules, using a practical example to illustrate the concepts.

### Scenario Overview

In the given scenario, we are examining a web application that sells products online. The application has a feature that allows users to apply coupons to their purchases. However, there is a flaw in the way the application enforces the business rules related to the use of coupons and the available store credit.

#### Key Components

- **Lightweight Leather Jacket**: A product priced at $1,337.
- **User Store Credit**: The user has only $100 in store credit.
- **Coupon Functionality**: A new customer coupon that provides either $5 or 5% off the cost of the jacket.

### Step-by-Step Analysis

#### Step 1: Adding the Product to Cart

First, we navigate to the product page and add the lightweight leather jacket to the cart. The jacket costs $1,337, which is more than the user's available store credit of $100.

```markdown

---
<!-- nav -->
[[03-Applying the Coupon|Applying the Coupon]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/05-Lab 4 Flawed enforcement of business rules/00-Overview|Overview]] | [[05-Placing the Order|Placing the Order]]
