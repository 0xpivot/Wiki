---
tags: [vapt, clickjacking, ui, beginner]
difficulty: beginner
module: "28 - Clickjacking"
topic: "28.01 What is Clickjacking?"
---

# 28.01 — What is Clickjacking?

## What is it?
**Clickjacking** (also known as UI Redressing) is a client-side attack that tricks a user into clicking on something different from what they perceive they are clicking on. 

This is achieved by using transparent or opaque layers (usually via HTML `<iframe>` tags and CSS positioning) to place a hidden, malicious webpage exactly over the top of a visible, harmless webpage.

When the user thinks they are clicking a button on the harmless webpage (e.g., "Win a free iPad!"), they are actually clicking a hidden button on the malicious webpage (e.g., "Transfer $1,000" or "Delete My Account"). Because the hidden page is loaded in an iframe, the browser automatically sends the victim's session cookies along with the request, executing the action perfectly authenticated.

Think of it like putting a transparent sheet of glass over an ATM keypad. On the glass, you paint the words "Enter your favorite number here to win a prize." You align this painted message perfectly over the ATM's "Enter PIN" buttons. When the victim presses the buttons on the glass, the physical keys underneath are pressed, and you steal their PIN.

## ASCII Diagram
```text
================================================================================
                    THE CLICKJACKING ILLUSION
================================================================================

[Layer 1: The Attacker's Fake UI (Visible)]
z-index: 1 (Background)
opacity: 1.0 (Fully Visible)

+-------------------------------------------------+
|                                                 |
|    CONGRATULATIONS! YOU ARE THE 1,000,000th     |
|    VISITOR! CLICK HERE TO CLAIM YOUR PRIZE!     |
|                                                 |
|               [ CLAIM PRIZE ]                   |  <-- User aims for this
|                                                 |
+-------------------------------------------------+

                                     ▲
                                     │ (Stacked perfectly on top)
                                     │

[Layer 2: The Target Application iframe (Hidden)]
z-index: 2 (Foreground, sitting ON TOP of Layer 1)
opacity: 0.0 (Completely Invisible!)

+-------------------------------------------------+
|  BANKING APPLICATION                            |
|  Current Balance: $500.00                       |
|                                                 |
|  Send all money to Attacker?                    |
|                                                 |
|               [ CONFIRM TRANSFER ]              |  <-- User actually clicks this!
|                                                 |
+-------------------------------------------------+

[Result]
The browser registers the click on the invisible [CONFIRM TRANSFER] button.
The bank processes the request using the victim's active session cookie.
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Identify a state-changing action on the target application (e.g., deleting an account, changing a password, liking a post, granting OAuth permissions).
  2. Verify if the target application can be loaded inside an `<iframe>`.
  3. Create a simple HTML file on your local machine:
     ```html
     <html>
       <body>
         <iframe src="https://target.com/account/settings"></iframe>
       </body>
     </html>
     ```
  4. Open this local file in your browser. If the target website loads inside the iframe, the application is technically vulnerable to Clickjacking.
  5. Check the HTTP response headers of the target site. Look for `X-Frame-Options` or `Content-Security-Policy: frame-ancestors`. If neither is present (or they are misconfigured), the site is vulnerable.

## How to Exploit It
- **Step-by-step walkthrough:**
  (Detailed exploitation is covered in [[02 - Basic iframe Clickjacking]]). The core premise is:
  1. Find a target page without framing protections.
  2. Write an attacker HTML page containing the target page in an iframe.
  3. Use CSS (`position: absolute; top: Xpx; left: Ypx; opacity: 0.0`) to position the target iframe's critical button perfectly under a decoy button on your attacker page.
  4. Host the attacker page and send the link to an authenticated victim.

## Real-World Example
One of the most famous early examples of Clickjacking was the Twitter "Don't Click" worm. An attacker created a page with a giant button that said "Don't Click". Hidden invisibly over that button was a Twitter iframe positioned perfectly over the "Tweet" button. The iframe was pre-populated with a status update: "Click here: [link to the attacker's page]". When a logged-in Twitter user clicked the attacker's button, they unknowingly tweeted out the link. Their followers saw the tweet, clicked the link, and fell victim to the exact same trap, causing the worm to spread virally across Twitter in minutes.

## How to Fix It
- **Developer remediation:**
  1. **Content-Security-Policy (CSP):** Implement the `frame-ancestors` directive in the CSP header. To completely block framing: `Content-Security-Policy: frame-ancestors 'none';`. To allow framing only by your own domain: `Content-Security-Policy: frame-ancestors 'self';`.
  2. **X-Frame-Options (Legacy):** For older browsers, implement `X-Frame-Options: DENY` or `X-Frame-Options: SAMEORIGIN`.
  3. **SameSite Cookies:** Set session cookies to `SameSite=Lax` or `SameSite=Strict`. This prevents the browser from sending the user's session cookie when the site is loaded inside a third-party iframe, neutralizing the impact of Clickjacking even if framing is possible.

## Chaining Opportunities
- This vuln + [[01 - What is CSRF?]] → If a site has anti-CSRF tokens, you can't force the browser to make the request via script. However, you *can* use Clickjacking to make the user manually click the button containing the valid CSRF token, completely bypassing CSRF protections.
- This vuln + [[04 - Drag and Drop Clickjacking]] → Stealing sensitive data by tricking the user into dragging it out of the hidden iframe.

## Related Notes
- [[02 - Basic iframe Clickjacking]]
- [[06 - Defense — X-Frame-Options, CSP frame-ancestors]]
