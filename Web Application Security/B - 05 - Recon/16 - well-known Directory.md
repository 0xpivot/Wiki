---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.16 .well-known Directory"
---

# 05.16 — .well-known Directory

## What is it?

The `/.well-known/` directory (RFC 5785) is a standardized location for well-known services and information files. It's used for domain verification, security contacts, mobile app linking, and other machine-readable metadata. Each file in this directory can reveal information about the target's infrastructure and services.

---

## Important .well-known Files

```
/.well-known/security.txt      → Bug bounty/responsible disclosure info
/.well-known/robots.txt        → Alternative robots location (less common)
/.well-known/change-password   → Password change page URL
/.well-known/openid-configuration → OAuth/OIDC configuration!
/.well-known/jwks.json         → JSON Web Key Set (JWK public keys)
/.well-known/oauth-authorization-server → OAuth server metadata
/.well-known/assetlinks.json   → Android app deep link verification
/.well-known/apple-app-site-association → iOS app deep link verification
/.well-known/dnt-policy.txt    → Do Not Track policy
/.well-known/core              → CoAP resource discovery
/.well-known/matrix            → Matrix server config
/.well-known/caldav, carddav   → Calendar/contacts server
```

---

## High-Value: OpenID Connect Configuration

```bash
# FETCH OIDC CONFIG (huge intelligence!):
curl -s https://target.com/.well-known/openid-configuration | python3 -m json.tool
# OR:
curl -s https://auth.target.com/.well-known/openid-configuration

TYPICAL RESPONSE:
{
  "issuer": "https://auth.target.com",
  "authorization_endpoint": "https://auth.target.com/oauth2/authorize",
  "token_endpoint": "https://auth.target.com/oauth2/token",
  "userinfo_endpoint": "https://auth.target.com/oauth2/userinfo",
  "jwks_uri": "https://auth.target.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.target.com/oauth2/register",
  "scopes_supported": ["openid", "profile", "email", "admin"],
  "response_types_supported": ["code", "token", "id_token"],
  "grant_types_supported": ["authorization_code", "implicit", "password"],
  "id_token_signing_alg_values_supported": ["RS256", "HS256"]
}

REVEALS:
  → OAuth/OIDC endpoints → attack targets!
  → Supported grant types (is "password" grant enabled? → brute force!)
  → Supported algorithms (HS256? → JWT weak secret attack)
  → Admin scope supported? → try to get admin token!
```

---

## JWKS — JSON Web Key Set

```bash
# FETCH JWK PUBLIC KEYS:
curl -s https://target.com/.well-known/jwks.json | python3 -m json.tool

EXAMPLE RESPONSE:
{
  "keys": [{
    "kty": "RSA",
    "use": "sig",
    "kid": "key1",
    "n": "0vx7agoebGcQSuuPiLJXZptN...",  ← public key
    "e": "AQAB"
  }]
}

VAPT USE CASES:
  1. JWT RS256 → HS256 confusion attack:
     Get RSA public key from JWKS
     Forge JWT using public key as HMAC secret!
     If server accepts HS256 with RSA public key → critical!
  
  2. Algorithm confusion:
     Server configured for RS256 but allows algorithm override
     → Change JWT header alg to HS256
     → Sign with public key (known!) → forge any JWT!
```

---

## Mobile App Deep Link Verification

```bash
# iOS — Apple App Site Association:
curl -s https://target.com/.well-known/apple-app-site-association | python3 -m json.tool

REVEALS:
{
  "applinks": {
    "apps": [],
    "details": [{
      "appID": "TEAMID.com.target.app",
      "paths": ["/account/*", "/payment/*", "/admin/*"]
    }]
  }
}

→ TEAMID is the Apple Developer Team ID! (fingerprinting)
→ Deep link paths (potential attack surface in mobile app)
→ Admin paths that mobile app can handle (hidden functionality!)

# Android — Asset Links:
curl -s https://target.com/.well-known/assetlinks.json | python3 -m json.tool

REVEALS:
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.target.app",
    "sha256_cert_fingerprints": ["AB:CD:EF:..."]
  }
}]

→ App package name (com.target.app → find APK for analysis!)
→ Certificate fingerprint (for cert pinning bypass research)
```

---

## Checking All .well-known Files

```bash
# Common .well-known file list:
WELLKNOWN_FILES=(
  security.txt
  openid-configuration
  jwks.json
  oauth-authorization-server
  assetlinks.json
  apple-app-site-association
  dnt-policy.txt
  change-password
  core
  nodeinfo
  caldav
  carddav
)

for file in "${WELLKNOWN_FILES[@]}"; do
  url="https://target.com/.well-known/$file"
  code=$(curl -s -o /tmp/wk-content -w "%{http_code}" "$url")
  if [ "$code" = "200" ]; then
    echo "FOUND: $url"
    cat /tmp/wk-content | head -5
  fi
done
```

---

## Related Notes
- [[15 - robots.txt and sitemap.xml]] — other standard files
- [[18 - Authorization header]] — OAuth JWT attacks
- [[Module 14 - OAuth and OIDC]] — full OAuth attack guide
