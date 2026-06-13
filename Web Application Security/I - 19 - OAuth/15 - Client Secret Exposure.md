---
tags: [vapt, oauth, beginner]
difficulty: beginner
module: "19 - OAuth"
topic: "19.15 Client Secret Exposure"
---

# 19.15 — Client Secret Exposure

## What Is the Client Secret?

```
CLIENT CREDENTIALS IN OAUTH:
  client_id     = Public identifier of the app (like username)
  client_secret = Private password of the app
  
  Used in the token exchange step:
  POST /oauth/token {
    grant_type=authorization_code,
    code=AUTH_CODE,
    client_id=CLIENT_ID,        ← public, OK to see
    client_secret=CLIENT_SECRET ← PRIVATE, must stay on server!
    redirect_uri=...
  }
  
  Purpose of client_secret:
  → Proves token request came from the LEGITIMATE app
  → Not just anyone who intercepted an auth code
  → Binds auth code to the registered client
  
  IF SECRET IS EXPOSED:
  → Attacker can impersonate the app
  → Exchange any auth code for tokens
  → Makes redirect_uri bypass irrelevant!
```

---

## Where Secrets Leak

### 1. JavaScript / Mobile App Source Code

```
BIGGEST MISTAKE:
  Including client_secret in frontend code
  
  // JavaScript (frontend — NEVER DO THIS):
  const CLIENT_SECRET = "abc123supersecretvalue";
  
  // Android (Java):
  String CLIENT_SECRET = "abc123supersecretvalue";
  
  FINDING:
  View source → Ctrl+F "secret" or "CLIENT_SECRET"
  Decompile APK: apktool d app.apk → grep -r "secret" ./
  
  WHY IT HAPPENS:
  Developer copies backend code to frontend
  Developer doesn't understand client secret must stay on server
  Framework template includes it (bad tutorial/template)
  
  IMPACT: Anyone can extract secret → impersonate app
```

### 2. GitHub / Public Repositories

```bash
# SEARCH GITHUB FOR EXPOSED SECRETS:
# Google dorks:
# "client_secret" "target.com" site:github.com
# "OAUTH_SECRET" "target.com" site:github.com
# filename:.env "CLIENT_SECRET"

# Check git history (secret deleted but still in history!):
git log --all --full-history --source --oneline -- .env
git show COMMIT_HASH:.env  # show old version of file

# Tools for git history scanning:
# trufflehog: trufflehog git https://github.com/target/repo
# gitleaks: gitleaks detect --source . --verbose

# GitHub API search:
curl "https://api.github.com/search/code?q=client_secret+COMPANY_NAME" \
  -H "Authorization: token YOUR_GITHUB_TOKEN"
```

### 3. Docker Images

```bash
# DOCKER IMAGE LAYER INSPECTION:
# Each RUN command creates a layer
# If secret was ever in a layer, it persists even if later deleted!

docker pull target/app-image
docker history target/app-image --no-trunc
# Look for: ENV CLIENT_SECRET=... or echo "secret" in RUN commands

# Inspect all layers:
docker save target/app-image | tar -xv
# or use dive tool:
dive target/app-image

# Also check environment variables in running containers:
docker inspect CONTAINER_ID | grep -i secret
```

### 4. CI/CD Pipeline Logs

```
CI/CD LOGS OFTEN PUBLIC OR ACCESSIBLE:
  Build scripts echo environment variables for debugging
  Test output includes API calls with credentials
  
  LOOK FOR:
  - Travis CI public repo builds (logs accessible)
  - GitHub Actions run logs (if public repo)
  - Jenkins console output
  
  FINDING IN LOGS:
  curl https://auth.example.com/token -d "client_secret=SECRET"
  → If this command runs in CI → secret in build log!
  
  CHECK:
  /github/workflows/*.yml → look for secrets usage
  Does any step print env vars? (set -x, env, printenv)
```

### 5. API Documentation

```
DEVELOPERS SOMETIMES PUT REAL SECRETS IN DOCS:
  "Example request: curl ... -d 'client_secret=actualRealSecretHere'"
  
  Check: docs.target.com, developer.target.com, api.target.com
  Look at: code examples, getting started guides, Postman collections
  
  POSTMAN COLLECTIONS:
  Many orgs share Postman collections with real credentials
  Site: postman.com/explore → search target company name
```

---

## Testing for Exposed Secrets

```bash
# QUICK CHECKS:
# 1. View page source → search for "secret"
# 2. Check .js bundle files
# 3. Check mobile app (decompile)
# 4. Check GitHub org repos
# 5. Check docker hub images

# AUTOMATED SCAN OF JAVASCRIPT FILES:
# Download all JS files from target:
wget -r -l1 -H -t1 -nd -N -np -A.js https://app.target.com -P ./js_files/
grep -ri "client_secret\|oauth_secret\|app_secret" ./js_files/

# VERIFY FOUND SECRET WORKS:
# (Only in authorized testing!)
curl -X POST https://auth.target.com/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=FOUND_CLIENT_ID" \
  -d "client_secret=FOUND_SECRET"
# → token issued? → SECRET IS VALID AND EXPOSED!

# ALSO TEST: CAN SECRET EXCHANGE ARBITRARY CODE?
# (Demonstrates full impact of exposure)
```

---

## Impact of Client Secret Exposure

```
WHAT ATTACKER CAN DO:
  1. Exchange any intercepted auth code for tokens:
     → Combine with redirect_uri bypass or code interception
     → Full account takeover chain!
     
  2. Make API calls as the application:
     → Some APIs have "app-level" access beyond user level
     → May access ALL users' data if API is user-agnostic
     
  3. Client credentials flow (machine-to-machine):
     → Impersonate the service itself
     → Access all service-to-service APIs
     
  4. Token introspection:
     → Some introspection endpoints require client auth
     → With secret → can check validity of any token
```

---

## Fix

```
PROTECTING CLIENT SECRETS:

CONFIDENTIAL CLIENTS (server-side apps):
  ✓ Store secret in environment variables or secrets manager:
     AWS: AWS Secrets Manager
     GCP: Secret Manager
     HashiCorp: Vault
     Docker: Docker Secrets
     K8s: Kubernetes Secrets (+ sealed secrets)
     
  ✓ NEVER commit to version control
  ✓ NEVER include in Docker image (use runtime injection)
  ✓ NEVER log or print the secret
  ✓ Rotate secrets regularly
  
  # Python (reading from environment):
  import os
  CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']  # not hardcoded!
  
  # .gitignore (mandatory):
  .env
  *.secrets
  config/secrets.yml

PUBLIC CLIENTS (SPAs, Mobile Apps):
  ✓ Public clients CANNOT safely store a secret
  ✓ Solution: Use Auth Code + PKCE (no client secret needed)
  ✓ Never include client_secret in mobile app or JavaScript
  
  # OAuth registration: mark as "public client"
  # No client_secret issued → PKCE provides proof instead

DETECTION:
  ✓ Pre-commit hooks to catch secrets before push
  ✓ GitHub secret scanning (built-in for public repos)
  ✓ Automated scanning: trufflehog, gitleaks, detect-secrets
  ✓ Regular secret rotation (reduces window if compromised)
```

---

## Related Notes
- [[04 - Client Credentials Flow]] — machine-to-machine, secret usage
- [[05 - PKCE — What It Protects Against]] — alternative to client secret for public clients
- [[14 - Token Replay Attack]] — using stolen token after secret exposure
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
