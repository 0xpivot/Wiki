---
course: DevSecOps
topic: Improving Your Incident Response Capability
tags: [devsecops]
---

## Metrics for Incident Response Capability

### Introduction to Incident Response Metrics

Incident response is a critical component of any organization's cybersecurity strategy. Effective incident response involves detecting, analyzing, containing, and recovering from security incidents as quickly and efficiently as possible. To measure and improve the effectiveness of incident response, organizations use various metrics. These metrics provide insights into the performance of the incident response process and help identify areas for improvement.

In this section, we will explore several key metrics used in incident response:

- **Mean Time to Detection (MTTD)**
- **Mean Time to Respond/Recover/Remediate (MTTR)**
- **Dwell Time**
- **Containment Time**

Each of these metrics serves a specific purpose and provides valuable information about the incident response process. Understanding and tracking these metrics can significantly enhance an organization's ability to manage and mitigate security incidents effectively.

### Mean Time to Detection (MTTD)

**Definition:** Mean Time to Detection (MTTD) is the average time it takes to detect an incident after it occurs. This metric is crucial because the sooner an incident is detected, the faster it can be contained and mitigated, reducing potential damage.

#### Why MTTD Matters

- **Reducing Damage:** Early detection minimizes the time an attacker has to exploit vulnerabilities, thereby reducing the potential damage.
- **Improving Response Time:** A shorter MTTD allows for quicker response times, which can be critical in preventing further harm.
- **Enhancing Reputation:** Quick detection and response can help maintain an organization’s reputation by demonstrating a proactive approach to security.

#### How MTTD Works Under the Hood

To calculate MTTD, you need to track the time from when an incident occurs to when it is first detected. This can be done using various tools and techniques, such as:

- **Security Information and Event Management (SIEM) Systems:** SIEM systems collect and analyze log data from various sources to detect anomalies and potential security incidents.
- **Network Monitoring Tools:** Tools like Snort or Suricata can monitor network traffic for suspicious activity.
- **Endpoint Detection and Response (EDR) Solutions:** EDR solutions provide visibility into endpoint activities and can detect malicious behavior.

#### Real-World Example: Recent Breach

Consider the **SolarWinds breach** (CVE-2020-1014), where attackers exploited a vulnerability in SolarWinds’ Orion software. The breach went undetected for months, highlighting the importance of reducing MTTD. Had SolarWinds had a more robust detection mechanism in place, the breach could have been identified earlier, potentially limiting the scope of the attack.

#### Code Example: SIEM Configuration

Here is an example of configuring a SIEM system to detect unusual login patterns:

```json
{
  "rule": {
    "name": "Unusual Login Activity",
    "description": "Detects unusual login activity across multiple endpoints.",
    "condition": "login_count > 10 AND unique_ips > 5",
    "actions": [
      {
        "type": "alert",
        "message": "Unusual login activity detected."
      }
    ]
  }
}
```

This configuration sets up a rule to alert when there are more than 10 login attempts from more than 5 unique IP addresses within a short timeframe.

#### How to Prevent / Defend

**Detection:**
- Implement robust logging and monitoring across all systems.
- Use SIEM systems to correlate logs and detect anomalies.
- Regularly review and update detection rules based on new threats.

**Prevention:**
- Harden systems against common attack vectors.
- Educate employees on recognizing and reporting suspicious activity.
- Conduct regular security audits and penetration testing.

### Mean Time to Respond/Recover/Remediate (MTTR)

**Definition:** Mean Time to Respond/Recover/Remediate (MTTR) is the average time it takes to respond to, recover from, or remediate a security incident. The exact definition can vary depending on the organization, but generally, it encompasses the entire process from initial detection to full recovery.

#### Why MTTR Matters

- **Minimizing Downtime:** A shorter MTTR reduces the amount of time systems are unavailable, minimizing business disruption.
- **Reducing Costs:** Faster response and recovery can reduce the financial impact of an incident.
- **Improving Customer Trust:** Quick and effective incident resolution helps maintain customer trust and confidence.

#### How MTTR Works Under the Hood

To calculate MTTR, you need to track the time from when an incident is detected to when it is fully resolved. This involves several steps:

1. **Initial Response:** Containing the incident to prevent further damage.
2. **Analysis:** Investigating the root cause of the incident.
3. **Recovery:** Restoring affected systems and data.
4. **Remediation:** Implementing measures to prevent similar incidents in the future.

#### Real-World Example: Recent Breach

The **Equifax breach** (CVE-2017-5638) is a notable example where a prolonged MTTR contributed to significant damage. The breach was detected in July 2017, but Equifax did not publicly disclose it until September 2017, leading to widespread criticism and financial losses.

#### Code Example: Incident Response Playbook

Here is an example of an incident response playbook:

```yaml
incident_response_playbook:
  - name: Initial Response
    steps:
      - isolate_affected_systems
      - notify_incident_response_team
      - gather_initial_logs
  - name: Analysis
    steps:
      - identify_root_cause
      - assess_impact
  - name: Recovery
    steps:
      - restore_systems_from_backup
      - validate_data_integrity
  - name: Remediation
    steps:
      - patch_vulnerabilities
      - implement_additional_security_measures
```

This playbook outlines the steps involved in responding to an incident, from initial containment to final remediation.

#### How to Prevent / Defend

