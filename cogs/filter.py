"""
A cog that filters all but a specific few phrases. (ignores bots)
"""
import discord


class Filter():

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.channels = bot.filter_channels
        self.filter_allowed = bot.filter_allowed

    async def on_message(self, message):
        if message.channel.id not in self.channels:
            return
        if message.author.bot:
            return
        cleaned_message = message.clean_content
        if cleaned_message.lower() in self.filter_allowed:
            return
        else:
            try:
                await message.delete()
                self.bot.logger.info(
                    'Successfully deleted message from: '
                    f'{message.author.display_name}')
            except Exception as e:
                self.bot.logger.warning(f'Error deleting message: {e}')
