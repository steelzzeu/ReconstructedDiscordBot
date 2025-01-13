import discord
from discord.ext import commands
from datetime import datetime

class AuditLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1328480497143386172

    async def send_log(self, embed):
        """Send log embed to the specified channel"""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="👋 Member Joined",
            description=f"{member.mention} joined the server",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="User ID", value=member.id)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="🚶 Member Left",
            description=f"{member.name}#{member.discriminator} left the server",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="User ID", value=member.id)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                title="📝 Nickname Changed",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Member", value=after.mention)
            embed.add_field(name="Before", value=before.nick or "None")
            embed.add_field(name="After", value=after.nick or "None")
            await self.send_log(embed)

        # Role changes
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]
            
            if added_roles or removed_roles:
                embed = discord.Embed(
                    title="👑 Role Changes",
                    color=discord.Color.gold(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Member", value=after.mention)
                if added_roles:
                    embed.add_field(name="Added Roles", value=", ".join([role.mention for role in added_roles]))
                if removed_roles:
                    embed.add_field(name="Removed Roles", value=", ".join([role.mention for role in removed_roles]))
                await self.send_log(embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=f"Message by {message.author.mention} deleted in {message.channel.mention}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            if message.content:
                embed.add_field(name="Content", value=message.content[:1024])
            if message.attachments:
                embed.add_field(name="Attachments", value="\n".join([a.url for a in message.attachments]))
            await self.send_log(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author.bot and before.content != after.content:
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"Message by {before.author.mention} edited in {before.channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Before", value=before.content[:1024])
            embed.add_field(name="After", value=after.content[:1024])
            embed.add_field(name="Jump to Message", value=f"[Click Here]({after.jump_url})")
            await self.send_log(embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        embed = discord.Embed(
            title="🎤 Voice Update",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Member", value=member.mention)

        if before.channel != after.channel:
            if after.channel and not before.channel:
                embed.description = f"Joined {after.channel.name}"
            elif before.channel and not after.channel:
                embed.description = f"Left {before.channel.name}"
            else:
                embed.description = f"Moved from {before.channel.name} to {after.channel.name}"
            await self.send_log(embed)

async def setup(bot):
    await bot.add_cog(AuditLogger(bot)) 