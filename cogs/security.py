import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, Counter

class SecuritySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1328480497143386172
        self.join_history = defaultdict(list)  # Track join patterns
        self.message_history = defaultdict(list)  # Track message patterns
        self.suspicious_patterns = defaultdict(int)  # Track suspicious activity
        self.min_account_age = timedelta(days=7)  # Minimum account age
        self.raid_detection_interval = timedelta(minutes=5)
        self.raid_join_threshold = 5  # Number of joins within interval to trigger alert
        self.clear_old_data.start()

    def cog_unload(self):
        self.clear_old_data.cancel()

    async def send_log(self, embed):
        """Send log embed to the specified channel"""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(embed=embed)

    @tasks.loop(minutes=30)
    async def clear_old_data(self):
        """Clear old tracking data"""
        current_time = datetime.utcnow()
        for user_id in list(self.join_history.keys()):
            self.join_history[user_id] = [t for t in self.join_history[user_id] 
                                        if current_time - t < timedelta(hours=1)]

    async def check_raid(self, member):
        """Check for potential raid activity"""
        current_time = datetime.utcnow()
        self.join_history[member.guild.id].append(current_time)
        
        # Check recent joins
        recent_joins = [t for t in self.join_history[member.guild.id] 
                       if current_time - t < self.raid_detection_interval]
        
        if len(recent_joins) >= self.raid_join_threshold:
            embed = discord.Embed(
                title="⚠️ RAID ALERT",
                description=f"Detected {len(recent_joins)} joins in the last {self.raid_detection_interval.seconds // 60} minutes",
                color=discord.Color.red(),
                timestamp=current_time
            )
            await self.send_log(embed)
            return True
        return False

    async def check_account_age(self, member):
        """Check if account is too new"""
        account_age = datetime.utcnow() - member.created_at
        if account_age < self.min_account_age:
            embed = discord.Embed(
                title="⚠️ New Account Alert",
                description=f"{member.mention}'s account is only {account_age.days} days old",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            embed.add_field(name="User ID", value=member.id)
            await self.send_log(embed)
            return True
        return False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Process new member joins"""
        alerts = []
        
        # Check for raid
        if await self.check_raid(member):
            alerts.append("🚨 Potential Raid Detected")
            
        # Check account age
        if await self.check_account_age(member):
            alerts.append("⚠️ New Account")

        # Send comprehensive join log
        embed = discord.Embed(
            title="Member Joined" if not alerts else "⚠️ Suspicious Join",
            description=f"{member.mention} joined the server",
            color=discord.Color.red() if alerts else discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Account Age", value=f"{(datetime.utcnow() - member.created_at).days} days")
        embed.add_field(name="User ID", value=member.id)
        if alerts:
            embed.add_field(name="Alerts", value="\n".join(alerts), inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor chat for suspicious behavior"""
        if message.author.bot:
            return

        current_time = datetime.utcnow()
        self.message_history[message.author.id].append(current_time)
        
        # Check for spam
        recent_messages = [t for t in self.message_history[message.author.id] 
                         if current_time - t < timedelta(seconds=5)]
        
        if len(recent_messages) >= 5:
            embed = discord.Embed(
                title="🚨 Spam Detection",
                description=f"{message.author.mention} sent {len(recent_messages)} messages in 5 seconds",
                color=discord.Color.red(),
                timestamp=current_time
            )
            await self.send_log(embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def securitystatus(self, ctx):
        """Check security system status"""
        embed = discord.Embed(
            title="Security System Status",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Raid Detection", value=f"Threshold: {self.raid_join_threshold} joins/{self.raid_detection_interval.seconds // 60}min")
        embed.add_field(name="Min Account Age", value=f"{self.min_account_age.days} days")
        embed.add_field(name="Monitoring", value="✅ Active")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SecuritySystem(bot)) 