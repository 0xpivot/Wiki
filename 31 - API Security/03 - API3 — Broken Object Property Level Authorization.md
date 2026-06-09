---
tags: [API, Web-Security, OWASP-API, Authorization, BOPLA]
difficulty: intermediate
module: "31 - API Security"
topic: "31.03 API3 - Broken Object Property Level Authorization"
---

# 31.03 API3 — Broken Object Property Level Authorization (BOPLA)

## 1. Executive Summary
Introduced in the OWASP API Security Top 10 2023, **Broken Object Property Level Authorization (BOPLA)** represents the consolidation of two previously distinct vulnerabilities: *Mass Assignment* and *Excessive Data Exposure*. BOPLA addresses the core issue of an API failing to properly authorize access at the granular level of object *properties* (or fields), rather than just the object itself. 

An API might correctly verify that User A has access to User A's profile (preventing BOLA), but it might fail to restrict User A from modifying their `is_admin` property (Mass Assignment) or prevent the API from leaking User A's `social_security_number` back to the client (Excessive Data Exposure). 

## 2. Core Mechanics
BOPLA operates on two distinct vectors: **Reading** properties and **Updating/Writing** properties.

### 2.1 The Reading Vector (Excessive Data Exposure)
Developers often rely on the client-side application to filter data before presenting it to the user. The API queries the database, retrieves an entire object, and sends the raw JSON object to the client. If this JSON contains sensitive fields that the user shouldn't see, an attacker inspecting the HTTP traffic (e.g., via DevTools or Burp Suite) can access this data.

### 2.2 The Writing Vector (Mass Assignment)
Modern web frameworks (like Spring, Rails, Node/Express, and Django) offer mechanisms to automatically bind HTTP request parameters (JSON payloads, form data) directly to internal object models or database records. If the API doesn't define a strict whitelist of properties that are allowed to be modified, an attacker can append unexpected properties to their request payload. The framework will obediently "mass assign" these attacker-supplied values to the object, potentially altering critical business logic fields.

## 3. Architectural Context

```text
========================================================================================
                      BOPLA ATTACK ARCHITECTURE DIAGRAM
========================================================================================

                          [ Attacker ]
                               |
  +-------------------------------------------------------------------------+
  | Vector 1: Mass Assignment (Writing)                                     |
  | Request:  PUT /api/profile                                              |
  | Payload:  {"username": "hacker", "role": "admin"}                       |
  +-------------------------------------------------------------------------+
                               |
                               V
                     +-------------------+
                     |   API Framework   |
                     | (Auto-binding ORM)|
                     +-------------------+
                               |  -> Overwrites `username` (Allowed)
                               |  -> Overwrites `role` (BOPLA FLAW!)
                               V
                     +-------------------+
                     |     Database      | -> User becomes Admin.
                     +-------------------+
                               |
  +-------------------------------------------------------------------------+
  | Vector 2: Excessive Data Exposure (Reading)                             |
  | Response: 200 OK                                                        |
  | Payload:  {"username": "hacker", "role": "admin", "pwd_hash": "xyz..."} |
  +-------------------------------------------------------------------------+
                               |
                               V
                          [ Attacker ]
                  (Views hidden fields in Burp Suite)

========================================================================================
```

## 4. Attack Vectors and Threat Modeling

### 4.1 Modifying Immutable Fields
Attackers might attempt to modify fields that should be read-only, such as:
- `balance` in a financial app.
- `verified_status` in an identity management system.
- `product_price` in an e-commerce checkout flow.

### 4.2 Exploiting Default Values
During object creation (`POST`), an API might set default values (e.g., `is_premium = false`). By providing `{"is_premium": true}` in the initial creation request, the attacker bypasses payment flows.

### 4.3 Data Leakage for Reconnaissance
APIs returning fields like `internal_node_id`, `backend_ip`, or `debug_stack_trace` provide attackers with immense reconnaissance data to stage further attacks, such as Server-Side Request Forgery (SSRF) or Remote Code Execution (RCE).

## 5. Step-by-Step Testing Methodology

