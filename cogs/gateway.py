"""Gateway for entry message and joining role/channel."""

import discord
from discord.ext import commands
from .utils import checks


class Gateway(commands.Cog):
    """Gateway Cog."""

    def __init__(self, bot):
        """Init method."""
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Actually handles printing the welcome message."""
        welcome_channels = await \
            self.bot.pg_utils.get_welcome_channels(
                member.guild.id, self.bot.logger)
        welcome_message = await \
            self.bot.pg_utils.get_welcome_message(
                member.guild.id, self.bot.logger)
        for ch_id in welcome_channels:
            channel = self.bot.get_channel(ch_id)
            await channel.send(welcome_message.replace(
                f'%user%', member.mention).replace(
                f'%server%', member.guild.name))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Actually handles printing the role greeting message."""
        if before.roles == after.roles:
            return
        role_diff = set(after.roles) - (set(before.roles))
        for role in role_diff:
            role_greetings = await \
                self.bot.pg_utils.get_role_greetings(
                    role.id, self.bot.logger)
            for role_greet in role_greetings:
                channel = self.bot.get_channel(role_greet["channel_id"])
                if not channel:
                    self.bot.logger.error("Channel removed")
                    continue
                await channel.send(role_greet['greeting'].replace(
                    f'%user%', after.mention).replace(
                    f'%server%', after.guild.name))

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def welcome(self, ctx):
        """Welcome message command."""
        """If no subcommand is
        invoked, it will return the current welcome message."""
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
    async def setwelcome(self, ctx, *, welcome_string: str=None):
        """Attempt to set welcome message to string passed in."""
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
                f'%user%', ctx.message.author.mention).replace(
                f'%server%', ctx.guild.name)
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
        """Enable the welcome message in this channel."""
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
        """Enable the welcome message in this channel."""
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


    @commands.group(aliases=["greetings"])
    @commands.guild_only()
    @checks.is_admin()
    async def greeting(self, ctx):
        """Role greeting command."""
        """If no subcommand is
        invoked, it will return the current role greetings."""
        if ctx.invoked_subcommand is None:
            role_greetings = await \
                self.bot.pg_utils.get_all_role_greetings(
                    ctx.guild.id, self.bot.logger)
            string = ""
            for role_greet in role_greetings:
                role = ctx.guild.get_role(role_greet['role_id'])
                channel = self.bot.get_channel(role_greet["channel_id"])
                if not channel or not role:
                    self.bot.logger.error("Channel/role removed")
                    continue
                string += f"Role: {role.mention} "
                string += f"- Channel: {channel.mention}\n"
            local_embed = discord.Embed(
                title=f'Current role_greetings: ',
                description=string
            )
            await ctx.send(embed=local_embed)


    @greeting.command(name='set')
    async def setgreeting(self, ctx, role: discord.Role , *, welcome_string: str=None):
        """Attempt to set role greeting message to string passed in."""
        if not welcome_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_role_greeting(
            ctx.guild.id,
            ctx.channel.id,
            role.id,
            welcome_string,
            self.bot.logger
        )
        if success:
            desc = welcome_string.replace(
                f'%user%', ctx.message.author.mention).replace(
                f'%server%', ctx.guild.name)
            local_embed = discord.Embed(
                title=f'Role greeting message set:',
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

    @greeting.command(name='remove', aliases=['rem'])
    async def remgreeting(self, ctx, role: discord.Role):
        """Attempt to set role greeting message to string passed in."""
        success = await self.bot.pg_utils.del_role_greeting(
            role.id,
            ctx.channel.id,
            self.bot.logger
        )
        if success:
            local_embed = discord.Embed(
                title=f'Role greeting message deleted from this channel',
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

    @greeting.command(name='get')
    async def getgreeting(self, ctx, role: discord.Role):
        """Attempt to set role greeting message to string passed in."""
        role_greeting = await self.bot.pg_utils.get_channel_role_greeting(
            role.id,
            ctx.channel.id,
            self.bot.logger
        )
        if not role_greeting:
            local_embed = discord.Embed(
                title=f'No role greetings in this channel',
                color=0x419400
            )
            await ctx.send(embed=local_embed)
            return
        local_embed = discord.Embed(
            title=f'Current role greeting: ',
            description=role_greeting["greeting"]
        )
        await ctx.send(embed=local_embed)

def setup(bot):
    """General cog loading."""
    bot.add_cog(Gateway(bot))
