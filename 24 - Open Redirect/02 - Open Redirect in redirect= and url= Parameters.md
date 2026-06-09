---
tags: [vapt, open-redirect, beginner]
difficulty: beginner
module: "24 - Open Redirect"
topic: "24.02 Open Redirect in redirect= and url= Parameters"
---

# 24.02 — Open Redirect in `redirect=` and `url=` Parameters

## What is it?
The most prevalent location for Open Redirect vulnerabilities is directly within GET query parameters specifically designed for navigation. Developers frequently implement parameters like `redirect=`, `url=`, `next=`, or `returnTo=` to improve the User Experience (UX) across complex application flows, such as single sign-on (SSO), shopping carts, or multi-step wizards.

Because these parameters are explicitly designed to alter the browser's location, they are the primary targets during reconnaissance. 

Think of these parameters as taxi drivers at an airport. They are holding a sign (`redirect=`) waiting to take the passenger to a destination. If the taxi company does not verify the address, an attacker can simply write their own malicious address on the sign.

## ASCII Diagram
```text
[Common App Flow]
1. User clicks "Checkout" on an e-commerce site without being logged in.
   URL: https://shop.com/cart
   
2. Server intercepts, demands login, and saves intended destination.
   Redirects to: https://shop.com/login?next=/cart

3. User logs in. Server reads `next` parameter.
   Redirects to: https://shop.com/cart (User is happy!)

[Attacker Manipulation]
1. Attacker crafts a link.
   URL: https://shop.com/login?next=http://evil.com/fake_checkout

2. Victim clicks link, logs in.

3. Server blindly reads `next` parameter.
   Redirects to: http://evil.com/fake_checkout (Victim is phished!)
```

## How to Find It
- **Manual steps:**
  1. Spider the application thoroughly. Look specifically at:
     - Login and Registration pages (`/login?redirect=...`).
     - Logout endpoints (`/logout?url=...`).
     - Interstitial pages (e.g., "You are leaving our site... click here to continue").
     - Language toggles (`/setLang?lang=en&return_to=...`).
  2. Modify the parameter to point to a reliable external listener (e.g., `http://burpcollaborator.net` or `http://webhook.site`).
  3. If you receive an HTTP ping on your listener, the redirect succeeded.

- **Tool commands with flags explained:**
  Using `gau` (GetAllUrls) and `uro` to hunt for navigation parameters across an entire domain:
  ```bash
  # 1. Fetch all known URLs for a domain
  gau target.com | uro > urls.txt
  
  # 2. Grep for common redirect parameters
  grep -E "(redirect|url|next|return|goto|dest)Url=" urls.txt
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Discover the vulnerable parameter.
  2. Set up a honeypot or payload host (e.g., a server returning an XSS payload, or a fake login page).
  3. Craft the link: `https://target.com/auth?dest=http://attacker.com/payload`.
  4. Monitor network traffic. If the application is an API or uses client-side routing (React/Angular), the parameter might be parsed by JavaScript instead of causing an HTTP 302.
  5. Check if JavaScript executes `window.location.href = new URLSearchParams(window.location.search).get('dest')`. This is DOM-based Open Redirect.

- **Actual payloads:**
  **Common Parameter Names to Fuzz:**
  ```text
  ?redirect=
  ?redirect_uri=
  ?redirect_url=
  ?url=
  ?next=
  ?return=
  ?return_to=
  ?dest=
  ?destination=
  ?goto=
  ?out=
  ?view=
  ```

- **Real HTTP request/response examples:**
  **DOM-Based Redirect Example (JavaScript):**
  *Vulnerable Code:*
  ```javascript
  let params = new URLSearchParams(window.location.search);
  if (params.has('returnUrl')) {
      window.location.replace(params.get('returnUrl'));
  }
  ```
  *Exploit Request:*
  ```http
  GET /dashboard?returnUrl=https://evil.com HTTP/1.1
  Host: target.com
  ```
  *(No 302 response from the server; the browser's JavaScript engine executes the redirect locally).*

## Real-World Example
A bug bounty hunter was testing a video streaming platform. They found that when a user tried to view a premium video without a subscription, they were sent to `https://stream.com/upgrade?url=/video/123`. The hunter changed this to `https://stream.com/upgrade?url=javascript:alert(1)`. The application took the `url` parameter and placed it directly into an `<a href="...">Continue</a>` tag. Because the input wasn't validated as a safe HTTP URL, the hunter achieved XSS via the Open Redirect vector!

## How to Fix It
- **Developer remediation:**
  Validate the parameter strictly. If the application expects a relative path, ensure it starts with `/` and contains alphanumeric characters and valid path symbols only. Reject anything starting with `http://`, `https://`, `//`, `javascript:`, or `data:`.

- **Code snippet:**
  **Python (Flask - Safe Redirect Validation):**
  ```python
  from urllib.parse import urlparse, urljoin
  from flask import request, redirect, url_for

  def is_safe_url(target):
      ref_url = urlparse(request.host_url)
      test_url = urlparse(urljoin(request.host_url, target))
      # Ensure the scheme is HTTP/HTTPS and the network location matches the host exactly
      return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

  @app.route('/login')
  def login():
      next_url = request.args.get('next')
      # Validate the URL before redirecting
      if not is_safe_url(next_url):
          return abort(400)
      return redirect(next_url)
  ```

## Chaining Opportunities
- This vuln + [[07 - XSS / Cross-Site Scripting]] → If the application reflects the redirect URL into an anchor tag (`<a href="URL">`), use `javascript:alert(1)` to achieve Reflected or DOM XSS.
- This vuln + [[24.03 Bypass Techniques (//evil.com, /\evil.com, ///evil.com)]] → Often, developers put basic filters in place (e.g., blocking `http://`). Combine parameter discovery with bypass techniques to defeat these filters.

## Related Notes
- [[24.01 What is Open Redirect?]]
- [[24.03 Bypass Techniques (//evil.com, /\evil.com, ///evil.com)]]
