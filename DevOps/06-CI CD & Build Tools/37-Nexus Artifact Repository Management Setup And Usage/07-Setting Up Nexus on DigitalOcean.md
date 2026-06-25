---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up Nexus on DigitalOcean

### Prerequisites

Before setting up Nexus, ensure you have the following:

1. **DigitalOcean Account**: Sign up for a DigitalOcean account if you don’t already have one.
2. **Server**: Create a new server instance on DigitalOcean. Choose a Linux distribution (e.g., Ubuntu 20.04 LTS) and allocate appropriate resources (CPU, RAM, and disk space).

### Installing Java

Nexus requires Java to run. Ensure Java is installed on your server:

```bash
sudo apt update
sudo apt install openjdk-11-jdk
```

Verify the installation:

```bash
java -version
```

### Downloading and Installing Nexus

Download the latest version of Nexus from the official website:

```bash
wget https://download.sonatype.com/nexus/3/latest-unix.tar.gz
tar xvf latest-unix.tar.gz
sudo mv nexus /opt/
```

Create a system user for Nexus:

```bash
sudo useradd --no-create-home --shell /bin/false nexus
```

Change ownership of the Nexus directory:

```bash
sudo chown -R nexus:nexus /opt/nexus
```

Create a systemd service file for Nexus:

```bash
sudo nano /etc/systemd/system/nexus.service
```

Add the following content to the `nexus.service` file:

