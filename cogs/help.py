from discord.ext import commands
from discord.ext.commands import Group, Command
import discord


class Help(commands.Cog):

    def __init__(self, bot):
        """Init method."""
        self.bot = bot
        super().__init__()

    @commands.command(name='help',
                      description='The help command!',
                      aliases=['commands', 'command'],
                      usage='cog')
    async def help_command(self, ctx, *args):
        """
        Main control flow logic for the help command
        """
        if len(args) == 0:
            # No command/cog passed in so print all help items
            await self.send_base_help(ctx)

        entity = args[0]
        if entity is None:
            return None

        if isinstance(entity, str):
            entity = self.bot.get_cog(entity) or self.bot.get_command(entity)

        try:
            qualified_name = entity.qualified_name
        except AttributeError:
            # if we're here then it's not a cog, group, or command.
            return None

        try:
            if hasattr(entity, '__cog_commands__'):
                await self.send_cog_help(ctx, args[0])
            elif isinstance(entity, Group):
                # TODO: Implement Group Help Command
                await ctx.send(f'Group: {qualified_name}')
            elif isinstance(entity, Command):
                # TODO: Implement Basic Help Command:
                await ctx.send(f'Command: {qualified_name}')
            else:
                return None
        except Exception as e:
            await ctx.send(e)

    async def send_base_help(self, ctx):
        try:
            help_embed = discord.Embed(
                title='Help',
                type='rich',
                description=f'Use `{ctx.prefix}{ctx.invoked_with} '
                            f'[command]` for more info on a command.\n'
            )
            help_embed.set_footer(
                text=f'Requested by {ctx.message.author.name} | '
                     f'yinbot v{self.bot.version}{self.bot.commit}',
                icon_url=self.bot.user.avatar_url
            )

            # Get a list of all cogs
            cogs = [c for c in self.bot.cogs.keys()]
            for cog in cogs:
                # Get a list of all commands under each cog

                cog_commands = self.bot.get_cog(cog).get_commands()
                commands_list = ''
                for command in cog_commands:
                    name = command.name + ':'
                    commands_list += f'> **{name}** {command.short_doc}\n'
                if not commands_list:
                    commands_list += '`No commands found in this cog`'
                help_embed.add_field(
                    name=cog,
                    value=commands_list,
                    inline=False,
                )
            await ctx.send(embed=help_embed)
        except Exception as e:
            await ctx.send(e)

    async def send_cog_help(self, ctx, cog):
        """
        Send the help embed, but limited to a single cog
        """
        try:
            help_embed = discord.Embed(
                title='Yinbot Help',
                type='rich',
                description=f'Use `{ctx.prefix}{ctx.invoked_with} '
                            f'[command]` for more info on a command.\n'
            )
            help_embed.set_footer(
                text=f'Requested by {ctx.message.author.name} | '
                     f'yinbot v{self.bot.version}{self.bot.commit}',
                icon_url=self.bot.user.avatar_url
            )

            cog_commands = self.bot.get_cog(cog).get_commands()
            commands_list = ''
            for command in cog_commands:
                name = command.name + ':'
                commands_list += f'> **{name}** {command.short_doc}\n'
            if not commands_list:
                commands_list += '`No commands found in this cog`'
            help_embed.add_field(
                name=cog,
                value=commands_list,
                inline=False,
            )
            await ctx.send(embed=help_embed)
        except Exception as e:
            await ctx.send(e)
