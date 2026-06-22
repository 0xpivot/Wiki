---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Lab Setup and Overview

In this lab, we will explore an SSRF vulnerability with a blacklist-based input filter. The lab is hosted on the PortSwigger Web Security Academy, a platform designed to teach web security concepts through practical exercises.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path for Server-Side Request Forgery.
6. Choose the third lab titled "SSRF with blacklist-based input filter."

### Lab Objective

The objective of this lab is to exploit an SSRF vulnerability to access the admin interface and delete the user "Carlos." The application has a stock check feature that fetches data from an internal system. The developer has implemented two weak anti-SSRF defenses that you will need to bypass.

### Vulnerable Feature

The vulnerable feature is the stock check functionality. The goal is to change the stock check URL to access the admin interface, which is available on `http://localhost/admin`, and then delete the user "Carlos."

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/01-Introduction to Server-Side Request Forgery (SSRF)|Introduction to Server-Side Request Forgery (SSRF)]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/00-Overview|Overview]] | [[03-Blacklist-Based Input Filtering|Blacklist-Based Input Filtering]]
