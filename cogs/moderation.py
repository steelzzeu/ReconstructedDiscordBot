import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        # Create and send DM embed
        embed = discord.Embed(
            title="You have been kicked!",
            description=f"You have been kicked from {ctx.guild.name}",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason:", value=reason or "No reason provided")
        embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        
        try:
            await member.send(embed=embed)
        except:
            pass  # If DM fails, continue with kick
            
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked. Reason: {reason}')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        # Create and send DM embed
        embed = discord.Embed(
            title="You have been banned!",
            description=f"You have been banned from {ctx.guild.name}",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Reason:", value=reason or "No reason provided")
        embed.set_footer(text=f"Banned by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        # Add the ban hammer GIF (using a different direct GIF URL)
        embed.set_image(url="https://i.imgur.com/O3DHIA5.gif")
        
        try:
            await member.send(embed=embed)
        except:
            pass  # If DM fails, continue with ban
            
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned. Reason: {reason}')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'Purged {amount} messages.', delete_after=5)

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: int, *, reason=None):
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=duration), reason=reason)
        await ctx.send(f'{member.mention} has been timed out for {duration} minutes. Reason: {reason}')

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        try:
            # Convert member string to user ID if possible
            member_id = int(member) if member.isdigit() else None
            
            banned_users = [entry async for entry in ctx.guild.bans()]
            for ban_entry in banned_users:
                user = ban_entry.user
                # Check if the user matches either by ID or by name#discriminator
                if (member_id and user.id == member_id) or str(user) == member:
                    await ctx.guild.unban(user)
                    embed = discord.Embed(
                        title="User Unbanned",
                        description=f"Successfully unbanned {user.mention}",
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Unbanned by {ctx.author}", icon_url=ctx.author.avatar.url)
                    await ctx.send(embed=embed)
                    return
            
            await ctx.send("User not found in ban list.")
            
        except ValueError:
            await ctx.send("Please provide a valid user ID or username#discriminator")

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx, member: discord.Member, *, role: discord.Role):
        try:
            if role in member.roles:
                await ctx.send(f"{member.mention} already has the {role.name} role!")
                return
                
            await member.add_roles(role)
            
            # Create and send embed
            embed = discord.Embed(
                title="Role Added! 🎭",
                description=f"Successfully gave {role.mention} to {member.mention}",
                color=role.color
            )
            embed.add_field(name="Role", value=role.name, inline=True)
            embed.add_field(name="Member", value=member.name, inline=True)
            embed.set_footer(text=f"Given by {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.set_thumbnail(url=member.avatar.url)
            # Add the rat wave GIF
            embed.set_image(url="https://media.tenor.com/p6c_YBRwdqkAAAAC/rat-hi.gif")
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to give that role!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @giverole.error
    async def giverole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please specify both a member and a role!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("❌ That role was not found!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ That member was not found!")

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 