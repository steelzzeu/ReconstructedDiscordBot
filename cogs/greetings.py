import discord
from discord.ext import commands
import json

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.config['welcome_channel_id'])
        embed = discord.Embed(
            title="Welcome!",
            description=f"Welcome to the server, {member.mention}! We're glad to have you here!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if len(before.roles) < len(after.roles):
            new_role = next(role for role in after.roles if role not in before.roles)
            if new_role.is_premium_subscriber():
                channel = self.bot.get_channel(self.config['boost_channel_id'])
                embed = discord.Embed(
                    title="Server Boost!",
                    description=f"Thank you {after.mention} for boosting the server! 🚀",
                    color=discord.Color.purple()
                )
                embed.set_thumbnail(url=after.avatar.url)
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Greetings(bot)) 