---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Publishing Artifacts to Nexus

### Using Maven

To publish a JAR file artifact to Nexus using Maven, you need to configure the `settings.xml` file and the `pom.xml` file.

#### Configuring `settings.xml`

Edit the `settings.xml` file to include the Nexus repository:

```xml
<settings>
  <servers>
    <server>
      <id>nexus</id>
      <username>admin</username>
      <password>admin123</password>
    </server>
  </servers>
</settings>
```

#### Configuring `pom.xml`

Edit the `pom.xml` file to include the Nexus repository:

```xml
<project>
  <distributionManagement>
    <repository>
      <id>nexus</id>
      <url>http://<your-server-ip>:8081/repository/maven-releases/</url>
    </repository>
    <snapshotRepository>
      <id>nexus</id>
      <url>http://<your-server-ip>:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
  </distributionManagement>
</project>
```

Run the following Maven command to publish the artifact:

```bash
mvn deploy
```

### Using Gradle

To publish a JAR file artifact to Nexus using Gradle, you need to configure the `build.gradle` file.

#### Configuring `build.gradle`

Edit the `build.gradle` file to include the Nexus repository:

```groovy
plugins {
  id 'maven-publish'
}

publishing {
  repositories {
    maven {
      url "http://<your-server-ip>:8081/repository/maven-releases/"
      credentials {
        username = 'admin'
        password = 'admin123'
      }
    }
  }
  publications {
    mavenJava(MavenPublication) {
      from components.java
    }
  }
}
```

Run the following Gradle command to publish the artifact:

```bash
gradle publish
```

---
<!-- nav -->
[[05-Managing Users and Permissions|Managing Users and Permissions]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/00-Overview|Overview]] | [[07-Realistic Scenarios and Best Practices|Realistic Scenarios and Best Practices]]
