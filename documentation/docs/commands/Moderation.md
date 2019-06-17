# Moderation

## Kicking and Banning

When a user is kicked/banned from your server, Yin will attempt to send them a message notifying them about the action.

<img src="../../images/Moderation/kick_notification.png"/> 

You can change the footer of the message with the next two commands:

### Footer
**Base Command**: `footer`

**Usage**: This will edit the last line that gets added to the kick/ban notification message. Using the base command by itself prints the current footers for both ban and kick notifications.

<img src="../../images/Moderation/footer_base.png"/>

#### Setting Kick/Ban footer
**Command**: `footer set_kick <new footer> | footer set_ban <new footer>`

**Usage**: This will change either the kick or ban notification footer.

<img src="../../images/Moderation/footer_kick.png"/>

And the result:

<img src="../../images/Moderation/kick_notificationv2.png"/>

### Kicking
**Command**: `kick <user> <reason>`

**Usage**: This will remove a user from your guild, with the ability for them to join back

**Notes**

 - The `<user>` part of the command can be either a mention, an id, or a manual mention `<@id>`
 - You will have 10 seconds to type `confirm` in order to kick the user
 - While there is no limit on how long a reason can be - only 500 chars will be added to audit log

<img src="../../images/Moderation/kick.png"/> 

### Banning
**Base Command**: `ban <user> <reason>`

**Usage**: This will remove a user from your guild permanently

**Notes**

 - The `<user>` part of the command can be either a mention, an id, or a manual mention `<@id>`
 - You will have 10 seconds to type `confirm` in order to ban the user
 - While there is no limit on how long a reason can be - only 500 chars will be added to audit log

<img src="../../images/Moderation/ban.png"/> 

### Un-Banning
**Base Command**: `unban <user> <reason>`

**Usage**: This will unban a previously banned user from your guild

**Notes**

 - The `<user>` part of the command can be either a mention, an id, or a manual mention `<@id>`
 - You will have 10 seconds to type `confirm` in order to ban the user
 - While there is no limit on how long a reason can be - only 500 chars will be added to audit log

<img src="../../images/Moderation/unban.png"/> 

### Mass Message Deletion
**Command**: `purge (<number of messages>) (<user to focus>)`

**Usage**: This will remove the number of specified messages from a channel. You can add a user to only remove messages from that user.

**Notes**

 - The default amount of messages to purge is 100
