import discord
from discord.ext import commands
import json
import random
import asyncio

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = {}
        self.load_levels()
        self.level_roles = {
            1: "Level 1",
            5: "Level 5",
            10: "Level 10",
            15: "Level 15",
            20: "Level 20"
        }

    def load_levels(self):
        try:
            with open('levels.json', 'r') as f:
                self.levels = json.load(f)
        except FileNotFoundError:
            self.levels = {}

    def save_levels(self):
        with open('levels.json', 'w') as f:
            json.dump(self.levels, f, indent=4)

    def get_level(self, exp):
        level = 0
        # Level 1-5: 1000 exp per level (about 50 messages)
        while level < 5 and exp >= ((level + 1) * 1000):
            level += 1
            exp -= level * 1000

        # Level 5-10: 2500 exp per level (about 125 messages)
        while level >= 5 and level < 10 and exp >= ((level + 1) * 2500):
            level += 1
            exp -= level * 2500

        # Level 10-15: 5000 exp per level (about 250 messages)
        while level >= 10 and level < 15 and exp >= ((level + 1) * 5000):
            level += 1
            exp -= level * 5000

        # Level 15-20: 10000 exp per level (about 500 messages)
        while level >= 15 and level < 20 and exp >= ((level + 1) * 10000):
            level += 1
            exp -= level * 10000

        return level

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Convert guild and user IDs to strings for JSON storage
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        # Initialize guild/user data if not exists
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"exp": 0, "level": 0}

        # Add random exp between 15-25
        exp_gain = random.randint(15, 25)
        self.levels[guild_id][user_id]["exp"] += exp_gain

        # Calculate new level
        new_level = self.get_level(self.levels[guild_id][user_id]["exp"])

        # Check for level up
        if new_level > self.levels[guild_id][user_id]["level"]:
            self.levels[guild_id][user_id]["level"] = new_level
            
            # Create level up embed
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} has reached Level {new_level}!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=message.author.avatar.url)
            
            await message.channel.send(embed=embed)

            # Handle role rewards
            if new_level in self.level_roles:
                role_name = self.level_roles[new_level]
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role:
                    await message.author.add_roles(role)

        self.save_levels()

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.levels or user_id not in self.levels[guild_id]:
            await ctx.send("This user has no level data!")
            return

        exp = self.levels[guild_id][user_id]["exp"]
        level = self.levels[guild_id][user_id]["level"]
        
        # Calculate next level exp requirement
        if level < 5:
            next_level_exp = (level + 1) * 1000
            progress_msg = "Level 1-5: 1,000 XP per level"
        elif level < 10:
            next_level_exp = (level + 1) * 2500
            progress_msg = "Level 5-10: 2,500 XP per level"
        elif level < 15:
            next_level_exp = (level + 1) * 5000
            progress_msg = "Level 10-15: 5,000 XP per level"
        else:
            next_level_exp = (level + 1) * 10000
            progress_msg = "Level 15-20: 10,000 XP per level"

        # Calculate percentage to next level
        current_level_exp = next_level_exp - ((level + 1) * (1000 if level < 5 else 2500 if level < 10 else 5000 if level < 15 else 10000))
        progress_percent = int((exp - current_level_exp) / (next_level_exp - current_level_exp) * 100)
        progress_bar = "█" * (progress_percent // 10) + "░" * (10 - (progress_percent // 10))

        embed = discord.Embed(
            title=f"{member.name}'s Level",
            description=f"Level: **{level}**\nXP: **{exp:,}/{next_level_exp:,}**\n\n{progress_bar} {progress_percent}%",
            color=discord.Color.blue()
        )
        embed.add_field(name="Current Tier", value=progress_msg, inline=False)
        embed.set_thumbnail(url=member.avatar.url)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def syncroles(self, ctx):
        # Create roles if they don't exist
        for level, role_name in self.level_roles.items():
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                await ctx.guild.create_role(name=role_name, color=discord.Color.blue())
                await ctx.send(f"Created role: {role_name}")

        # Give everyone Level 1 role
        level1_role = discord.utils.get(ctx.guild.roles, name="Level 1")
        if level1_role:
            for member in ctx.guild.members:
                if not member.bot and level1_role not in member.roles:
                    await member.add_roles(level1_role)
            
            await ctx.send("✅ Synchronized roles and gave everyone Level 1 role!")
        else:
            await ctx.send("❌ Could not find Level 1 role!")

async def setup(bot):
    await bot.add_cog(Leveling(bot)) 