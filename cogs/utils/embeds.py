"""
This class will contain all the embeds used for at the very least
the mod log
"""

import discord
import datetime

NEGATIVECOLOR = 0x651111
POSITIVECOLOR = 0x419400
DELETEDCOLOR = 0x3399CC
EDITEDCOLOR = 0x00E4C9
USEREDITCOLOR = 0xe9e6c2
ROLECOLOR = 0x800080


class KickEmbed(discord.Embed):
    """
    Embed for when a user has been kicked
    """
    def __init__(self, kicked_user: discord.Member,
                 resp_mod: discord.Member, reason: str):
        """
        Init class for embed
        """
        local_title = f'{kicked_user.name} was kicked by {resp_mod}'
        local_desc = f'Reason: {reason}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class BanEmbed(discord.Embed):
    """
    Embed for when a user has been kicked
    """
    def __init__(self, banned_user: discord.Member,
                 resp_mod: discord.Member, reason: str):
        """
        Init class for embed
        """
        local_title = f'{banned_user.name} was banned by {resp_mod}'
        local_desc = f'Reason: {reason}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class JoinEmbed(discord.Embed):
    """
    Embed for when a user joins the server
    """
    def __init__(self, joining_user: discord.Member):
        """
        Init class for embed
        """
        local_title = f'User joined'
        local_desc = f'{joining_user.name}#{joining_user.discriminator}'\
                     f' | {joining_user.id}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class LeaveEmbed(discord.Embed):
    """
    Embed for when a user joins the server
    """
    def __init__(self, leaving_user: discord.Member):
        """
        Init class for embed
        """
        local_title = f'User left'
        local_desc = f'{leaving_user.name}#{leaving_user.discriminator}'\
                     f' | {leaving_user.id}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class UsernameUpdateEmbed(discord.Embed):
    """
    Embed for when a user edits their profile
    """
    def __init__(self, updated_user: discord.Member,
                 old_name: str, new_name: str):
        """
        Init class for embed
        """
        local_title = f'Username changed'
        local_desc = f'{updated_user.name}#{updated_user.discriminator}'\
                     f' | {updated_user.id}'\
                     f'\n**From**: {old_name} **To**: {new_name}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=USEREDITCOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class RoleAddEmbed(discord.Embed):
    """
    Embed for when a user's role is updated
    """
    def __init__(self, updated_user: discord.Member,
                 role_name: str):
        """
        Init class for embed
        """
        local_title = f'Role Added'
        local_desc = f'{updated_user.name}#{updated_user.discriminator}'\
                     f' | {updated_user.id}\n'\
                     f'*{role_name}*'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=ROLECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class RoleRemoveEmbed(discord.Embed):
    """
    Embed for when a user's role is updated
    """
    def __init__(self, updated_user: discord.Member,
                 role_name: str):
        """
        Init class for embed
        """
        local_title = f'Role Removed'
        local_desc = f'{updated_user.name}#{updated_user.discriminator}'\
                     f' | {updated_user.id}\n'\
                     f'*{role_name}*'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=ROLECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class MessageEditEmbed(discord.Embed):
    """
    Embed for when a user updates their message
    """
    def __init__(self, message_user: discord.Member,
                 channel_name, old_message, new_message):
        """
        Init class for embed
        """
        local_title = f'Message updated in {channel_name}'
        local_desc = f'{message_user.name}#{message_user.discriminator}'\
                     f' | {message_user.id}\n'\
                     f'**Old message**:\n{old_message}\n'\
                     f'**New message**:\n{new_message}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=EDITEDCOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))


class MessageDeleteEmbed(discord.Embed):
    """
    Embed for when a user updates their message
    """
    def __init__(self, message_user: discord.Member,
                 channel_name, old_message):
        """
        Init class for embed
        """
        local_title = f'Message deleted in {channel_name}'
        local_desc = f'{message_user.name}#{message_user.discriminator}'\
                     f' | {message_user.id}\n'\
                     f'\n{old_message}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=DELETEDCOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))
