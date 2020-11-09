# Tryton Admin Bot
This is an official Discord bot for Tryton.
## Features
- Create new users accounts with SFTP and SQL access
- Password reset for existing accounts
- Delete users accounts
- Check which Discord user owns which account on Tryton and vice-versa
## Requirements
- Superuser permissions
- Python3
- NGINX
- PHP-FPM
- MariaDB
## Installation
We recommend to install this bot as a `systemd` service.
1. Create new bot on the [Discord Developer Platform](https://discord.com/developers/applications).
2. Create `systemd` unit file and set up Your bot token:
```
[Unit]
Description=Admin bot service.

[Service]
Environment="DISCORD_TOKEN=YOUR_TOKEN_HERE"
WorkingDirectory=/srv/admin-bot/
ExecStart=/usr/bin/python3 /srv/admin-bot/bot.py

[Install]
WantedBy=multi-user.target
```
3. Copy this file to `/lib/systemd/system/`
4. Clone this repo and put it in `/srv/admin-bot/`
5. Run the bot using `sudo systemctl start adminbot` command.
## Configuration
Bot configuration can be done using the `conf.json` file.
### phpapi - API for managing PHP-FPM pools
- service - Name of PHP-FPM service running on the server
- conf_dir - Directory of PHP-FPM config file to use
- template - Template used for creating new PHP-FPM config file
### dbapi - API for managing databases
- sock - Socket which can be used to connect to the database
- host - Hostname or address of the database
### userapi - API for managing users
- base_dir - Directory for users' subdirectiories
- user_group - Group to which all users are to be assigned
- samplequota - Disk quota profile for all users
- admins - Array of Discord ID's of server administrators.
### passgen - password generator
- wordsfile - Dictionary of words used in passwords
- word_length - Minimum and maximum length of words in passwords
- extra_chars - Additional characters used in passwords
- word_count - Minimum and maximum passwords word count
- extra_chars_count - Minimum and maximum number of extra characters in passwords
- uppercase_prob - Probability of uppercase letter in passwords
- force_length - Maximum length for all passwords