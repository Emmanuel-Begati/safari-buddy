import discord
from discord.ext import commands
import config

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coach")
    async def coach(self, ctx):
        """Sends information about coaching sessions"""
        embed = discord.Embed(
            title="🧠 Chess Coaching with ChessSafari 🧠",
            description="Level up your chess game with personalized coaching!",
            color=0x7CFC00  # Jungle green color
        )
        embed.add_field(name="Book a Session", value=f"[Click here to book]({config.COACH_LINK})", inline=False)
        embed.set_footer(text="🐘 Let's navigate the chess jungle together! 🌴")
        
        await ctx.send(embed=embed)

    @commands.command(name="discord")
    async def discord_invite(self, ctx):
        """Shares the Discord invite link"""
        embed = discord.Embed(
            title="🌿 Join Our Chess Community! 🌿",
            description="Invite your friends to the ChessSafari Discord server!",
            color=0x7CFC00
        )
        embed.add_field(name="Invite Link", value=f"[Join the jungle!]({config.DISCORD_INVITE})", inline=False)
        embed.set_footer(text="🦁 The more, the merrier in our chess safari! 🦓")
        
        await ctx.send(embed=embed)

    @commands.command(name="twitch")
    async def twitch(self, ctx):
        """Links to the Twitch channel"""
        embed = discord.Embed(
            title="📺 ChessSafari on Twitch 📺",
            description="Watch live chess streams, analysis, and more!",
            color=0x6441A4  # Twitch purple
        )
        embed.add_field(name="Channel Link", value=f"[Follow on Twitch]({config.TWITCH_CHANNEL})", inline=False)
        embed.set_footer(text="🐯 Join the stream and let's play some chess! ��")
        
        await ctx.send(embed=embed)

    @commands.command(name="youtube")
    async def youtube(self, ctx):
        """Links to the YouTube channel"""
        embed = discord.Embed(
            title="🎬 ChessSafari YouTube Channel 🎬",
            description="Check out our chess videos, tutorials, and game analyses!",
            color=0xFF0000  # YouTube red
        )
        embed.add_field(name="Channel Link", value=f"[Subscribe on YouTube]({config.YOUTUBE_CHANNEL})", inline=False)
        embed.set_footer(text="🦒 Tall content for tall ambitions! 🌴")
        
        await ctx.send(embed=embed)

    @commands.command(name="insta")
    async def instagram(self, ctx):
        """Shares the Instagram profile"""
        embed = discord.Embed(
            title="📸 ChessSafari on Instagram 📸",
            description="Follow us for chess puzzles, highlights, and behind-the-scenes!",
            color=0xE1306C  # Instagram pink/purple
        )
        embed.add_field(name="Profile Link", value=f"[Follow on Instagram]({config.INSTAGRAM_PROFILE})", inline=False)
        embed.set_footer(text="🐒 Swinging from pawns to kings! 🌴")
        
        await ctx.send(embed=embed)

    @commands.command(name="live")
    async def live_notification(self, ctx):
        """Announces when going live on Twitch"""
        embed = discord.Embed(
            title="🔴 ChessSafari is LIVE! 🔴",
            description=f"I'm live on Twitch! Come join 🐘♟️",
            color=0x6441A4  # Twitch purple
        )
        embed.add_field(name="Watch Now", value=f"[Join the stream]({config.TWITCH_CHANNEL})", inline=False)
        embed.set_footer(text="🦓 Wild chess moves incoming! 🐘")
        
        await ctx.send("@everyone", embed=embed)
        
async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
