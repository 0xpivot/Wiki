---
tags: [vapt, recon, osint, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.11 GitHub Dorking for Secrets"
---

# 05.11 — GitHub Dorking for Secrets

## What is it?

GitHub is a goldmine for accidentally committed secrets. Developers regularly commit API keys, database credentials, private keys, and internal URLs. Even when they delete the commit, it remains in git history. GitHub dorking uses GitHub's search to find these exposures before attackers do.

---

## GitHub Search Operators

```
OPERATORS:
  filename:    → search specific filename
  extension:   → search file extension
  path:        → search in specific path
  org:         → within an organization
  user:        → within a user's repos
  repo:        → in a specific repo
  language:    → by programming language
  
COMBINING WITH KEYWORDS:
  "target.com" API_KEY filename:.env
  org:target-company password
  "api.target.com" secret
```

---

## Essential GitHub Dorks for VAPT

```
# CREDENTIALS AND SECRETS:
"target.com" password
"target.com" secret
"target.com" api_key
"target.com" apikey
"target.com" client_secret
"target.com" token
"target.com" credentials

# CONFIGURATION FILES:
filename:.env "target.com"
filename:config.js "target.com"
filename:database.yml "target.com"
filename:settings.py "target.com"
filename:credentials.json "target.com"
filename:.npmrc "target.com"

# CONNECTION STRINGS (database credentials!):
"target.com" "mysql://"
"target.com" "postgres://"
"target.com" "mongodb://"
"target.com" "redis://"
"target.com" "jdbc:"

# PRIVATE KEYS:
"target.com" "BEGIN RSA PRIVATE KEY"
"target.com" "BEGIN OPENSSH PRIVATE KEY"
org:target-company "-----BEGIN RSA PRIVATE KEY"

# INTERNAL ENDPOINTS:
"api.target.com" path:*
"internal.target.com" path:*
"target.corp" path:*
```

---

## Automated Tools

```bash
# TRUFFLEHOG (deep git history scanning):
trufflehog github --org=TargetOrg \
  --token=YOUR_GITHUB_TOKEN \
  --only-verified

# Scan specific repo:
trufflehog git https://github.com/target/repo.git

# GITLEAKS (detect secrets in repos):
gitleaks detect --source /path/to/cloned/repo

# Scan remote repo:
gitleaks detect --source https://github.com/target/repo \
  --no-git  # or clone first

# GITROB (find sensitive files):
gitrob analyze target-organization

# GITALLSECRETS (scan entire GitHub org):
python gitallsecrets.py -t ORG_NAME -o output.txt

# SHHGIT (real-time GitHub secret scanning):
shhgit  # monitors GitHub events for secrets

# GITHUB-SEARCH (CLI GitHub search):
github-search "target.com" "password" --type code

# Using GitHub API:
curl -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/search/code?q=target.com+password&sort=indexed" | \
  python3 -m json.tool | grep "html_url"
```

---

## Git History Analysis (After Clone)

```bash
# Clone target repo:
git clone https://github.com/target/repo.git
cd repo

# Search all commits for secrets:
git log --all --full-history --oneline  # see all commits

# Search git history for specific terms:
git log -p | grep -i "password\|secret\|api.key\|token" | head -50

# GITLEAKS on cloned repo:
gitleaks detect --source . --verbose

# TRUFFLEHOG on git history:
trufflehog git file://./  # scan local repo including history

# GITGRABER (find strings in git history):
python3 gitGraber.py -k wordlist/keys.txt -q "target.com" -s

# Manual search for credentials in history:
git log -S "password" --source --all  # find commits that added/removed "password"
git log --all --diff-filter=D --summary | grep delete  # deleted files in history

# View a specific commit:
git show abc123def456  # show commit contents

# Find secrets that were deleted (most important!):
git log --all --oneline | head -20
git show <commit-hash>  # check the deleted content!
```

---

## What to Do With Found Credentials

```
WHEN YOU FIND A SECRET:

1. DOCUMENT: Record the finding (screenshot, URL, exact string)

2. VERIFY VALIDITY (carefully):
   API key: Check if it's valid by testing against API with minimal impact
   AWS key: aws sts get-caller-identity → just check who it belongs to
   DB credential: DON'T try to connect to production database!
   
3. ASSESS IMPACT:
   AWS keys → potential full cloud compromise
   API keys → API abuse, data access
   DB credentials → data access
   Private SSH key → server access
   
4. REPORT:
   Include in findings with: what was found, where, when committed,
   current validity status, worst-case impact
   
5. RESPONSIBLE DISCLOSURE:
   For private repos: report to company directly
   For public repos: report to company (contact security@company.com)

DO NOT:
  × Use found credentials for unauthorized access
  × Keep valid credentials after engagement
  × Test against systems not in scope
```

---

## Related Notes
- [[02 - OSINT]] — broader intelligence context
- [[03 - Google Dorking]] — web-based secret hunting
- [[19 - Source Code Leakage]] — exposed .git directory on web servers
- [[17 - JavaScript File Analysis]] — secrets in client-side JS
