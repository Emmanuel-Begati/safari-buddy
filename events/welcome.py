import discord
from discord.ext import commands
import logging

logger = logging.getLogger("safari_buddy.welcome")

class Welcome(commands.Cog):
    """Welcome new members and handle welcome channel messages."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Event triggered when a new member joins the server."""
        logger.info(f"New grandmaster joined: {member.name}#{member.discriminator} ({member.id})")
        
        # Find the welcome channel
        welcome_channel = discord.utils.get(member.guild.channels, name="welcome")
        
        if not welcome_channel:
            logger.warning(f"Welcome channel not found in {member.guild.name}")
            for channel in member.guild.channels:
                if isinstance(channel, discord.TextChannel) and "welcome" in channel.name.lower():
                    welcome_channel = channel
                    break
        
        if welcome_channel:
            # Send a welcome message with a fun safari theme
            welcome_message = (
                f"🌴 Welcome to the jungle, {member.mention}! "
                f"Grab a banana and enjoy the vibes 🍌\n\n"
                f"Make sure to check out the rules and introduce yourself!"
            )
            
            embed = discord.Embed(
                title=f"New Safari Explorer: {member.name}",
                description=welcome_message,
                color=discord.Color.green()
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Safari Buddy - Guiding you through the chess jungle")
            
            await welcome_channel.send(embed=embed)
        else:
            logger.error(f"Could not find welcome channel in {member.guild.name}")

def setup(bot):
    return bot.add_cog(Welcome(bot))