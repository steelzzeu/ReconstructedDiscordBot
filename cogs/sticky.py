import discord
from discord.ext import commands

class Sticky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky_messages = {}
        self.last_sticky_message = {}

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def sticky(self, ctx, *, message):
        self.sticky_messages[ctx.channel.id] = message
        
        # Delete the old sticky message if it exists
        if ctx.channel.id in self.last_sticky_message:
            try:
                old_message = await ctx.channel.fetch_message(self.last_sticky_message[ctx.channel.id])
                await old_message.delete()
            except:
                pass

        # Send new sticky message
        sticky_msg = await ctx.send(f"📌 {message}")
        self.last_sticky_message[ctx.channel.id] = sticky_msg.id

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id in self.sticky_messages:
            # Delete the old sticky message
            if message.channel.id in self.last_sticky_message:
                try:
                    old_message = await message.channel.fetch_message(self.last_sticky_message[message.channel.id])
                    await old_message.delete()
                except:
                    pass

            # Send new sticky message
            sticky_msg = await message.channel.send(f"📌 {self.sticky_messages[message.channel.id]}")
            self.last_sticky_message[message.channel.id] = sticky_msg.id

async def setup(bot):
    await bot.add_cog(Sticky(bot)) 