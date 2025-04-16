import discord
from discord.ext import commands
import config
import datetime

class LoggingEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_logs_channel(self, guild):
        """Helper method to get the logs channel"""
        return discord.utils.get(guild.channels, name=config.LOGS_CHANNEL)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Logs when a member joins the server"""
        logs_channel = await self.get_logs_channel(member.guild)
        if logs_channel:
            embed = discord.Embed(
                title="📝 Member Joined",
                description=f"{member.mention} joined the server",
                color=0x2ECC71,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=False)
            embed.set_footer(text=f"ID: {member.id}")
            
            await logs_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Logs when a member leaves the server"""
        logs_channel = await self.get_logs_channel(member.guild)
        if logs_channel:
            embed = discord.Embed(
                title="📝 Member Left",
                description=f"{member.display_name} left the server",
                color=0xE74C3C,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=False)
            embed.set_footer(text=f"ID: {member.id}")
            
            await logs_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Logs when a message is deleted"""
        # Skip if message is from a bot
        if message.author.bot:
            return
            
        logs_channel = await self.get_logs_channel(message.guild)
        if logs_channel:
            embed = discord.Embed(
                title="📝 Message Deleted",
                description=f"Message by {message.author.mention} deleted in {message.channel.mention}",
                color=0xF1C40F,
                timestamp=datetime.datetime.now()
            )
            
            # Add the message content (if it exists)
            if message.content:
                # Truncate if too long
                content = message.content
                if len(content) > 1024:
                    content = content[:1021] + "..."
                embed.add_field(name="Content", value=content, inline=False)
            
            # Add attachments if any
            if message.attachments:
                attach_str = "\n".join([f"[{a.filename}]({a.url})" for a in message.attachments])
                if attach_str:
                    embed.add_field(name="Attachments", value=attach_str, inline=False)
            
            embed.set_footer(text=f"User ID: {message.author.id} | Message ID: {message.id}")
            
            await logs_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LoggingEvents(bot))
