---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating the Backup Process

To ensure the backup process runs automatically every day, we can use a scheduling tool like `cron` on Linux or Task Scheduler on Windows.

### Using Cron on Linux

1. **Edit the crontab File**:
    ```bash
    crontab -e
    ```
2. **Add a Cron Job**:
    ```bash
    0 2 * * * /usr/bin/python /path/to/backup_ec2.py >> /path/to/logfile.log 2>&1
    ```
    This cron job runs the script every day at 2:00 AM.

### Using Task Scheduler on Windows

1. **Open Task Scheduler**.
2. **Create a Basic Task**:
    - Name the task (e.g., `EC2 Backup`).
    - Set the trigger to daily at a specific time.
    - Set the action to start a program, pointing to the Python executable and the script path.
3. **Save and Run the Task**.

---
<!-- nav -->
[[04-Automating EC2 Instance Backups with Python|Automating EC2 Instance Backups with Python]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/06-How to Prevent  Defend|How to Prevent  Defend]]
