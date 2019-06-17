# User Warnings
Yin has a warning system based on both mod-given warnings as well as modactions taken

## Warnings
### Viewing Warnings
**Base Command**: `warnings <user> (<recent>)`

**Usage**: This will return all of a users warnings in the last 6 months, as well as modactions. If you pass in `false` to the `<recent>` variable it will show ALL warnings/modactions for a user

**Notes**

 - The `<user>` part of the command can be either a mention, an id, or a manual mention `<@id>`

<img src="../../images/Warnings/warnings.png"/> 

### Adding a Warning
**Base Command**: `warn major <user> <reason> | warn minor <user> <reason>`

**Usage**: This will add a warning to the user for this server. Minor/Major is just an internal measure.

**Notes**

 - The `<user>` part of the command can be either a mention, an id, or a manual mention `<@id>`

<img src="../../images/Warnings/warn_minor.png"/> 

### Editing a Warning
**Base Command**: `warn edit <user> <index> <major/minor> <reason>`

**Usage**: This will edit the warning at index `<index>` to a new level or with a new reason

**Notes**

 - The `<user>` part of the command can be either a mention, an id, or a manual mention `<@id>`

<img src="../../images/Warnings/warn_edit.png"/> 
