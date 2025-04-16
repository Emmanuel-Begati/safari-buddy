import discord
from discord.ext import commands
import logging
from datetime import datetime

logger = logging.getLogger("safari_buddy.logging")

class Logging(commands.Cog):
    """Log member activities and message changes to a mod-logs channel."""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_logs_channel(self, guild):
        """Find the mod-logs channel in the guild."""
        logs_channel = discord.utils.get(guild.channels, name="mod-logs")
        
        if not logs_channel:
            # Try to find a channel with "log" in the name
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) and ("log" in channel.name.lower() or "mod" in channel.name.lower()):
                    logs_channel = channel
                    break
        
        return logs_channel
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log when a member joins the server."""
        logs_channel = await self.get_logs_channel(member.guild)
        
        if logs_channel:
            embed = discord.Embed(
                title="Member Joined",
                description=f"{member.mention} joined the server",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="ID", value=member.id, inline=True)
            embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
            
            await logs_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a member leaves the server."""
        logs_channel = await self.get_logs_channel(member.guild)
        
        if logs_channel:
            embed = discord.Embed(
                title="Member Left",
                description=f"{member.name}#{member.discriminator} left the server",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="ID", value=member.id, inline=True)
            embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp()) if member.joined_at else 0}:R>", inline=True)
            
            await logs_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log when a message is deleted."""
        if message.author.bot:
            return
        
        logs_channel = await self.get_logs_channel(message.guild)
        
        if logs_channel:
            embed = discord.Embed(
                title="Message Deleted",
                description=f"Message by {message.author.mention} deleted in {message.channel.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            if message.content:
                if len(message.content) > 1024:
                    embed.add_field(name="Content", value=f"{message.content[:1021]}...", inline=False)
                else:
                    embed.add_field(name="Content", value=message.content, inline=False)
            
            if message.attachments:
                attachment_names = [attachment.filename for attachment in message.attachments]
                embed.add_field(name="Attachments", value=", ".join(attachment_names), inline=False)
            
            await logs_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log when a message is edited."""
        if before.author.bot or before.content == after.content:
            return
        
        logs_channel = await self.get_logs_channel(before.guild)
        
        if logs_channel:
            embed = discord.Embed(
                title="Message Edited",
                description=f"Message by {before.author.mention} edited in {before.channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=before.author.display_avatar.url)
            embed.add_field(name="Before", value=before.content[:1024] if before.content else "(empty)", inline=False)
            embed.add_field(name="After", value=after.content[:1024] if after.content else "(empty)", inline=False)
            embed.add_field(name="Jump to Message", value=f"[Click Here]({after.jump_url})", inline=False)
            
            await logs_channel.send(embed=embed)

def setup(bot):
    return bot.add_cog(Logging(bot))