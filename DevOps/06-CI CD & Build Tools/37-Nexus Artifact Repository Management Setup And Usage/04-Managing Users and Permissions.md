---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Managing Users and Permissions

### User Management

Nexus allows you to manage users and their permissions. This ensures that only authorized individuals can access and modify artifacts.

#### Creating a New User

To create a new user, log in to Nexus and navigate to **Security > Users**. Click on **Create User** and fill in the required details:

- **Username**
- **First Name**
- **Last Name**
- **Email Address**
- **Password**

Click **Save** to create the user.

#### Assigning Roles

Users can be assigned roles to define their permissions. Navigate to **Security > Roles** and select the role you want to assign. Then, go to **Security > Users** and click on the user you created. Under **Roles**, select the desired role and click **Save**.

### Role-Based Access Control (RBAC)

RBAC is a method of controlling access to artifacts based on roles. Nexus supports predefined roles such as:

- **Admin**: Full administrative access.
- **Deployer**: Can deploy artifacts but cannot manage users or settings.
- **Viewer**: Can view artifacts but cannot deploy or manage them.

### Example Scenario

Suppose you have a team of developers and a separate team of administrators. You can create roles for each team and assign them accordingly:

- **Developer Role**: Allows deploying artifacts but not managing users or settings.
- **Admin Role**: Allows full administrative access.

This ensures that developers can deploy artifacts without having unnecessary administrative privileges.

---
<!-- nav -->
[[04-Difference Between Components and Assets|Difference Between Components and Assets]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/00-Overview|Overview]] | [[06-Publishing Artifacts to Nexus|Publishing Artifacts to Nexus]]
