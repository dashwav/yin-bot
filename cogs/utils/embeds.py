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
        local_title = f'{kicked_user} was kicked by {resp_mod}'
        local_desc = f'Reason: {reason}'
        current_time = datetime.datetime.utcnow()
        super().__init__(
            color=NEGATIVECOLOR,
            title=local_title,
            description=local_desc,
            )
        self.set_footer(text=current_time.strftime('%A, %b %d %H:%M'))
