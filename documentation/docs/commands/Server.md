# Server Management

### Invite Deletion
**Base Command**: `invites`

**Usage**: This command allows for automatic deletion of discord invites in your server. Using just the base command will respond with the current status of invite deletion.

 <img src="../../images/Server/invites_base.png"/> 

#### Enable/Disable
**Base Command**: `invites <enable|allow> | invites <disable|disallow>`

**Usage**: Disabling invites will cause yin to delete any discord invite posted in your channel. 

**Notes**

 - Users with the `manage_messages` permission will not have their invites deleted.

 <img src="../../images/Server/invites_allow.png"/>

### Server Welcome Message
**Base Command**: `welcome`

**Usage**: This command will set up a message that yin will send to any user that joins the server. Using just the base command will respond with the current welcome message.

 <img src="../../images/Server/welcome_base.png"/> 

#### Set Message
**Base Command**: `welcome set <new message>`

**Usage**: This will update the current welcome message with the one passed in.

**Notes**:

 - If you wish for Yin to mention the user, add the string `%user%` in the message.

 <img src="../../images/Server/welcome_set.png"/> 

#### Enable/Disable
**Base Command**: `welcome enable | welcome disable`

**Usage**: This will either enable or disable the current channel from welcoming users

 <img src="../../images/Server/welcome_enable.png"/> 

## Logging

### Server Logs
This logging channel will serve as a log for all general purpose server logging

**Command**: `logging enable | logging disable`

**Usage**: This will either enable or disable logging to the current channel. Usage with just `logging` will print out current log channels

<img src="../../images/Server/server_logging.png"/>

### Modlog
This logging channel will post a message on each mod-action taken on the server.

**Command**: `modlog enable | modlog disable`

**Usage**: This will either enable or disable modlogs to the current channel. Usage with just `modlog` will print out current log channels

<img src="../../images/Server/mod_logging.png"/>