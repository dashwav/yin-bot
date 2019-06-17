# Role Management

### Assignable Roles
**Base Command**: `assignableroles | ar`

**Usage**: This sets up and manages the assignable roles that will get added to a user when they use the IAM commands. If you use just the base command with no subcommands, it will print out the current assignable roles

<img src="../../images/Roles/ar_base.png"/> 

#### Add/Remove
**Command**: `ar add <rolename>` | `ar remove <rolename>`

**Usage**: This will add/remove a role from the assignable roles list if found

<img src="../../images/Roles/ar_add.png"/> 
<img src="../../images/Roles/ar_rem.png"/> 

#### iam/iamnot
**Command**: `iam <rolename>` | `iamnot <rolename>`

**Usage**: This will add/remove a role to the user invoking the command

<img src="../../images/Roles/ar_iam.png"/> 
<img src="../../images/Roles/ar_iamnot.png"/> 

### Auto Assignable Roles
**Base Command**: `autoassignroles | aar`

**Usage**: This sets up and manages the auto-assignable roles that will get added to a user when first join the guild. If you use just the base command with no subcommands, it will print out the current auto-assignable roles

<img src="../../images/Roles/aar_base.png"/> 

#### Add/Remove
**Command**: `aar add <rolename>` | `aar remove <rolename>`

**Usage**: This will add/remove a role from the auto-assignable roles list if found

<img src="../../images/Roles/aar_add.png"/> 
<img src="../../images/Roles/aar_rem.png"/> 