**Detection:**
- Establish clear incident response protocols.
- Train staff on incident response procedures.
- Use automated tools to assist in the response process.

**Prevention:**
- Regularly update and patch systems to address known vulnerabilities.
- Conduct regular security training and awareness programs.
- Implement multi-factor authentication (MFA) to enhance security.

### Dwell Time

**Definition:** Dwell Time is the duration between the initial intrusion and the detection or remediation of the incident. This metric is particularly important in security contexts because it reflects the time an attacker has to operate undetected.

#### Why Dwell Time Matters

- **Minimizing Attack Window:** Reducing dwell time limits the window during which an attacker can exploit vulnerabilities.
- **Improving Detection Mechanisms:** Shorter dwell times indicate more effective detection mechanisms.
- **Enhancing Security Posture:** By reducing dwell time, organizations can demonstrate a stronger security posture.

#### How Dwell Time Works Under the Hood

To calculate dwell time, you need to track the time from when an intrusion occurs to when it is detected or remediated. This involves:

- **Intrusion Detection:** Using tools and techniques to detect unauthorized access.
- **Incident Response:** Quickly responding to detected intrusions to minimize damage.

#### Real-World Example: Recent Breach

The **Capital One breach** (CVE-2019-11510) is an example where dwell time played a significant role. The breach occurred in March 2019, but it was not detected until July 2019, highlighting the importance of reducing dwell time.

#### Code Example: Intrusion Detection System (IDS)

Here is an example of configuring an IDS to detect unauthorized access:

```json
{
  "rule": {
    "name": "Unauthorized Access",
    "description": "Detects unauthorized access attempts.",
    "condition": "failed_login_attempts > 5 AND user_is_not_admin",
    "actions": [
      {
        "type": "alert",
        "message": "Unauthorized access attempt detected."
      }
    ]
  }
}
```

This configuration sets up a rule to alert when there are more than 5 failed login attempts from a non-admin user.

#### How to Prevent / Defend

**Detection:**
- Implement robust intrusion detection systems.
- Monitor network traffic for signs of unauthorized access.
- Regularly review and update detection rules based on new threats.

**Prevention:**
- Harden systems against common attack vectors.
- Implement strong authentication mechanisms.
- Conduct regular security audits and penetration testing.

### Containment Time

**Definition:** Containment Time is the duration it takes to contain an incident once it is detected. This metric is crucial because it reflects the speed at which an organization can limit the spread of an incident.

#### Why Containment Time Matters

- **Limiting Spread:** Quick containment prevents the incident from spreading to other parts of the network.
- **Reducing Damage:** Faster containment reduces the potential damage caused by the incident.
- **Improving Response Efficiency:** Shorter containment times indicate more efficient incident response processes.

#### How Containment Time Works Under the Hood

To calculate containment time, you need to track the time from when an incident is detected to when it is fully contained. This involves:

- **Isolation:** Isolating affected systems to prevent further spread.
- **Analysis:** Analyzing the incident to understand its scope and impact.
- **Containment:** Implementing measures to contain the incident.

#### Real-World Example: Recent Breach

The **Marriott breach** (CVE-2018-12609) is an example where containment time played a significant role. The breach was detected in September 2018, and Marriott took immediate action to contain the incident, demonstrating the importance of quick containment.

#### Code Example: Incident Containment Script

Here is an example of a script to contain an incident:

```bash
#!/bin/bash

# Isolate affected systems
echo "Isolating affected systems..."
iptables -A INPUT -s <affected_ip> -j DROP

# Notify incident response team
echo "Notifying incident response team..."
curl -X POST -H "Content-Type: application/json" -d '{"message": "Incident detected. Affected systems isolated."}' https://<incident_response_url>

# Gather initial logs
echo "Gathering initial logs..."
tar -czvf /var/log/incident_logs.tar.gz /var/log/*
```

This script isolates affected systems, notifies the incident response team, and gathers initial logs for analysis.

#### How to Prevent / Defend

**Detection:**
- Establish clear containment procedures.
- Train staff on containment protocols.
- Use automated tools to assist in the containment process.

**Prevention:**
- Regularly update and patch systems to address known vulnerabilities.
- Conduct regular security training and awareness programs.
- Implement multi-factor authentication (MFA) to enhance security.

### Conclusion

Metrics such as MTTD, MTTR, dwell time, and containment time are essential for measuring and improving incident response capabilities. By tracking these metrics, organizations can gain valuable insights into their incident response performance and identify areas for improvement. Implementing robust detection, response, and containment mechanisms can significantly enhance an organization's ability to manage and mitigate security incidents effectively.

### Practice Labs

For hands-on practice with incident response metrics, consider the following well-known labs:

- **PortSwigger Web Security Academy:** Offers interactive labs to practice detecting and responding to web-based security incidents.
- **OWASP Juice Shop:** Provides a vulnerable web application to practice identifying and responding to security incidents.
- **DVWA (Damn Vulnerable Web Application):** A deliberately insecure web application for practicing web application security.

These labs provide practical experience in applying the concepts discussed in this chapter, helping to reinforce learning and improve incident response skills.

---
<!-- nav -->
[[01-Introduction to Incident Response Metrics|Introduction to Incident Response Metrics]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/02-Metrics/00-Overview|Overview]] | [[03-Understanding Dwell Time and Its Variants|Understanding Dwell Time and Its Variants]]
