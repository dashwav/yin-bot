"""
This cog will create messages that will manage channel perms with reacts.
"""
import discord
import datetime
from asyncpg.exceptions import UniqueViolationError
from collections import defaultdict
from .utils import helpers, checks
from discord.ext import commands


class Channels():
    """
    """

    def __init__(self, bot):
        super().__init__()
        self.reaction_emojis = [ '\N{WHITE HEAVY CHECK MARK}',
            '0\u20e3', '1\u20e3', '2\u20e3', '3\u20e3', '4\u20e3',
            '5\u20e3', '6\u20e3', '7\u20e3', '8\u20e3', '9\u20e3',
            '\N{REGIONAL INDICATOR SYMBOL LETTER A}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER D}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
            ]
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def reactables(self, ctx):
         if ctx.invoked_subcommand is None:
            await ctx.send(':thinking:')
    
    @reactables.command(aliases=['add'])
    async def create(self, ctx, role_id, *, description: str):
        local_embed = discord.Embed(
            title=f'#{target_channel.name}',
            description=f'{description[:2046]}',
            type="rich"
        )
        message = await ctx.send(embed=local_embed)
        await message.add_reaction(self.reaction_emojis[0])
        try:
            await self.bot.postgres_controller.add_reactables(
                message.id, target_channel.id, ctx.channel.id)
        except UniqueViolationError:
            await message.delete()
            await ctx.send(
                f"There already exists a link to {target_channel.name} here.")
        await ctx.message.delete()

    @reactables.command(aliases=['rem'])
    async def remove(self, ctx, target_channel: discord.TextChannel):
        """
        uhhh it removes the thing
        """
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except Exception as e:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        for reaction in og_message.reactions:
            async for user in reaction.users():
                if user.bot:
                    continue
                await og_message.remove_reaction(reaction.emoji, user)
                await self.remove_perms(user, target_channel)
        await og_message.delete()
        await self.bot.postgres_controller.rem_reactables(target_channel.id, ctx.channel.id)
        await ctx.message.delete()

    @reactables.command()
    async def edit(self, ctx, target_channel: discord.TextChannel, *, edit: str):
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        og_embed = og_message.embeds[0]
        og_embed.description = edit[:2046]
        await og_message.edit(embed=og_embed)
        await ctx.send(":ok_hand:", delete_after=3)
        await ctx.message.delete()

    @reactables.command(aliases=['fix'])
    async def update(self, ctx, target_channel: discord.TextChannel):
        """
        This will update the title of the embed to the currrent title of the channel
        """
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        og_embed = og_message.embeds[0]
        og_embed.title = f'#{target_channel.name}'
        await og_message.edit(embed=og_embed)
        await ctx.send(":ok_hand:", delete_after=3)
        await ctx.message.delete()

    @reactables.command(aliases=['color'])
    async def set_color(self, ctx, target_channel: discord.TextChannel, red, green, blue):
        """
        This will update the color of the embed to a given color code
        """
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        og_embed = og_message.embeds[0]
        og_embed.color = discord.Color.from_rgb(int(red), int(green), int(blue))
        await og_message.edit(embed=og_embed)
        await ctx.send(":ok_hand:", delete_after=3)
        await ctx.message.delete()

    @reactables.command()
    async def set_image(self, ctx, target_channel: discord.TextChannel, image_url):
        """
        This will update the image in the embed to the given url
        """
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        og_embed = og_message.embeds[0]
        try:
            og_embed.set_image(url=image_url)
        except Exception as e:
            self.bot.logger.warning(f'{e}')
            await ctx.send('something broke again', delete_after=3)
            return
        await og_message.edit(embed=og_embed)
        await ctx.send(":ok_hand:", delete_after=3)
        await ctx.message.delete()

    @reactables.command(aliases=['set_thumb'])
    async def set_thumbnail(self, ctx, target_channel: discord.TextChannel, image_url):
        """
        This will update the image in the embed to the given url
        """
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        og_embed = og_message.embeds[0]
        try:
            og_embed.set_thumbnail(url=image_url)
        except Exception as e:
            self.bot.logger.warning(f'{e}')
            await ctx.send('something broke again', delete_after=3)
            return
        await og_message.edit(embed=og_embed)
        await ctx.send(":ok_hand:", delete_after=3)
        await ctx.message.delete()


    @reactables.command()
    async def set_footer(self, ctx, target_channel: discord.TextChannel, *, footer):
        """
        This will update the footer in the embed to the given message
        """
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("that is not a valid channel fam", delete_after=4)
            return
        try:
            message_id = await self.bot.postgres_controller.get_message_info(
                ctx.channel.id, target_channel.id)
        except:
            await ctx.send("something broke", delete_after=3)
            return
        if not message_id:
            return
        og_message = await ctx.channel.get_message(message_id)
        og_embed = og_message.embeds[0]
        try:
            og_embed.set_footer(text=footer)
        except Exception as e:
            self.bot.logger.warning(f'{e}')
            await ctx.send('something broke again', delete_after=3)
            return
        await og_message.edit(embed=og_embed)
        await ctx.send(":ok_hand:", delete_after=3)
        await ctx.message.delete()


    async def on_raw_reaction_add(self, emoji, message_id, channel_id, user_id):
        """
        Called when an emoji is added
        """
        target_channel = await self.bot.postgres_controller.get_target_channel(channel_id, message_id)
        if not target_channel:
                return 
        user = self.bot.get_user(user_id)
        channel = self.bot.get_channel(target_channel)
        reacts = await self.bot.postgres_controller.add_user_reaction(user_id, message_id)
        if int(reacts) in [10,20,100]:
                time = self.bot.timestamp()
                mod_info = self.bot.get_channel(259728514914189312)
                await mod_info.send(
                    f'**{time} | REACTION SPAM:** {user} has reacted {reacts} '\
                    f'times today on the permission message for #{channel}'
                )
        await self.add_perms(user, channel)

    async def on_raw_reaction_remove(self, emoji, message_id, channel_id, user_id):
        """
        Called when an emoji is removed
        """
        target_channel = await self.bot.postgres_controller.get_target_channel(channel_id, message_id)
        if not target_channel:
            return
        channel = self.bot.get_channel(target_channel)
        user = self.bot.get_user(user_id)
        await self.remove_perms(user, channel)
    
    async def add_perms(self, user, channel):
        """
        Adds a user to channels perms
        """
        try:
            await channel.set_permissions(user, read_messages=True)
        except Exception as e:
            self.bot.logger.warning(f'{e}')  

    async def remove_perms(self, user, channel):
        """
        removes a users perms on a channel
        """
        try:
            await channel.set_permissions(user, read_messages=False)
        except Exception as e:
            self.bot.logger.warning(f'{e}')  