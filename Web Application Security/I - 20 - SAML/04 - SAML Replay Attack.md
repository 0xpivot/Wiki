---
tags: [vapt, saml, intermediate]
difficulty: intermediate
module: "20 - SAML"
topic: "20.04 SAML Replay Attack"
---

# 20.04 — SAML Replay Attack

## What Is a SAML Replay Attack?

```
SAML ASSERTION = SIGNED DOCUMENT:
  It's a time-limited proof of identity
  
  REPLAY ATTACK:
  Attacker captures a valid SAML assertion
  → Submits it AGAIN (later, or to different SP)
  → SP processes it as if fresh authentication
  
  WHY POSSIBLE:
  1. Assertion doesn't expire (no NotOnOrAfter, or not checked)
  2. Assertion has been used before (should be single-use)
  3. Assertion InResponseTo not validated (no tie to original request)
  4. Assertion replayed to different SP (audience not checked)
```

---

## Types of SAML Replay

### 1. Same SP Replay (Literal Replay)

```
SCENARIO:
  User A logs in via SAML → SP processes assertion → creates session
  
  Attacker was watching (e.g., intercepted traffic, or found assertion in logs)
  
  Attacker replays same SAMLResponse to SP:
  POST /saml/acs
  SAMLResponse=CAPTURED_VALID_RESPONSE
  
  IF SP DOESN'T TRACK USED ASSERTIONS:
  → SP validates signature (still valid!) → logs attacker in as User A!
  
HOW SP SHOULD PROTECT:
  Track assertion IDs (AssertionID) in a short-lived cache
  If same AssertionID seen again → REJECT
```

### 2. Cross-SP Replay (Audience Bypass)

```
SCENARIO:
  Company has: Salesforce (SP-A) and Slack (SP-B) using same IdP
  
  User logs in to Salesforce → SP-A gets assertion:
  <saml:Audience>https://salesforce.com</saml:Audience>
  
  IF SP-B (Slack) doesn't validate Audience:
  Attacker takes Salesforce assertion → submits to Slack:
  POST https://slack.com/saml/acs
  SAMLResponse=SALESFORCE_ASSERTION
  
  Slack: "Signature is valid from our IdP... logging in!"
  → But the assertion was for Salesforce, not Slack!
  
IMPACT: 
  Any assertion for any SP in the same IdP → can authenticate to vulnerable SP!
```

### 3. Timing-Based Replay

```
SAML ASSERTION HAS VALIDITY WINDOW:
  NotBefore="2024-01-15T12:00:00Z"
  NotOnOrAfter="2024-01-15T12:05:00Z"
  
  Attacker captures assertion during valid window
  Replays it BEFORE it expires → success!
  
  OR: SP doesn't check NotOnOrAfter → assertion valid forever!
  
  CLOCK SKEW:
  Servers may be slightly out of sync
  Best practice: allow ±5 min clock skew
  BUT: very loose skew (30 min) → wider replay window
```

### 4. InResponseTo Not Validated

```
SP-INITIATED FLOW:
  SP sends AuthnRequest with ID="_req123"
  Assertion should contain: InResponseTo="_req123"
  
  This TIES the assertion to a specific request from this SP session
  
  IF SP IGNORES InResponseTo:
  → Assertion from any flow can be replayed
  → Or: assertion from IdP-initiated flow accepted in SP-initiated context
  → No guarantee the user actively chose to authenticate right now
```

---

## Testing for Replay Vulnerabilities

```bash
# TEST 1: LITERAL REPLAY
# 1. Complete SAML login, capture SAMLResponse in Burp
# 2. Log out (or just start a new session)
# 3. Replay the captured SAMLResponse:
#    Burp: Send to Repeater → change cookie/session → forward
#    OR: Use curl with the captured SAMLResponse
curl -X POST https://app.example.com/saml/acs \
  -d "SAMLResponse=CAPTURED_VALUE&RelayState=/"
# → Logged in? → No assertion replay prevention!

# TEST 2: EXPIRED ASSERTION REPLAY
# 1. Wait until after the NotOnOrAfter time
#    (usually 5 minutes after assertion issued)
# 2. Replay the captured SAMLResponse
# → Still works? → Expiry not checked!

# TEST 3: CROSS-SP REPLAY
# 1. Capture assertion from SP-A
# 2. Submit to SP-B:
curl -X POST https://sp-b.example.com/saml/acs \
  -d "SAMLResponse=ASSERTION_FOR_SP_A"
# → Logged in? → Audience not validated!

# TEST 4: InResponseTo CHECK
# Capture a valid SAMLResponse from one flow
# Start a NEW auth flow (get new AuthnRequest ID)
# Submit OLD SAMLResponse to the NEW callback
# → Still accepted? → InResponseTo not validated!

# CHECK ASSERTION STRUCTURE:
# Verify what values are in the assertion:
echo "SAML_VALUE" | base64 -d | grep -E "NotOnOrAfter|Audience|InResponseTo|AssertionID"
```

---

## Fix

```
PREVENTING REPLAY ATTACKS:

1. TRACK USED ASSERTION IDs (primary defense):
   # Redis-based:
   def process_saml_response(response):
       assertion_id = response.assertion.id
       
       # Check if we've seen this ID before:
       if redis.exists(f"used_assertion:{assertion_id}"):
           raise Exception("Assertion already used!")
       
       # Mark as used (TTL = NotOnOrAfter - now + clock_skew):
       ttl = (not_on_or_after - datetime.utcnow()).seconds + 300
       redis.setex(f"used_assertion:{assertion_id}", ttl, "1")
       
       # Process normally
       return process_identity(response)

2. VALIDATE NotOnOrAfter:
   now = datetime.utcnow()
   if now >= assertion.not_on_or_after:
       raise Exception("Assertion expired!")

3. VALIDATE AUDIENCE:
   if assertion.audience != YOUR_ENTITY_ID:
       raise Exception("Assertion not for this SP!")

4. VALIDATE InResponseTo (for SP-initiated flows):
   expected_id = session.pop('authn_request_id', None)
   if assertion.in_response_to != expected_id:
       raise Exception("Assertion not for this request!")

5. VALIDATE NotBefore:
   if now < assertion.not_before - timedelta(seconds=CLOCK_SKEW):
       raise Exception("Assertion not yet valid (clock skew)!")

CLOCK SKEW RECOMMENDATION:
  Allow ±5 minutes maximum (300 seconds)
  Larger skew = larger replay window
```

---

## Related Notes
- [[02 - SAML Assertion Structure]] — assertion elements (NotOnOrAfter, Audience, InResponseTo)
- [[03 - XML Signature Wrapping (XSW) Attacks]] — signature-based attacks
- [[09 - SAML to Account Takeover]] — full attack chains
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — full defense
