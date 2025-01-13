import discord
from discord.ext import commands, tasks
import asyncio

class StatusChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_icons = {
            "broken": "🔴",
            "fixed": "🟢",
            "trying": "🟡"
        }
        self.member_count_update.start()

    def cog_unload(self):
        self.member_count_update.cancel()

    async def create_status_category(self, guild):
        try:
            # Create status category if it doesn't exist
            category = discord.utils.get(guild.categories, name="Status")
            if not category:
                category = await guild.create_category("Status", position=0)
                
            # Create or get status channel
            status_channel = discord.utils.get(category.voice_channels, name__startswith="Status:")
            if not status_channel:
                status_channel = await category.create_voice_channel("Status: 🔴 Broken")
                await status_channel.set_permissions(guild.default_role, connect=False)

            # Create or get member count channel
            count_channel = discord.utils.get(category.voice_channels, name__startswith="Members:")
            if not count_channel:
                count_channel = await category.create_voice_channel(f"Members: {guild.member_count}")
                await count_channel.set_permissions(guild.default_role, connect=False)

            return status_channel, count_channel
        except Exception as e:
            print(f"Error creating channels: {e}")
            return None, None

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupstatus(self, ctx):
        """Manually create the status channels"""
        status_channel, count_channel = await self.create_status_category(ctx.guild)
        if status_channel and count_channel:
            await ctx.send("✅ Status channels have been created!")
        else:
            await ctx.send("❌ Failed to create status channels!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx, status_type: str):
        status_type = status_type.lower()
        if status_type not in self.status_icons:
            await ctx.send("❌ Invalid status! Use: broken, fixed, or trying")
            return

        status_channel = discord.utils.get(ctx.guild.voice_channels, name__startswith="Status:")
        if not status_channel:
            status_channel, _ = await self.create_status_category(ctx.guild)

        icon = self.status_icons[status_type]
        status_text = f"Status: {icon} {status_type.capitalize()}"
        await status_channel.edit(name=status_text)

        embed = discord.Embed(
            title="Status Updated",
            description=f"Status has been set to: {status_text}",
            color=discord.Color.green() if status_type == "fixed" else 
                  discord.Color.red() if status_type == "broken" else 
                  discord.Color.gold()
        )
        embed.set_footer(text=f"Updated by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        """Create status channels when bot starts up"""
        for guild in self.bot.guilds:
            await self.create_status_category(guild)

    async def update_member_count(self, guild):
        """Update member count channel name"""
        try:
            category = discord.utils.get(guild.categories, name="Status")
            if category:
                count_channel = discord.utils.get(category.voice_channels, name__startswith="Members:")
                if count_channel:
                    new_count = guild.member_count
                    new_name = f"Members: {new_count}"
                    
                    if count_channel.name != new_name:
                        await count_channel.edit(name=new_name)
                        print(f"Updated member count for {guild.name} to {new_count}")
        except Exception as e:
            print(f"Error updating member count: {e}")

    @tasks.loop(seconds=30)
    async def member_count_update(self):
        """Update member count every 30 seconds"""
        for guild in self.bot.guilds:
            await self.update_member_count(guild)

    @member_count_update.before_loop
    async def before_member_count_update(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Update count when a member joins and assign Community role"""
        try:
            # Update member count
            await asyncio.sleep(2)
            await self.update_member_count(member.guild)
            
            # Assign Community role
            community_role = member.guild.get_role(1327000444148383784)
            if community_role:
                await member.add_roles(community_role)
                print(f"Assigned Community role to {member.name}")
            else:
                print("Community role not found!")
                
        except Exception as e:
            print(f"Error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Update count when a member leaves"""
        await asyncio.sleep(2)  # Wait for Discord to process the leave
        await self.update_member_count(member.guild)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def syncmembers(self, ctx):
        """Force sync member count"""
        try:
            guild = ctx.guild
            if not guild.chunked:
                await guild.chunk()
            
            total_members = sum(1 for m in guild.members)
            await self.update_member_count(guild)
            
            embed = discord.Embed(
                title="Member Count Synced",
                description=f"Total Members: {total_members}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error syncing members: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.create_status_category(guild)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def forcesync(self, ctx):
        """Force sync member count with detailed feedback"""
        try:
            guild = ctx.guild
            before_count = guild.member_count
            await guild.chunk()  # Force Discord to update member cache
            after_count = guild.member_count
            
            await self.update_member_count(guild)
            
            embed = discord.Embed(
                title="Member Count Sync",
                description=f"Before: {before_count}\nAfter: {after_count}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error syncing: {e}")

async def setup(bot):
    await bot.add_cog(StatusChannels(bot)) 