---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.12 LinkedIn and Employee OSINT"
---

# 05.12 — LinkedIn and Employee OSINT

## What is it?

LinkedIn is the world's largest professional database. For VAPT, it reveals employee names, job titles, technology stacks (from skills sections and job postings), and organizational structure — all useful for targeted attacks, password spraying, and tech-stack fingerprinting.

---

## What LinkedIn Reveals

```
1. TECHNOLOGY STACK (from employee skills):
   Employee Skills: "AWS, Kubernetes, Terraform, PostgreSQL, Redis, 
                    Spring Boot, React, Jenkins"
   → Full infrastructure map!
   → Now you know what to attack!

2. EMPLOYEE EMAIL FORMAT:
   Find any publicly visible email in LinkedIn
   → firstname.lastname@target.com
   → Now construct emails for all employees!
   
3. ORGANIZATIONAL STRUCTURE:
   CEO → CISO → Security Engineers
   → Who to phish? → Executives (high access)
   → Who knows the tech? → Engineers (can be socially engineered)

4. RECENT HIRES:
   New security hire → transitioning period → policy gaps?
   New developer → might commit secrets?

5. JOB POSTINGS:
   "Experience with Apache Kafka, Elasticsearch, Kubernetes"
   → Target uses these specific technologies!
   → Search CVEs for exact versions!

6. VENDORS AND PARTNERS:
   "Works with AWS, Salesforce, Okta"
   → These third parties have access to target!
```

---

## LinkedIn Search Techniques

```
FINDING EMPLOYEES:
  site:linkedin.com "Target Company" "Security Engineer"
  site:linkedin.com "Target Company" "DevOps"
  
  LinkedIn search: "Target Company employees"
  Filter: Current company = Target Corp

FINDING TECH STACK FROM JOB POSTINGS:
  LinkedIn Jobs → Company: Target Corp
  Read ALL job postings → extract technologies:
  
  "Backend Engineer - Required: Java 11+, Spring Boot 2.x, PostgreSQL 13+"
  → Java Spring Boot + PostgreSQL (specific versions!)
  
  "Cloud Engineer - Required: AWS (EKS, RDS, S3, CloudTrail), Terraform"
  → AWS services they use → attack surface!

FINDING EMAIL FORMAT:
  Look for employees who list their email publicly
  OR: Hunter.io (email format finder)
  OR: Check GitHub commits (email in git log!)
  OR: Job applications may reveal format in description footer
```

---

## Email Discovery Tools

```bash
# HUNTER.IO (find email format and emails):
curl "https://api.hunter.io/v2/domain-search?domain=target.com&api_key=YOUR_KEY"
# Returns: emails found online + email format pattern

# CROSSLINKED (generate email list from LinkedIn):
crosslinked -f 'first.last@target.com' -j 'Target Company'
# Scrapes LinkedIn → generates likely email addresses!

# THEHARVESTER (multiple sources):
theHarvester -d target.com -b linkedin
theHarvester -d target.com -b all -l 500

# ROCKET REACH (paid but effective):
# Find any professional email

# CLEARBIT CONNECT (free Chrome extension):
# Shows email when viewing LinkedIn profile

# FINDTHAT.EMAIL / FIND THAT LEAD:
# Online tools for finding emails

# VERIFY EMAILS:
# https://tools.emailhippo.com/
# https://verify-email.org/
# Or: send test email and check bounce (careful - might alert them!)
```

---

## Password Spraying with Found Emails

```
WARNING: Password spraying requires explicit authorization in RoE!
Only do this with written permission — it can lock accounts!

COMMON SPRAY TARGETS:
  - Company VPN (Cisco ASA, Fortinet, Palo Alto)
  - Email (OWA, webmail)
  - Azure AD / O365
  - Slack
  - Corporate SSO

COMMON PASSWORDS TO TRY:
  Company@2024    (company name + year)
  Company@2023
  Welcome@1234
  Password@123
  Season+Year: Summer2024!, Winter2023@
  Company+Season: Target@Spring24

TOOLS (with authorization):
  spray -u users.txt -p "Company@2024" -d target.com -m owa
  ruler --domain target.com brute --userpass credentials.txt
  
  BURP SUITE: Intruder → load user list → single password

LOCKOUT AWARENESS:
  Most orgs lock after 5-10 failed attempts
  Space attempts (1/hour) to avoid lockout
  Or use "low and slow" approach
```

---

## People OSINT for Social Engineering (Red Team Context)

```
FOR RED TEAM ENGAGEMENT (explicit authorization required):
  
TARGETS:
  IT helpdesk → call pretending to be employee
  Finance → business email compromise (BEC) target
  Executives → spear phishing with personalized lures
  
INFORMATION TO GATHER:
  Name, title, manager name, direct reports
  Recent projects (from LinkedIn posts)
  Interests (for lure personalization)
  Work events (conferences, trade shows)
  
SOCIAL ENGINEERING APPLICATIONS:
  Vishing: call helpdesk as "John Smith from finance" 
  Phishing: email targeting recent LinkedIn milestone
  Pretexting: impersonate IT support using employee info
  
LEGAL/ETHICAL:
  Only for authorized red team engagements
  Stop if you've gathered enough to prove feasibility
  Never actually defraud or harm individuals
```

---

## Related Notes
- [[02 - OSINT]] — OSINT framework
- [[13 - Email Harvesting]] — email discovery tools
- [[04.10 - Bug Bounty vs Pentest]] — scope of people OSINT
