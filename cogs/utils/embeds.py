"""
This class will contain all the embeds used for at the very least
the mod log
"""

import discord
import datetime

NEGATIVECOLOR = 0x651111


class KickEmbed(discord.Embed):
    """
    Embed for when a user has been kicked
    """
    def __init__(self, kicked_user: discord.Member,
                 resp_mod: discord.Member, reason: str):
        """
        Init class for embed
        """
        local_title = f'{kicked_user.name} was kicked by {resp_mod.name}'
        local_desc = f'Reason: {reason}'
        current_time = datetime.utcnow()
        local_footer = current_time.strptime('%A, %b %d %H:%M')
        super.__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            footer=local_footer)
