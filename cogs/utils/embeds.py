"""
This class will contain all the embeds used for at the very least
the mod log
"""

import discord
import datetime

NEGATIVECOLOR = 0x651111
SLIGHTLYNEGATIVECOLOR = 0xF26E00
POSITIVECOLOR = 0x419400
DELETEDCOLOR = 0x3399CC
EDITEDCOLOR = 0x00E4C9
USEREDITCOLOR = 0xe9e6c2
ROLECOLOR = 0x800080

INVITE = 'https://discordapp.com/oauth2/authorize?'\
         'client_id=369362004458078208&scope=bot&permissions=268528894'

DISCORD = 'https://discordapp.com/invite/svU3Mdd'


def return_current_time():
    """
    Returns a string with the current time in it
    """
    time = datetime.datetime.utcnow()
    return time.strftime('%A, %b %d %H:%M')


class InternalErrorEmbed(discord.Embed):
    """
    Embed for when it isn't the users fault
    """
    def __init__(self):
        local_title = f'Internal error!'
        local_desc = f'Contact <@164546159140929538>'\
                     f' or [Click here]({DISCORD}) to join '\
                     f'<@369362004458078208>\'s support server!'
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc
        )
        self.set_footer(text=return_current_time())


class InviteEmbed(discord.Embed):
    """
    Embed that contains link to invite
    """
    def __init__(self):
        local_title = f'Invite link'
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=f'[Click here]({INVITE}) to invite '
                        f'<@369362004458078208> to your server!'
        )
        self.set_footer(text=return_current_time())


class SupportEmbed(discord.Embed):
    """
    Embed that contains link to invite
    """
    def __init__(self):
        local_title = f'Invite link'
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=f'[Click here]({DISCORD}) to join '
                        f'<@369362004458078208>\'s support server!'
        )
        self.set_footer(text=return_current_time())


