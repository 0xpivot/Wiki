---
tags: [vapt, information-disclosure, api, excess-data, intermediate]
difficulty: intermediate
module: "33 - Information Disclosure"
topic: "33.11 API Response Over-Exposure"
---

# API Response Over-Exposure (Excessive Data Exposure)

## 1. Introduction

API Response Over-Exposure (historically categorized under OWASP API Top 10 as API3:2019 Excessive Data Exposure, and closely related to API1:2023 Broken Object Level Authorization) occurs when an Application Programming Interface (API) backend returns more data to the client than is strictly necessary to fulfill the immediate functional requirement. 

Instead of filtering data on the server side to send only what the user interface (UI) requires, developers mistakenly rely on the client-side application (like a frontend React, Angular, or mobile app) to filter the data and display only the relevant fields to the user.

While the end-user looking at the polished application interface sees no anomaly, an attacker monitoring the raw HTTP/HTTPS traffic can intercept the full, unfiltered JSON or XML response, which often contains highly sensitive Information. This represents a severe architectural flaw where the server inherently trusts the client to act as a data shield.

## 2. The Core Underlying Problem: ORMs and Lazy Serialization

To truly understand this vulnerability, one must understand how modern web applications are built. Most contemporary frameworks rely on Object-Relational Mapping (ORM) tools (e.g., Hibernate in Java, Entity Framework in .NET, Sequelize in Node.js, ActiveRecord in Ruby).

ORMs allow developers to query databases and receive programmatic objects in return. 
A standard database row representing a user might look like this:
`{ id, username, email, password_hash, reset_token, role, created_at, updated_at, internal_notes, last_login_ip }`

When the frontend simply needs to display a list of usernames to populate a dropdown menu, the developer *should* write a specific query to fetch only the `username` field. However, to save time, developers often fetch the entire object using a generic `User.findAll()` method.

Then, instead of creating a Data Transfer Object (DTO) to selectively serialize only safe fields for the API response, they serialize the *entire database object* directly to JSON:
`res.json(userObject);`

The frontend JavaScript receives the massive payload but only renders `userObject.username`. The rest of the data—including password hashes, IP addresses, and PII—remains invisible in the browser window, but fully exposed in the network layer.

## 3. Visual Architecture of the Vulnerability

The following ASCII diagram illustrates the flawed architecture that leads to API Response Over-Exposure.

```text
       DATABASE                  BACKEND API (Node/Spring/Django)           CLIENT APP (Browser/Mobile)
+-----------------------+      +---------------------------------+      +---------------------------------+
|                       |      | 1. Query: User.findById(5)      |      | 3. Raw Data Received:           |
| User Table            | <--> |                                 |      | {                               |
| - id: 5               |      | 2. Receives full object.        |      |   "id": 5,                      |
| - username: "alice"   |      |                                 |======|   "username": "alice",          |
| - role: "admin"       |      | 3. Directly serializes to JSON. |      |   "role": "admin",              |
| - pass_hash: "bcrypt" |      |    res.send(user);              |      |   "pass_hash": "bcrypt",        |
| - ssn: "000-00-0000"  |      |                                 |      |   "ssn": "000-00-0000",         |
| - reset_token: "xyz"  |      |                                 |      |   "reset_token": "xyz"          |
+-----------------------+      +---------------------------------+      | }                               |
                                                                        |                                 |
                                                                        | 4. Frontend Code:               |
                                                                        |    <h1>{user.username}</h1>     |
                                                                        +---------------------------------+
                                                                                         |
  ATTACKER / PEN-TESTER <================================================================+
  Using Burp Suite, the attacker intercepts Step 3. 
  They see the exact same raw data as the client app, including the SSN, Hash, and Tokens!
```

## 4. REST vs GraphQL Over-Exposure

### REST API Over-Exposure
In REST architecture, endpoints are generally fixed (e.g., `GET /api/v1/users/5`). The structure of the response is entirely determined by the backend developer. If the developer includes excessive properties in the returned resource representation, the vulnerability is static and predictable. Attackers simply need to enumerate endpoints and inspect the responses. Testing is a matter of crawling the application and observing the JSON blobs returned.