### 5.1 Testing for Excessive Data Exposure (Read)
1. **Traffic Interception:** Route all client traffic through an HTTP proxy (Burp Suite, OWASP ZAP).
2. **UI vs API Comparison:** Use the application naturally. When viewing a profile, note what the UI displays (e.g., Name, Email).
3. **Response Inspection:** Look at the raw JSON response in the proxy. Does it contain fields not shown in the UI? (e.g., `reset_token`, `mfa_enabled`, `internal_id`).
4. **Data Classification:** Determine if the extra fields are sensitive or represent a security risk.

### 5.2 Testing for Mass Assignment (Write)
1. **Property Discovery:** Gather a list of object properties. You can find these by:
   - Observing GET requests (Excessive Data Exposure helps here!).
   - Fuzzing common property names (`role`, `is_admin`, `permissions`, `status`).
   - Analyzing Swagger/OpenAPI documentation.
2. **Payload Modification:** Intercept a legitimate `POST` or `PUT` request.
3. **Injection:** Add the discovered or guessed properties to the JSON payload.
   ```json
   {
     "first_name": "John",
     "last_name": "Doe",
     "account_balance": 999999
   }
   ```
4. **Verification:** Check if the property was successfully modified by making a subsequent `GET` request or observing changes in application behavior.

## 6. Source Code Analysis

### 6.1 Vulnerable Implementation (Ruby on Rails)
```ruby
class UsersController < ApplicationController
  def update
    user = User.find(params[:id])
    
    # VULNERABLE: Mass Assignment. All parameters passed in the request 
    # are blindly applied to the User model.
    if user.update(params[:user]) 
      # VULNERABLE: Excessive Data Exposure. Returning the entire user object
      # including password hashes and internal IDs.
      render json: user
    else
      render json: user.errors, status: :unprocessable_entity
    end
  end
end
```

### 6.2 Secure Implementation (Ruby on Rails)
```ruby
class UsersController < ApplicationController
  def update
    user = User.find(params[:id])
    
    # SECURE: Using Strong Parameters to explicitly whitelist allowed fields.
    if user.update(user_params)
      # SECURE: Explicitly defining which fields are serialized and returned.
      render json: user.as_json(only: [:id, :first_name, :last_name, :email])
    else
      render json: user.errors, status: :unprocessable_entity
    end
  end

  private

  def user_params
    # Only permit specific fields to be updated. `is_admin` is ignored.
    params.require(:user).permit(:first_name, :last_name, :email)
  end
end
```

## 7. Advanced Exploitation Techniques

### 7.1 Nested Object Mass Assignment
Modern APIs use complex JSON structures. An attacker might target nested objects.
```json
{
  "user": {
    "name": "Attacker",
    "settings": {
      "theme": "dark",
      "two_factor_auth_enabled": false 
    }
  }
}
```
If the binding mechanism traverses deep into objects, nested properties can be manipulated.

### 7.2 Type Confusion via Mass Assignment
If an API expects an integer for a property but an attacker passes an object or array, the ORM might crash, bypass logic, or result in a Denial of Service.

## 8. Mitigation and Defense in Depth

### 8.1 Data Transfer Objects (DTOs)
Never bind client requests directly to database models. Create intermediary Data Transfer Objects (DTOs). The DTO only contains fields that the client is permitted to send or receive. Map the DTO to the internal model explicitly.

### 8.2 Strict Schema Validation
Implement robust schema validation using libraries like Joi (Node.js), Pydantic (Python), or native framework tools. Reject requests containing unexpected properties (`additionalProperties: false` in JSON Schema).

### 8.3 Response Serialization
Define explicit serialization views. Do not rely on `toJSON()` methods that dump the entire object. Use tools like GraphQL (with proper authorization) or specific REST serializers to sculpt the output data.

## 9. Chaining Opportunities
- **BOPLA (Excessive Data Exposure) -> BOLA:** Finding internal IDs leaked in a response and using them in BOLA attacks.
- **BOPLA (Mass Assignment) -> BFLA:** Overwriting a `role` property to elevate privileges, then accessing administrative endpoints.
- **BOPLA -> Account Takeover (ATO):** Modifying a `password_reset_email` property to route recovery emails to an attacker-controlled address.

## 10. Related Notes
- [[01 - API1 — Broken Object Level Authorization (BOLA)]]
- [[05 - API5 — Broken Function Level Authorization (BFLA)]]
- [[04 - API4 — Unrestricted Resource Consumption]]
