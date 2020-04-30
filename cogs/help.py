from discord.ext import commands
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
    async def help_command(self, ctx, cog='all'):
        try:
            help_embed = discord.Embed(title='Help', type='rich')
            help_embed.set_footer(
                text=f'Requested by {ctx.message.author.name}',
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
                    commands_list += '\u200b'
                help_embed.add_field(
                    name=cog,
                    value=commands_list,
                    inline=False,
                )
            await ctx.send(embed=help_embed)
        except Exception as e:
            await ctx.send(e)
