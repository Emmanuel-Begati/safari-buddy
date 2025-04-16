import discord
from discord.ext import commands
from discord import SlashCommandGroup, Option
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class General(commands.Cog):
    """General commands for ChessSafari Discord bot."""
    
    def __init__(self, bot):
        self.bot = bot
        self.coach_link = os.getenv('COACH_LINK', 'https://example.com/coach')
        self.discord_link = os.getenv('DISCORD_LINK', 'https://discord.gg/chesssafari')
        self.twitch_link = os.getenv('TWITCH_LINK', 'https://twitch.tv/chesssafari')
        self.youtube_link = os.getenv('YOUTUBE_LINK', 'https://youtube.com/chesssafari')
        self.instagram_link = os.getenv('INSTAGRAM_LINK', 'https://instagram.com/chesssafari')
    
    # Slash Commands
    
    @discord.slash_command(name="coach", description="Get coaching information")
    async def coach_slash(self, ctx):
        """Slash command to get coaching information."""
        await ctx.respond(f"🦒 **Looking for chess coaching?** Check out ChessSafari's coaching services:\n{self.coach_link}")
    
    @discord.slash_command(name="discord", description="Get an invite link to this Discord server")
    async def discord_slash(self, ctx):
        """Slash command to get Discord invite link."""
        await ctx.respond(f"🐘 **Join our Discord community!**\n{self.discord_link}")
    
    @discord.slash_command(name="twitch", description="Get a link to ChessSafari's Twitch channel")
    async def twitch_slash(self, ctx):
        """Slash command to get Twitch channel link."""
        await ctx.respond(f"🦁 **Watch ChessSafari live on Twitch!**\n{self.twitch_link}")
    
    @discord.slash_command(name="youtube", description="Get a link to ChessSafari's YouTube channel")
    async def youtube_slash(self, ctx):
        """Slash command to get YouTube channel link."""
        await ctx.respond(f"🦓 **Check out ChessSafari's YouTube channel!**\n{self.youtube_link}")
    
    @discord.slash_command(name="instagram", description="Get a link to ChessSafari's Instagram")
    async def instagram_slash(self, ctx):
        """Slash command to get Instagram link."""
        await ctx.respond(f"🐒 **Follow ChessSafari on Instagram!**\n{self.instagram_link}")
    
    @discord.slash_command(name="status", description="Check the bot's current status")
    async def status_slash(self, ctx):
        """Slash command to check bot status."""
        uptime = discord.utils.utcnow() - self.bot.user.created_at
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title="🌴 Safari Buddy Status",
            description="Here's the current status of the Safari Buddy bot",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Bot Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Connected Servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(
            name="Uptime", 
            value=f"{days}d {hours}h {minutes}m {seconds}s", 
            inline=True
        )
        embed.set_footer(text="Safari Buddy - Watching the jungle 🦁")
        
        await ctx.respond(embed=embed)
    
    @discord.slash_command(name="chessfact", description="Get a random chess fact")
    async def chessfact_slash(self, ctx):
        """Slash command to get a random chess fact."""
        import random
        
        facts = [
            "The longest chess game theoretically possible is 5,949 moves.",
            "The word 'Checkmate' comes from the Persian phrase 'Shah Mat,' which means 'the king is dead.'",
            "The longest chess game ever played lasted for 269 moves and ended in a draw.",
            "There are 400 different possible positions after each player makes one move apiece.",
            "There are 72,084 possible positions after two moves each.",
            "The number of possible unique chess games is much greater than the number of electrons in the observable universe.",
            "The first chess computer program was developed in 1951.",
            "The first official World Chess Champion was Wilhelm Steinitz in 1886.",
            "The shortest possible chess game ending in checkmate is just two moves.",
            "The oldest recorded chess game in history dates back to the 10th century.",
            "The folding chessboard was invented by a priest who was forbidden to play chess.",
            "Chess pieces were originally made to represent medieval court figures.",
            "In medieval India, chess was used as a way to teach military strategy."
        ]
        
        await ctx.respond(f"🧠 **Chess Fact**: {random.choice(facts)}")
    
    # Traditional Prefix Commands
    
    @commands.command(name="coach")
    async def coach_prefix(self, ctx):
        """Traditional command to get coaching information."""
        try:
            await ctx.send(f"🦒 **Looking for chess coaching?** Check out ChessSafari's coaching services:\n{self.coach_link}")
        except discord.Forbidden:
            # Try to DM the user if we can't send to the channel
            try:
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's the coaching info:\n\n🦒 **Looking for chess coaching?** Check out ChessSafari's coaching services:\n{self.coach_link}")
            except discord.Forbidden:
                # Can't DM either, silently fail
                pass
    
    @commands.command(name="discord")
    async def discord_prefix(self, ctx):
        """Traditional command to get Discord invite link."""
        try:
            await ctx.send(f"🐘 **Join our Discord community!**\n{self.discord_link}")
        except discord.Forbidden:
            try:
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's the Discord link:\n\n🐘 **Join our Discord community!**\n{self.discord_link}")
            except discord.Forbidden:
                pass
    
    @commands.command(name="twitch")
    async def twitch_prefix(self, ctx):
        """Traditional command to get Twitch channel link."""
        try:
            await ctx.send(f"🦁 **Watch ChessSafari live on Twitch!**\n{self.twitch_link}")
        except discord.Forbidden:
            try:
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's the Twitch link:\n\n🦁 **Watch ChessSafari live on Twitch!**\n{self.twitch_link}")
            except discord.Forbidden:
                pass
    
    @commands.command(name="youtube")
    async def youtube_prefix(self, ctx):
        """Traditional command to get YouTube channel link."""
        try:
            await ctx.send(f"🦓 **Check out ChessSafari's YouTube channel!**\n{self.youtube_link}")
        except discord.Forbidden:
            try:
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's the YouTube link:\n\n🦓 **Check out ChessSafari's YouTube channel!**\n{self.youtube_link}")
            except discord.Forbidden:
                pass
    
    @commands.command(name="instagram")
    async def instagram_prefix(self, ctx):
        """Traditional command to get Instagram link."""
        try:
            await ctx.send(f"🐒 **Follow ChessSafari on Instagram!**\n{self.instagram_link}")
        except discord.Forbidden:
            try:
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's the Instagram link:\n\n🐒 **Follow ChessSafari on Instagram!**\n{self.instagram_link}")
            except discord.Forbidden:
                pass
    
    @commands.command(name="status")
    async def status_prefix(self, ctx):
        """Traditional command to check bot status."""
        try:
            await self.status_slash.invoke(ctx)
        except discord.Forbidden:
            try:
                # Create a basic text version for DM
                uptime = discord.utils.utcnow() - self.bot.user.created_at
                days, remainder = divmod(int(uptime.total_seconds()), 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                status_text = f"**🌴 Safari Buddy Status**\n\n" \
                              f"**Bot Latency:** {round(self.bot.latency * 1000)}ms\n" \
                              f"**Connected Servers:** {len(self.bot.guilds)}\n" \
                              f"**Uptime:** {days}d {hours}h {minutes}m {seconds}s\n\n" \
                              f"*Safari Buddy - Watching the jungle 🦁*"
                
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's the bot status:\n\n{status_text}")
            except discord.Forbidden:
                pass
    
    @commands.command(name="chessfact")
    async def chessfact_prefix(self, ctx):
        """Traditional command to get a random chess fact."""
        try:
            await self.chessfact_slash.invoke(ctx)
        except discord.Forbidden:
            import random
            
            facts = [
                "The longest chess game theoretically possible is 5,949 moves.",
                "The word 'Checkmate' comes from the Persian phrase 'Shah Mat,' which means 'the king is dead.'",
                "The longest chess game ever played lasted for 269 moves and ended in a draw.",
                # ... other facts omitted for brevity
            ]
            
            try:
                await ctx.author.send(f"I don't have permission to send messages in that channel. Here's a chess fact:\n\n🧠 **Chess Fact**: {random.choice(facts)}")
            except discord.Forbidden:
                pass
    
    # Add a global error handler for the cog
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle errors from commands in this cog."""
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.Forbidden):
                # Already handled in the individual commands
                pass
        # Let other errors propagate to the global handler

def setup(bot):
    return bot.add_cog(General(bot))