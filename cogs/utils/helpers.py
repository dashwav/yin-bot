"""
Helper functions for nano-chan.
Did take a few from kitsu-chan and modify them tbh
"""
import asyncio
import discord
from discord.ext import commands


async def confirm(ctx: commands.Context, member_to_kick, reason):
    """
    Yes no helper. Ask a confirmation message with a timeout of 5 seconds.
    ctx - The context in which the question is being asked.
    message - Optional messsage that the question should ask.
    """
    message = create_confirm_embed(ctx, ctx.guild, member_to_kick, reason)
    confirmation_message = await ctx.send(embed=message, delete_after=10)
    try:
        message = await ctx.bot.wait_for("message",
                                         timeout=10,
                                         check=lambda message: message.author
                                         == ctx.message.author)
    except asyncio.TimeoutError:
        return False
    if message.clean_content.lower() != 'confirm':
        return False
    try:
        await confirmation_message.delete()
        await message.delete()
    except Exception as e:
        print(f'Error in deleting message: {e}')
    return True


async def custom_confirm(ctx: commands.Context, custom_message):
    """
    Yes no helper. Ask a confirmation message with a timeout of 5 seconds.
    ctx - The context in which the question is being asked.
    message - Optional messsage that the question should ask.
    """
    message = create_custom_embed(ctx, custom_message)
    confirmation_message = await ctx.send(embed=message, delete_after=10)
    try:
        message = await ctx.bot.wait_for("message",
                                         timeout=10,
                                         check=lambda message: message.author
                                         == ctx.message.author)
    except asyncio.TimeoutError:
        return False
    if message.clean_content.lower() != 'confirm':
        return False
    try:
        await confirmation_message.delete()
        await message.delete()
    except Exception as e:
        print(f'Error in deleting message: {e}')
    return True


def create_confirm_embed(ctx, server_name, member_to_kick, reason):
        embed = discord.Embed(
            title=f'❗ Confirmation Request ❗',
            type='rich')
        embed.description = f'\nYou are attempting to {ctx.command}'\
                            f'**{member_to_kick}** from **{server_name}**'\
                            f'\n```{str(ctx.command).title()} '\
                            f'reason:\n\n{reason}```'\
                            f'\n➡️ Type `confirm` to {ctx.command} the user,'\
                            ' or literally anything else to cancel.'\
                            '\n\n*You have 10 seconds...*'
        embed.add_field(name='ID', value=member_to_kick.id)
        return embed


def create_custom_embed(ctx, custom_message):
        embed = discord.Embed(
            title=f'❗ Confirmation Request ❗',
            type='rich')
        embed.description = f'\nYou are attempting to {ctx.command}:\n'\
                            f'{custom_message}'\
                            f'\n➡️ Type `confirm` to {ctx.command}'\
                            ' or literally anything else to cancel.'\
                            '\n\n*You have 10 seconds...*'
        return embed