```ini
[Unit]
Description=nexus service
After=network.target

[Service]
Type=forking
LimitNOFILE=65536
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
Environment=JAVACMD=/usr/bin/java
Environment=MEMINIT=-Xms1g
Environment=MEMMAX=-Xmx1g
Environment=NETTY_BOSS_THREAD_COUNT=2
Environment=NETTY_WORKER_THREAD_COUNT=4
Environment=RUN_JETTY_RUNNER=-Djetty.port=8081
Environment=RUN_JETTY_RUNNER=-Djetty.request.header.size=65536
Environment=RUN_JETTY_RUNNER=-Djetty.response.header.size=65536
Environment=RUN_JETTY_RUNNER=-Djetty.http.config.customizer.class=org.sonatype.nexus.bootstrap.jetty.JettyHttpConfigurationCustomizer
Environment=RUN_JETTY_RUNNER=-Djetty.https.config.customizer.class=org.sonatype.nexus.bootstrap.jetty.JettyHttpsConfigurationCustomizer
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.provider=SunJSSE
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStorePath=/opt/nexus/etc/ssl/keystore.jks
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStorePassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyManagerPassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStorePath=/opt/nexus/etc/ssl/truststore.jks
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStorePassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.protocol=TLSv1.2
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.ciphers=TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_DHE_DSS_WITH_AES_128_GCM_SHA256,TLS_DHE_RSA_WITH_AES_256_GCM_SHA384,TLS_DHE_DSS_WITH_AES_256_GCM_SHA384,TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_GCM_SHA256,TLS_RSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_CBC_SHA256,TLS_RSA_WITH_AES_256_CBC_SHA256,TLS_RSA_WITH_AES_128_CBC_SHA,TLS_RSA_WITH_AES_256_CBC_SHA,TLS_DHE_RSA_WITH_AES_128_CBC_SHA256,TLS_DHE_RSA_WITH_AES_256_CBC_SHA256,TLS_DHE_DSS_WITH_AES_128_CBC_SHA256,TLS_DHE_RSA_WITH_AES_128_CBC_SHA,TLS_DHE_DSS_WITH_AES_128_CBC_SHA,TLS_DHE_RSA_WITH_AES_256_CBC_SHA,TLS_DHE_DSS_WITH_AES_256_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDH_RSA_WITH_AES_128_CBC_SHA,TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDH_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDH_RSA_WITH_AES_256_CBC_SHA,TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.clientAuth=want
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyAlias=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStoreType=JKS
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStoreType=JKS
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyManagerAlgorithm=SunX509
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustManagerAlgorithm=PKIX
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStoreProvider=SUN
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStoreProvider=SUN
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStoreFile=/opt/nexus/etc/ssl/keystore.jks
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStorePassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyManagerPassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStoreFile=/opt/nexus/etc/ssl/truststore.jks
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStorePassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.protocol=TLSv1.2
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.ciphers=TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_DHE_DSS_WITH_AES_128_GCM_SHA256,TLS_DHE_RSA_WITH_AES_256_GCM_SHA384,TLS_DHE_DSS_WITH_AES_256_GCM_SHA384,TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_GCM_SHA256,TLS_RSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_CBC_SHA256,TLS_RSA_WITH_AES_256_CBC_SHA256,TLS_RSA_WITH_AES_128_CBC_SHA,TLS_RSA_WITH_AES_256_CBC_SHA,TLS_DHE_RSA_WITH_AES_128_CBC_SHA256,TLS_DHE_RSA_WITH_AES_256_CBC_SHA256,TLS_DHE_DSS_WITH_AES_128_CBC_SHA256,TLS_DHE_RSA_WITH_AES_128_CBC_SHA,TLS_DHE_DSS_WITH_AES_128_CBC_SHA,TLS_DHE_RSA_WITH_AES_256_CBC_SHA,TLS_DHE_DSS_WITH_AES_256_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDH_RSA_WITH_AES_128_CBC_SHA,TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDH_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDH_RSA_WITH_AES_256_CBC_SHA,TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.clientAuth=want
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyAlias=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStoreType=JKS
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStoreType=JKS
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyManagerAlgorithm=SunX509
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustManagerAlgorithm=PKIX
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStoreProvider=SUN
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStoreProvider=SUN
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStoreFile=/opt/nexus/etc/ssl/keystore.jks
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyStorePassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.keyManagerPassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStoreFile=/opt/nexus/etc/ssl/truststore.jks
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.trustStorePassword=nexus
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.protocol=TLSv1.2
Environment=RUN_JETTY_RUNNER=-Djetty.sslContextFactory.ciphers=TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_DHE_DSS_WITH_AES_128_GCM_SHA256,TLS_DHE_RSA_WITH_AES_256_GCM_SHA384,TLS_DHE_DSS_WITH_AES_256_GCM_SHA384,TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_GCM_SHA256,TLS_RSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_CBC_SHA256,TLS_RSA_WITH_AES_256_CBC_SHA256,TLS_RSA_WITH_AES_128_CBC_SHA,TLS_RSA_WITH_AES_256_CBC_SHA,TLS_DHE_RSA_WITH_AES_128_CBC_SHA256,TLS_DHE_RSA_WITH_AES_256_CBC_SHA256,TLS_DHE_DSS_WITH_AES_128_CBC_SHA256,TLS_DHE_RSA_WITH_AES_128_CBC_SHA,TLS_DHE_DSS_WITH_AES_128_CBC_SHA,TLS_DHE_RSA_WITH_AES_256_CBC_SHA,TLS_DHE_DSS_WITH_AES_256_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDH_RSA_WITH_AES_128_CBC_SHA,TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDH_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDH_RSA_WITH_AES_256_CBC_SHA,TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA
ExecStart=/opt/nexus/bin/nexus start
ExecStop=/opt/nexus/bin/nexus stop
Restart=on-failure
User=nexus
Group=nexus

[Install]
WantedBy=multi-user.target
```

Reload the systemd daemon and start the Nexus service:

```bash
sudo systemctl daemon-reload
sudo systemctl start nexus
sudo systemctl enable nexus
```

Check the status of the Nexus service:

```bash
sudo systemctl status nexus
```

### Accessing Nexus

Once Nexus is running, you can access it via a web browser at `http://<your-server-ip>:8081`. The default username and password are `admin` and `admin123`.

---
<!-- nav -->
[[07-Realistic Scenarios and Best Practices|Realistic Scenarios and Best Practices]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/00-Overview|Overview]] | [[09-Talking to Nexus REST API|Talking to Nexus REST API]]
