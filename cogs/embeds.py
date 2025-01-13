import discord
from discord.ext import commands

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, title, *, description):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Created by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def customembed(self, ctx, title, description, color: discord.Color, *, fields):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        # Parse fields (format: "field1|value1;field2|value2")
        field_list = fields.split(';')
        for field in field_list:
            name, value = field.split('|')
            embed.add_field(name=name.strip(), value=value.strip(), inline=False)
            
        embed.set_footer(text=f"Created by {ctx.author.name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Embeds(bot)) 