class ForbiddenEmbed(discord.Embed):
    """
    Embed for when bot lacks permissions to do something
    """
    def __init__(self, action, required_perm=None):
        local_title = f'Insuffecient Permissions:'
        local_desc = f'Couldn\'t complete command: **{action}**'\
                     ' due to lack of permissions'
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc
        )
        self.set_footer(text=return_current_time())


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
        super().__init__(
            color=SLIGHTLYNEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class BanEmbed(discord.Embed):
    """
    Embed for when a user has been banned
    """
    def __init__(self, banned_user: discord.Member,
                 resp_mod: discord.Member, reason: str):
        """
        Init class for embed
        """
        local_title = f'{banned_user.name} was banned by {resp_mod}'
        local_desc = f'Reason: {reason}'
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class ModerationEmbed(discord.Embed):
    """
    Embed for when a user has been moderated in other ways
    """
    def __init__(self, moderated_user: discord.Member,
                 resp_mod: discord.Member, reason: str):
        """
        Init class for embed
        """
        local_title = f'{moderated_user.name} was moderated by {resp_mod}'
        local_desc = f'Reason: {reason}'
        super().__init__(
            color=SLIGHTLYNEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class LogBanEmbed(discord.Embed):
    """
    Embed for when a user joins the server
    """
    def __init__(self, leaving_user: discord.Member):
        """
        Init class for embed
        """
        local_title = f'User banned'
        local_desc = f'{leaving_user.name}#{leaving_user.discriminator}'\
                     f'\n\n{leaving_user.id}'
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class UnBanEmbed(discord.Embed):
    """
    Embed for when a user has been kicked
    """
    def __init__(self, unbanned_user: discord.Member,
                 resp_mod: discord.Member, reason: str):
        """
        Init class for embed
        """
        local_title = f'{unbanned_user.name} was unbanned by {resp_mod}'
        local_desc = f'Reason: {reason}'
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


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
                     f'\n\n{joining_user.id}'
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_thumbnail(url=joining_user.avatar_url)
        self.set_footer(text=return_current_time())


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
                     f'\n\n{leaving_user.id}'
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_thumbnail(url=leaving_user.avatar_url)
        self.set_footer(text=return_current_time())


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
        super().__init__(
            color=USEREDITCOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


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
        super().__init__(
            color=ROLECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


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
        super().__init__(
            color=ROLECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


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
        super().__init__(
            color=EDITEDCOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


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
        super().__init__(
            color=DELETEDCOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class SelfRoleAddedEmbed(discord.Embed):
    """
    Embed for when a user adds a self assignable role
    """
    def __init__(self, message_user, role_name):
        local_title = f'Role Added'
        local_desc = f'{message_user.mention}, you now have the '\
                     f'**{role_name}** role.'
        super().__init__(
            title=local_title,
            description=local_desc,
            color=POSITIVECOLOR
        )
        self.set_footer(text=return_current_time())


class SelfRoleRemovedEmbed(discord.Embed):
    """
    Embed for when a role is added
    """
    def __init__(self, message_user, role_name):
        local_title = f'Role Removed'
        local_desc = f'{message_user.mention}, you no longer have the '\
                     f'**{role_name}** role.'
        super().__init__(
            title=local_title,
            description=local_desc,
            color=POSITIVECOLOR
        )
        self.set_footer(text=return_current_time())


class SelfRoleNotAssignableEmbed(discord.Embed):
    """
    Embed for when a role can't be assigned
    """
    def __init__(self, role_name):
        local_title = f'Role Not Added'
        local_desc = f'**{role_name}** is not self-assignable'
        super().__init__(
            title=local_title,
            description=local_desc,
            color=NEGATIVECOLOR
        )
        self.set_footer(text=return_current_time())


class RoleNotFoundEmbed(discord.Embed):
    """
    Embed for not found role
    """
    def __init__(self, role_name):
        local_title = f' '
        local_desc = f'Couldn\'t find role **{role_name}**'
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class RoleDuplicateUserEmbed(discord.Embed):
    """
    Embed for already has role
    """
    def __init__(self, message_user, role_name):
        local_desc = f'{message_user.mention}, you already have the '\
                     f'**{role_name}** role'
        super().__init__(
            title='Role Not Added',
            description=local_desc,
            color=NEGATIVECOLOR
        )
        self.set_footer(text=return_current_time())


class RoleNotRemovedEmbed(discord.Embed):
    """
    Embed for when people already have no role
    """
    def __init__(self, message_user, role_name):
        local_desc = f'{message_user.mention}, you already don\'t'\
                     f' have the **{role_name}** role'
        super().__init__(
            title='Role Not Removed',
            description=local_desc,
            color=NEGATIVECOLOR
        )
        self.set_footer(text=return_current_time())


class VoiceChannelStateEmbed(discord.Embed):
    """
    Embed for voice channel update
    """
    def __init__(self, channel_user: discord.Member,
                 channel_name, action):
        """
        init class for embed
        """
        local_title = 'Presence Update'
        local_desc = f'**{channel_user.name}#{channel_user.discriminator}**'\
                     f' has {action} **{channel_name}**.'
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class VoiceChannelMoveEmbed(discord.Embed):
    """
    Embed for voice channel update
    """
    def __init__(self, channel_user: discord.Member,
                 before_channel, after_channel):
        """
        init class for embed
        """
        local_title = f'Presence update'
        local_desc = f'**{channel_user.name}#{channel_user.discriminator}**'\
                     f' has moved from **{before_channel}**'\
                     f' to **{after_channel}**.'
        super().__init__(
            color=POSITIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=return_current_time())


class WarningAddEmbed(discord.Embed):
    """
    Embed for when someone gets warned
    """
    def __init__(self, warned_user: discord.Member, major: bool,
                 reason: str, infraction_count: int):
        level = 'MAJOR' if major else 'MINOR'
        local_title = f'User Warned'
        local_desc = f'{warned_user.mention}'\
                     f' has been given a **{level}** warning for:\n'\
                     f'\'**{reason}**\''
        super().__init__(
            color=SLIGHTLYNEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(
            text=f'This is warning number {infraction_count+1}'
                 f' for {warned_user.name}')


class WarningListEmbed(discord.Embed):
    """
    Embed that lists all a users infractions
    """
    def __init__(self, warned_user: discord.Member, infractions: list, logger):

        local_title = f'**{warned_user.name}#{warned_user.discriminator}'\
                      f'**\'s infractions'
        local_desc = f'' if infractions else f'User has no warnings'
        warning_string = ''
        string_list = []
        for index, warning in enumerate(infractions):
            level = 'MAJOR' if warning['major'] else 'MINOR'
            date = warning['logtime'].strftime('%b %d %Y %H:%M')
            tmp_warning_string = f'**{index+1}.** ({level})'\
                                 f' {warning["reason"]} '\
                                 f'[{date}]\n'
            if len(tmp_warning_string) + len(warning_string) > 1000:
                string_list.append(warning_string)
                warning_string = tmp_warning_string
            warning_string += tmp_warning_string
        string_list.append(warning_string)
        super().__init__(
            color=SLIGHTLYNEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        if string_list[0] != '':
            for index, string in enumerate(string_list):
                if index == 0:
                    self.add_field(
                        name='Infractions:',
                        value=string
                    )
                else:
                    self.add_field(
                            name='Infractions:(cont)',
                            value=string
                        )
        self.set_footer(text=return_current_time())
