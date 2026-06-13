---
tags: [vapt, business-logic, api, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.15 Hidden API Parameters"
---

# 25.15 — Hidden API Parameters

## What is it?
Also known as **Mass Assignment** or **Auto-Binding** vulnerabilities, **Hidden API Parameters** occur when a framework automatically maps client-provided HTTP request data directly into internal object variables or database columns without explicitly restricting which fields the user is allowed to modify.

If an attacker guesses (or discovers) the name of an administrative or internal parameter that the UI doesn't normally send, they can manually inject it into their HTTP request. Because the framework auto-binds all provided parameters to the object, the internal state is updated.

Think of it like filling out a job application form. The paper form only has lines for "Name" and "Phone Number." However, you notice there's blank space at the bottom. You draw a new line, write "Starting Salary: $1,000,000," and hand it to the HR robot. Because the robot is programmed to read *everything* written on the paper and enter it into the database, you get the job with a million-dollar salary. The developer assumed you would only fill out the provided lines.

## ASCII Diagram
```text
================================================================================
                        THE MASS ASSIGNMENT FLAW
================================================================================

[Normal User Profile Update via Browser UI]
POST /api/user/update
{
  "email": "user@gmail.com",
  "bio": "I love hacking!"
}

[Backend Logic (Vulnerable Auto-Binding)]
UserObject.update(request.json)   <-- IT UPDATES EVERY KEY PROVIDED!

[The Exploit]
Attacker guesses internal database column names.
POST /api/user/update
{
  "email": "user@gmail.com",
  "bio": "I love hacking!",
  "is_admin": true,             <-- INJECTED!
  "account_balance": 99999.99,  <-- INJECTED!
  "plan_tier": "enterprise"     <-- INJECTED!
}

[Result]
The UserObject blindly accepts the new keys. The attacker is now a wealthy Admin!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. **Identify Object Creation/Updates:** Find endpoints where you create or update an object (e.g., registering an account, editing a profile, creating a project).
  2. **Information Gathering:** You need to know what the hidden parameters might be called.
     - Look at `GET` requests. If `GET /api/user` returns `{"username":"bob", "is_admin":false, "verified":false}`, you now know the exact names of two highly sensitive parameters.
     - Look at the client-side JavaScript. Sometimes the frontend code contains models or interfaces that define the entire object, even the fields the UI doesn't display.
  3. **The Injection Test:** Intercept the `PUT` or `POST` request. Add the discovered parameters to the JSON payload (or form-data).
     - e.g., `{"username":"bob", "is_admin":true}`
  4. **Verify the State:** Send a `GET` request again. Did `"is_admin":false` change to `true`? If yes, the endpoint is vulnerable to Mass Assignment.
  5. **Fuzzing (Guessing):** If you can't see the `GET` response, use Burp Intruder to inject common parameters: `admin`, `is_admin`, `role`, `tier`, `status`, `verified`.

- **Tool commands with flags explained:**
  Using `Arjun` to find hidden HTTP parameters (often used for GET/POST parameter discovery):
  ```bash
  # -u URL, -m HTTP Method
  arjun -u https://api.target.com/user/update -m POST
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a ticketing system.
  1. You create a support ticket: `POST /api/tickets {"subject": "Help", "body": "My screen is blank."}`.
  2. You view your ticket: `GET /api/tickets/12`. The response is:
     `{"id": 12, "subject": "Help", "body": "...", "status": "open", "assigned_to": null}`.
  3. You want your ticket resolved immediately. You notice the `status` and `assigned_to` fields.
  4. You intercept the update request: `PUT /api/tickets/12 {"body": "Update: It works now."}`.
  5. You inject the hidden parameters: `PUT /api/tickets/12 {"body": "Fixed.", "status": "resolved", "assigned_to": "CEO"}`.
  6. The ticket system accepts the input, resolving the ticket and assigning it to the CEO.

- **Actual payloads:**
  **JSON Payload Injection:**
  ```json
  {
    "name": "John Doe",
    "email": "john@doe.com",
    "role_id": 1, 
    "permissions": ["all"]
  }
  ```
  **HTTP Parameter Pollution (Form Data):**
  ```http
  POST /register HTTP/1.1
  
  username=john&password=123&is_admin=1
  ```

## Real-World Example
A classic Mass Assignment vulnerability occurred in GitHub (reported by Egor Homakov). GitHub's Ruby on Rails backend used auto-binding for the `Commit` object. When a user submitted a public key to a repository, the `POST` request included parameters like `title` and `key`. The attacker discovered that by injecting the `public_key[user_id]` parameter and setting it to the ID of another organization, Rails would automatically bind the attacker's public key to the target organization's account. This allowed the attacker to push malicious code to the Ruby on Rails master repository itself!

## How to Fix It
- **Developer remediation:**
  1. **Explicit Binding (Allowlisting):** Never pass raw `request.body` directly into an ORM (Object-Relational Mapping) update or create function. You must explicitly define exactly which fields the user is allowed to update.
  2. **Data Transfer Objects (DTOs):** Create strict classes (DTOs) that represent exactly what the incoming request should look like. Validate the incoming JSON against the DTO. If the JSON contains extra fields not defined in the DTO, the framework should either strip them silently or reject the request with a `400 Bad Request`.

- **Code snippet:**
  **Node.js / Express (Vulnerable):**
  ```javascript
  // BAD: Blindly updates all fields provided in req.body
  User.update(req.body, { where: { id: req.user.id } });
  ```
  **Node.js / Express (Secure):**
  ```javascript
  // GOOD: Explicitly extracts only the allowed fields
  const allowedUpdates = {
      email: req.body.email,
      bio: req.body.bio
  };
  User.update(allowedUpdates, { where: { id: req.user.id } });
  ```

## Chaining Opportunities
- This vuln + [[13 - Function-Level Access Control Bypass]] → Mass assignment is the primary method for vertically escalating privileges (e.g., making yourself an admin) to access restricted functions.

## Related Notes
- [[01 - What are Business Logic Flaws?]]
- [[13 - Function-Level Access Control Bypass]]
