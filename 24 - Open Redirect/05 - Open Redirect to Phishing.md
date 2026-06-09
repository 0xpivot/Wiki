---
tags: [vapt, open-redirect, phishing, chaining]
difficulty: beginner
module: "24 - Open Redirect"
topic: "24.05 Open Redirect to Phishing"
---

# 24.05 — Open Redirect to Phishing

## What is it?
By itself, an Open Redirect does not steal data or compromise servers. Its primary danger lies in how it perfectly facilitates **Phishing**. 

When attackers send phishing emails, the biggest hurdle is convincing the victim to click the link. Modern users are trained to hover over links and check the domain. If the link says `https://chase-bank-verify.com`, a cautious user will spot the fake domain. However, if the attacker uses an Open Redirect on the *actual* Chase Bank website, the link looks like `https://chase.com/login?redirect=https://chase-bank-verify.com`. The user sees the legitimate `chase.com` domain, clicks it with full confidence, and is seamlessly redirected to the fake site.

Think of it like a scammer setting up a fake booth inside a legitimate bank's lobby. Because the customer already walked through the real bank's front doors, they implicitly trust everything inside, making them drop their guard entirely.

## ASCII Diagram
```text
[Phishing Email]
"Your account has been locked. Click here to verify:"
Link: https://trusted-bank.com/auth?next=http://evil-bank.com/login
       │
       ▼
[Victim checks the link]
"Ah, it starts with trusted-bank.com. It must be safe!"
       │
[Victim clicks]
       ▼
[trusted-bank.com]
Reads `next` parameter -> Issues HTTP 302 Redirect to evil-bank.com
       │
       ▼
[evil-bank.com]
Displays perfect visual clone of trusted-bank.com
       │
       ▼
[Victim enters credentials] ──> [Attacker steals password!]
```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Identify an Open Redirect vulnerability on a high-reputation, trusted domain (e.g., a bank, a major cloud provider, a popular SaaS app).
  2. Clone the login page of the trusted domain using a tool like GoPhish, Social Engineer Toolkit (SET), or `wget`.
  3. Host the cloned page on a domain you control.
  4. Construct the malicious URL utilizing the trusted domain's Open Redirect pointing to your cloned page.
  5. Distribute the URL via email, SMS (Smishing), or social media.
  6. When users click, they see the trusted domain in the address bar for a split second, then the page loads. Because the page looks identical, they enter their credentials.

- **Actual payloads:**
  **Weaponized Phishing Link:**
  ```text
  https://auth.company.com/login?returnTo=https://auth-company-support.com/login
  ```

## Real-World Example
A classic example occurred with a major government tax portal. The portal had a vulnerability on its logout endpoint: `https://tax.gov/logout?url=...`. Attackers sent millions of SMS messages during tax season stating: "Your tax refund failed. Login to verify: `https://tax.gov/logout?url=https://tax-refund-portal.net`". Users saw `tax.gov`, clicked the link, and were redirected to a perfect clone of the government site that asked for their Social Security Number and banking details. The Open Redirect bypassed the users' natural skepticism.

## Chaining Opportunities
- This vuln + [[24.03 Bypass Techniques]] → Use URL obfuscation to hide the phishing domain in the email link (e.g., `https://trusted.com/login?next=%2f%2fevil.com`).
- This vuln + [[11.01 CSRF (Cross-Site Request Forgery)]] → Redirect the user to a page that automatically submits a hidden CSRF form back to the trusted domain, hijacking their account.

## Related Notes
- [[24.01 What is Open Redirect?]]
- [[24.02 Open Redirect in redirect= and url= Parameters]]
