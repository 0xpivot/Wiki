---
tags: [vapt, clickjacking, ui, intermediate]
difficulty: intermediate
module: "28 - Clickjacking"
topic: "28.03 Multistep Clickjacking"
---

# 28.03 — Multistep Clickjacking

## What is it?
**Multistep Clickjacking** is an advanced variation of standard Clickjacking required when a target application's sensitive action cannot be performed with a single click. 

Many modern web applications try to protect sensitive actions by adding confirmation dialogues, dropdown menus, or multi-page wizards (e.g., clicking "Delete Account", which spawns a modal popup asking "Are you sure?").

To exploit this, the attacker must design a deceptive, multi-step interaction on their decoy page that perfectly aligns with the sequence of buttons appearing dynamically within the hidden iframe.

Think of it like tricking someone into playing a game of "Simon Says." You tell them, "Press the red button, then press the green button to win!" In reality, the red button opens the bank's transfer menu, and the green button confirms the transfer. The attacker dictates the victim's mouse movements to match the backend workflow.

## ASCII Diagram
```text
================================================================================
                    MULTISTEP CLICKJACKING ILLUSION
================================================================================

[The Decoy Game: "Catch the Dot!"]

[Step 1]
User sees a blue dot. They click it to score a point.
(Hidden underneath is the "Account Settings" dropdown menu).
+-------------------------------------------------+
|                                                 |
|    Score: 0                                     |
|                                                 |
|                  [ ● ]                          | <-- Decoy Click 1
|                                                 |
+-------------------------------------------------+
(The hidden iframe registers the click. A dropdown menu appears inside the iframe).


[Step 2]
The blue dot disappears, and a new red dot appears lower down on the screen.
The user quickly moves their mouse and clicks the red dot.
(Hidden underneath the red dot is the "Delete Account" button that just appeared).
+-------------------------------------------------+
|                                                 |
|    Score: 1                                     |
|                                                 |
|                                                 |
|                               [ ● ]             | <-- Decoy Click 2
+-------------------------------------------------+

[Result]
The user thinks they scored 2 points in a game.
The application registers: Click(Settings) -> Click(Delete).
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Find a sensitive action that lacks `X-Frame-Options` but requires multiple clicks (e.g., clicking a shopping cart icon, then clicking "Checkout").
  2. Embed the page in a local iframe with `opacity: 0.5`.
  3. Manually trace the coordinates of every click required to complete the action.
  4. Design a decoy game or questionnaire that naturally leads the user's cursor to click exactly on those coordinates in the correct sequence.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Determine the exact pixel coordinates of Button 1 and Button 2 in the target iframe.
  2. Create a decoy HTML page with Javascript.
  3. Display Decoy Button 1 exactly over Target Button 1.
  4. Write a Javascript `onclick` event for Decoy Button 1 that immediately hides it and reveals Decoy Button 2.
  5. Position Decoy Button 2 exactly over Target Button 2.
  6. When the victim clicks Decoy Button 1, the iframe registers the click and updates its DOM. Simultaneously, the Javascript updates the decoy UI. 
  7. When the victim clicks Decoy Button 2, the iframe registers the confirmation click.

- **Actual payloads:**
  **A basic 2-step decoy script:**
  ```html
  <style>
      iframe { position: absolute; top: 0; left: 0; opacity: 0.001; z-index: 2; width: 800px; height: 600px;}
      .btn { position: absolute; z-index: 1; padding: 20px; cursor: pointer; }
      #decoy1 { top: 100px; left: 200px; background: blue; }
      #decoy2 { top: 300px; left: 400px; background: red; display: none; }
  </style>

  <iframe src="https://vulnerable.com/settings"></iframe>

  <!-- Step 1 -->
  <div id="decoy1" class="btn" onclick="nextStep()">Click me to start!</div>
  
  <!-- Step 2 -->
  <div id="decoy2" class="btn">Click me to win!</div>

  <script>
      function nextStep() {
          // Hide button 1, show button 2
          document.getElementById('decoy1').style.display = 'none';
          document.getElementById('decoy2').style.display = 'block';
      }
  </script>
  ```

## Real-World Example
An attacker targeted an e-commerce site to force users to buy a specific expensive product. The checkout flow required three clicks: "Add to Cart", "Go to Cart", and "Confirm Purchase". The attacker built a "Personality Test" quiz on their own domain. 
- Click 1: "Are you an introvert or an extrovert?" (Hidden: Add to Cart)
- Click 2: "Do you prefer cats or dogs?" (Hidden: Go to Cart)
- Click 3: "Click here to see your results!" (Hidden: Confirm Purchase)
By mapping the quiz buttons to the checkout flow, the attacker forced authenticated victims to unknowingly purchase items.

## How to Fix It
- **Developer remediation:**
  Multistep workflows do not protect against Clickjacking. The only robust defense is preventing the page from being framed in the first place using `Content-Security-Policy: frame-ancestors 'none'` or `SameSite` cookies.

## Chaining Opportunities
- This vuln + DOM manipulation → Useful when the target iframe dynamically changes size or layout after the first click.

## Related Notes
- [[02 - Basic iframe Clickjacking]]
- [[04 - Drag and Drop Clickjacking]]
