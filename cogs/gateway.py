"""
This cog will be used for setting up both the welcome message for each
guild as well as the gateway channel/role
"""

import discord
from discord.ext import commands
from .utils import checks


class Gateway(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Actually handles printing the welcome message
        """
        welcome_channels = await \
            self.bot.pg_utils.get_welcome_channels(
                member.guild.id, self.bot.logger)
        welcome_message = await \
            self.bot.pg_utils.get_welcome_message(
                member.guild.id, self.bot.logger)
        for ch_id in welcome_channels:
            channel = self.bot.get_channel(ch_id)
            await channel.send(welcome_message.replace(
                f'%user%', member.mention))

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def welcome(self, ctx):
        """
        Welcome message command. If no subcommand is
        invoked, it will return the current welcome message
        """
        welcome_msg = await self.bot.pg_utils.get_welcome_message(
            ctx.guild.id,
            self.bot.logger
        )
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current welcome message: ',
                description=welcome_msg
            )
            await ctx.send(embed=local_embed)

    @welcome.command(name='set')
    async def setwelcome(self, ctx, *, welcome_string):
        """
        Attempts to set welcome message to string passed in
        """
        if not welcome_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_welcome_message(
            ctx.guild.id,
            welcome_string,
            self.bot.logger
        )
        if success:
            desc = welcome_string.replace(
                f'%user%', ctx.message.author.mention)
            local_embed = discord.Embed(
                title=f'Welcome message set:',
                description=f'**Preview:**\n{desc} ',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error occured, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)
        return

    @welcome.command(aliases=['on'])
    async def enable(self, ctx):
        """
        Enables the welcome message in this channel
        """
        success = await self.bot.pg_utils.add_welcome_channel(
            ctx.guild.id, ctx.message.channel.id, self.bot.logger
        )
        if success:
            local_embed = discord.Embed(
                title=f'Channel Added:',
                description=f'{ctx.message.channel.name} '
                'was added to welcome list.',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)

    @welcome.command(aliases=['off'])
    async def disable(self, ctx):
        """
        Enables the welcome message in this channel
        """
        try:
            success = await self.bot.pg_utils.rem_welcome_channel(
                ctx.guild.id, ctx.message.channel.id, self.bot.logger
            )
        except ValueError:
            local_embed = discord.Embed(
                title=f'This channel is already not'
                'in the welcome channel list',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        if success:
            local_embed = discord.Embed(
                title=f'Channel removed:',
                description=f'{ctx.message.channel.name} '
                'was removed from welcome list.',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)


def setup(bot):
    bot.add_cog(Gateway(bot))
