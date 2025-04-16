import discord
from discord.ext import commands
import config

class WelcomeEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Sends a welcome message when a new member joins the server"""
        # Find the welcome channel
        welcome_channel = discord.utils.get(member.guild.channels, name=config.WELCOME_CHANNEL)
        
        if welcome_channel:
            embed = discord.Embed(
                title=f"🌴 Welcome to ChessSafari, {member.display_name}! 🌴",
                description="We're excited to have you in our chess community!",
                color=0x7CFC00  # Jungle green color
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="👋 Get Started", value="Check out our channels and introduce yourself!", inline=False)
            embed.add_field(name="🎮 Play Chess", value="Challenge others or join our community events!", inline=False)
            embed.add_field(name="📚 Learn", value="Share and gain chess knowledge with fellow enthusiasts!", inline=False)
            embed.set_footer(text="🐘 Welcome to the chess jungle! 🦓")
            
            await welcome_channel.send(f"Everyone welcome {member.mention} to our chess safari!", embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeEvents(bot))