### GraphQL Over-Exposure and Introspection
GraphQL introduces a radically different dynamic. By design, GraphQL allows the *client* to specify exactly what data it wants. 
A legitimate client query from the frontend might look like this:
```graphql
query {
  user(id: 5) {
    username
  }
}
```
The server correctly returns *only* the username. 
However, if the backend GraphQL resolvers are not strictly locked down, an attacker can simply modify the query to request fields that the frontend doesn't normally ask for, but which the backend database holds. 

But how does the attacker know what fields exist? Through **Introspection**. If introspection is enabled (a common misconfiguration), the attacker can query the schema itself:
```graphql
query {
  __schema {
    types {
      name
      fields {
        name
      }
    }
  }
}
```
Once the schema is known, the attacker crafts a malicious query:
```graphql
query {
  user(id: 5) {
    username
    role
    passwordHash
    creditCardTokens
    internal_admin_notes
  }
}
```
If the resolver blindly fetches the user object and the schema exposes those fields, GraphQL becomes an incredibly powerful tool for over-exposure and data mining.

## 5. Discovery Methodology

Discovering this vulnerability cannot be done purely visually through a web browser. It requires intercepting and analyzing the raw network traffic.

### 5.1 Tools of the Trade
*   **Burp Suite Professional / Community:** The standard tool for proxying traffic. Features like passive scanning automatically flag huge JSON blobs.
*   **Browser Developer Tools (F12):** The `Network` tab is sufficient for quick checks. Filtering by `Fetch/XHR` allows you to see the exact JSON payloads returned by APIs.
*   **Postman / Insomnia:** Useful for replaying API requests and analyzing responses in a clean environment.
*   **Kiterunner:** An API-specific directory discovery tool that can help find hidden endpoints that might be leaking data.
*   **Ffuf / Wfuzz:** Used to brute-force integer IDs on API endpoints to scrape large quantities of exposed data.

### 5.2 Step-by-Step Discovery
1.  **Proxy all Traffic:** Configure your browser to route traffic through Burp Suite.
2.  **Navigate the Application:** Perform normal user actions. View profiles, search for items, load dashboards, check transaction histories. Interact with every UI element.
3.  **Analyze the HTTP History:** In Burp, sort the proxy history by MIME type (looking for `application/json` or `application/xml`).
4.  **Compare UI vs Response:** Look at a specific page in the browser (e.g., a list of 10 users showing only names and avatars). Now look at the corresponding API response in Burp. If the JSON payload contains 50 fields for each user, including `date_of_birth`, `home_address`, or `account_balance`, you have found API Over-Exposure.

## 6. Exploitation and Impact Assessment

While "Information Disclosure" might sound benign to some developers, API Over-Exposure frequently leads to catastrophic data breaches.

### Real World Scenario 1: The Dating App
Consider a dating application where users can view profiles of potential matches. 
The UI displays: `First Name`, `Age`, `Distance`, and `Bio`.
Behind the scenes, the mobile app calls: `GET /api/matches/nearby`

The API returns:
```json
{
  "matches": [
    {
      "id": "user-89312",
      "first_name": "Bob",
      "age": 28,
      "distance_miles": 4.2,
      "bio": "Love hiking and dogs.",
      "exact_location": {
        "lat": 34.0522,
        "long": -118.2437
      },
      "email_address": "bob.smith@example.com",
      "facebook_id": "8931289412",
      "premium_member": true,
      "hidden_matches_count": 15
    }
  ]
}
```
**Impact Breakdown:**
1.  **PII Leakage:** The `email_address` and `facebook_id` are exposed, breaking anonymity.
2.  **Physical Security / Stalking:** The `exact_location` coordinates are leaked, despite the UI only showing "4.2 miles away". 
3.  **Business Logic Leaks:** The `premium_member` boolean is exposed, potentially leading to Mass Assignment attacks (where an attacker tries to send a `PUT` request setting this to `true` for their own account).

