import discord
from discord.ext import commands
import json

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    @commands.command()
    async def bug(self, ctx, *, bug_report):
        channel = self.bot.get_channel(self.config['bug_reports_channel_id'])
        embed = discord.Embed(
            title="Bug Report",
            description=bug_report,
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"ID: {ctx.author.id}")
        await channel.send(embed=embed)
        await ctx.send("Bug report submitted successfully!")

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        channel = self.bot.get_channel(self.config['suggestions_channel_id'])
        embed = discord.Embed(
            title="Suggestion",
            description=suggestion,
            color=discord.Color.green()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"ID: {ctx.author.id}")
        message = await channel.send(embed=embed)
        
        # Add reaction buttons
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        
        await ctx.send("Suggestion submitted successfully!")

async def setup(bot):
    await bot.add_cog(Feedback(bot)) 