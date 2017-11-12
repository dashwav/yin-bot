from discord.ext import commands
import random as rng
import discord

class RNG():

    def __init__(self, bot):
        self.bot = bot
        self.answers = [
            'For sure',
            'Very doubtful',
            'Most likely no',
            'As I see it, yes',
            'Probably not',
            'Nope',
            'Yes',
            'Maybe',
            'Most likely no',
            'Ask again later',
            'Definitely no',
            'Not sure',
            'It is uncertain',
            'Definitely yes',
            'Don\'t even think about it',
            'Perhaps',
            'NO - It may cause disease contraction',
        ]
        super().__init__()

    @commands.group(pass_context=True)
    async def random(self, ctx):
        """Displays a random thing you request."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect random subcommand passed. Try {ctx.prefix}help random')

    @random.command()
    async def number(self, ctx, minimum=0, maximum=100):
        """Displays a random number within an optional range.
        The minimum must be smaller than the maximum and the maximum number
        accepted is 1000.
        """

        maximum = min(maximum, 1000)
        if minimum >= maximum:
            await ctx.send('Maximum is smaller than minimum.')
            return

        await ctx.send(rng.randint(minimum, maximum))

    @commands.command()
    async def choose(self, ctx, *choices: commands.clean_content):
        """Chooses between multiple choices.
        To denote multiple choices, you should use double quotes.
        """
        choices = text.split(';')
        if len(choices) < 2:
            return await ctx.send('Not enough choices to pick from.')
        
        choice = rng.choice(choices)
        local_embed = discord.Embed(
            title=f' ',
            description=f':thinking:\n\n{choice}',
            color=0x419400
        )
        await ctx.send()

    @commands.command(name='8ball')
    async def eightball(self, ctx, *, question):
        """
        Uses magic to determine the answer to a question
        """
        if not question:
            return
        answer = rng.choice(self.answers)
        local_embed = discord.Embed(
            title=f' ',
            description=f'**❓ Question**\n\n{question}\n\n:8ball: **8ball**\n\n{answer}',
            color=0x419400
        )
        await ctx.send(embed=local_embed)
        
def setup(bot):
    bot.add_cog(RNG(bot))