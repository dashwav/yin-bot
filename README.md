# Yin-bot
General purpose discord bot written in python for the discord.py rewrite library

# Invite
[Click here](https://discordapp.com/oauth2/authorize?client_id=369362004458078208&scope=bot&permissions=268528894) to invite Yin-bot to your server

# Support
[Click here](https://discordapp.com/invite/svU3Mdd) to join the discord support server

# Development

Development with Yin is a very simple process.

Requirements:
```
Docker (CE edition is fine)
```

Steps to run:

* Clone repo (duh)
* Copy config/example_config.yml to config/config.yml and edit values as needed.
* Run `docker-compose up`
* Invite bot to server.

Once you have changed some code:

* Run `docker-compose build yinbot`
* Re-run `docker-compose up`

## Common Issues:

### Bot doesn't connect to db on first run

Don't worry this happens because both the bot and the DB are being built at the same time and they finish at different times.

 - This should resolve itself, the bot will attempt to reconnect every 5 seconds. If it goes on longer than 3 retries, check to see if database perms are set correctly or the database is up correctly


### Database is all out of wack

This may happen due to the database being on a volume to persist the data. If this happens you can run `docker system prune --volumes`

- This will require you to restore the server permissions/settings. (See 'Server Settings Deleted/Error Logs on Every Command')

### Server Settings Deleted/Error Logs on Every Command

Run `{prefix}auto_fix_servers`. This will go through and add any servers the bot is in to the database, if they are not already there.