### Real World Scenario 2: The E-Commerce Platform
An attacker visits an e-commerce platform and views an item for sale: `GET /api/products/99`.
The UI shows the price, title, and images. The API response contains:
```json
{
  "product_id": 99,
  "title": "Bluetooth Headphones",
  "price": 49.99,
  "stock_count": 150,
  "supplier_cost": 12.50,
  "supplier_contact": "vendor@electronics-supplier.com"
}
```
**Impact:** A direct breach of confidential business data. Competitors can scrape the entire catalog, identify exactly what the platform pays their suppliers (`supplier_cost`), and undercut their prices, or bypass them entirely by contacting the supplier directly.

### Exploitation via Data Mining (Scraping)
An attacker can write a simple Python script to iterate through an IDOR-vulnerable endpoint (e.g., `GET /api/users/[1-10000]`) and harvest the excessively exposed JSON data. This leads to massive database dumps and user enumerations, forming the basis of credential stuffing attacks or targeted phishing campaigns.

## 7. Intersection with Mass Assignment

Mass Assignment and API Response Over-Exposure are two sides of the same coin. 
*   **Over-Exposure** happens on the `GET` request (the server gives you too much).
*   **Mass Assignment** happens on the `POST`/`PUT` request (the server accepts too much).

If an API suffers from Over-Exposure, it is essentially providing the attacker with a blueprint of the database schema. If the attacker sees that a `GET` request returns an `is_admin` property, they know exactly what payload to craft to exploit a Mass Assignment vulnerability.

## 8. Detecting Over-Exposure Automatically

To scale testing, automated tools can be utilized to compare the data sent by the API against the data actually rendered on the DOM.
1.  **Burp Extensions:** Extensions like *API Scanner* or *AutoRepeater* can highlight excessively large JSON responses.
2.  **Diffing:** Run an API request as a low-privileged user, and run the same request as a high-privileged user. Diff the JSON responses. If the low-privileged user receives fields they shouldn't (even if the UI hides them), it's a finding.
3.  **TruffleHog for APIs:** Some variants of secrets scanners can be hooked into proxies to automatically detect API keys or tokens leaking in JSON responses.

## 9. Extended Case Study: The Healthcare Portal Data Bleed

A real-world example of API Over-Exposure occurred in a popular telehealth application. The application had a feature allowing patients to search for doctors by name or specialty. The API request was `GET /api/v2/doctors?search=cardiologist`.

The UI displayed a list of doctors, showing only their Name, Specialty, and Clinic Address. However, the API was returning the entire serialized `Doctor` object from the backend database. This object included:
```json
{
  "id": "dr-491",
  "name": "Dr. Alice Smith",
  "specialty": "Cardiology",
  "clinic_address": "123 Main St",
  "home_address": "456 Private Dr",
  "personal_cell_phone": "555-0199",
  "dea_registration_number": "AB1234567",
  "internal_performance_rating": 2.4
}
```
An attacker simply intercepted this API response and wrote a scraper to download the entire directory of doctors. The leakage of the `dea_registration_number` (Drug Enforcement Administration number) and personal contact information led to a severe regulatory fine under HIPAA, despite the fact that no complex "hacking" was required—the server simply over-shared.

## 10. Architectural Remediation Deep Dive
To fix Over-Exposure at an architectural level, organizations should adopt:
1. **Strict GraphQL Safelists:** If using GraphQL, disable introspection in production and use Persisted Queries, where the frontend can only request pre-approved queries.
2. **Contract-Driven Development:** Define API responses using OpenAPI/Swagger specifications. Use automated testing tools (like Dredd or schemathesis) to ensure the API never returns fields that are not explicitly documented in the contract.

## Chaining Opportunities
*   **[[01 - Insecure Direct Object References (IDOR)]]**: Combine IDOR to iterate through thousands of user profiles, leveraging the API Over-exposure to dump the entire database structure.
*   **[[18 - Mass Assignment]]**: Over-exposure reveals the exact backend property names (e.g., `is_admin`, `premium_status`). The attacker can then attempt to modify these properties using Mass Assignment (sending them in a `POST` or `PUT` request).
*   **[[12 - Defense]]**: Understanding defense is critical to writing mitigation recommendations for this vulnerability.

## Related Notes
*   [[08 - Privilege Escalation]]
*   [[10 - Comment Disclosure in HTML Source]]
*   [[15 - Discovering Hidden APIs]]
