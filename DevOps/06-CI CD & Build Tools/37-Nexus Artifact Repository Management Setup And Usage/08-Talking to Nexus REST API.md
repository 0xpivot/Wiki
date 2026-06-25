---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Talking to Nexus REST API

### Nexus REST API

The Nexus REST API allows you to interact with Nexus programmatically. This is useful for automating tasks and integrating Nexus with other tools.

#### Example Request

Here is an example of a GET request to retrieve information about a repository:

```http
GET /service/rest/v1/repositories/maven-releases HTTP/1.1
Host: <your-server-ip>:8081
Authorization: Basic YWRtaW46YWRtaW4xMjM=
Accept: application/json
```

#### Example Response

```json
{
  "name": "maven-releases",
  "format": "maven2",
  "type": "hosted",
  "apt": {},
  "bower": {},
  "cocoapods": {},
  "conan": {},
  "docker": {},
  "gitlfs": {},
  "group": {},
  "nuget": {},
  "npm": {},
  "pypi": {},
  "raw": {},
  "rubygems": {},
  "yum": {},
  "negativeCache": {
    "enabled": false,
    "timeToLive": 1440
  },
  "online": true,
  "storage": {
    "blobStoreName": "default",
    "strictContentValidation": true,
    "writePolicy": "allow_once"
  },
  "cleanup": {
    "policyNames": []
  },
  "component": {
    "proprietaryComponents": false
  },
  "versionPolicy": "release",
  "cleanupOnStartup": false,
  "autoBlock": true,
  "writable": true,
  "browseable": true,
  "metadata": {
    "attributes": {}
  }
}
```

### Example Scenario

Suppose you want to automate the process of creating a new repository. You can use the Nexus REST API to create the repository programmatically.

---
<!-- nav -->
[[08-Setting Up Nexus on DigitalOcean|Setting Up Nexus on DigitalOcean]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/10-Conclusion|Conclusion]]
