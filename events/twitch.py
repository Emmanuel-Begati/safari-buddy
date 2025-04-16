import discord
from discord.ext import commands, tasks
import os
import logging
import aiohttp
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

logger = logging.getLogger("safari_buddy.twitch")

class TwitchNotifier(commands.Cog):
    """Handles Twitch live notifications."""
    
    def __init__(self, bot):
        self.bot = bot
        self.twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
        self.twitch_client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.twitch_channel_name = os.getenv('TWITCH_CHANNEL', 'chesssafari')
        self.announcement_channel_name = os.getenv('ANNOUNCEMENT_CHANNEL', 'live-now')
        self.is_live = False
        self.access_token = None
        self.token_expires = datetime.utcnow()
        
        # Start the background task if credentials are provided
        if self.twitch_client_id and self.twitch_client_secret and self.twitch_client_id != "your_twitch_client_id":
            self.check_twitch_stream.start()
            logger.info("Twitch notifications enabled.")
        else:
            logger.warning("Twitch credentials not provided or are default values. Live notifications disabled.")
    
    def cog_unload(self):
        """Clean up when the cog is unloaded."""
        self.check_twitch_stream.cancel()
    
    @discord.slash_command(name="go-live", description="Manually trigger a live notification")
    @discord.default_permissions(administrator=True)
    async def go_live_slash(self, ctx):
        """Slash command to manually trigger a live notification."""
        await ctx.defer(ephemeral=True)  # Make the response only visible to the user who triggered it
        
        if await self.send_live_notification():
            await ctx.respond("✅ Live notification sent successfully!", ephemeral=True)
        else:
            await ctx.respond("❌ Failed to send live notification. Check logs for details.", ephemeral=True)
    
    @commands.command(name="go-live")
    @commands.has_permissions(administrator=True)
    async def go_live_prefix(self, ctx):
        """Traditional command to manually trigger a live notification."""
        if await self.send_live_notification():
            await ctx.send("✅ Live notification sent successfully!")
        else:
            await ctx.send("❌ Failed to send live notification. Check logs for details.")
    
    async def get_twitch_token(self):
        """Get a Twitch API access token."""
        if not self.twitch_client_id or not self.twitch_client_secret:
            logger.error("Twitch credentials not provided")
            return False
        
        # Check if we already have a valid token
        if self.access_token and datetime.utcnow() < self.token_expires:
            return True
        
        # Get a new token
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://id.twitch.tv/oauth2/token"
                params = {
                    "client_id": self.twitch_client_id,
                    "client_secret": self.twitch_client_secret,
                    "grant_type": "client_credentials"
                }
                
                async with session.post(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data["access_token"]
                        self.token_expires = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 300)  # 5 minute buffer
                        logger.info("Successfully obtained Twitch API token")
                        return True
                    else:
                        logger.error(f"Failed to get Twitch API token. Status: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error getting Twitch API token: {e}")
            return False
    
    async def check_if_live(self):
        """Check if the Twitch channel is currently live."""
        if not await self.get_twitch_token():
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.twitch.tv/helix/streams"
                headers = {
                    "Client-ID": self.twitch_client_id,
                    "Authorization": f"Bearer {self.access_token}"
                }
                params = {
                    "user_login": self.twitch_channel_name
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        stream_data = data.get("data", [])
                        
                        if stream_data and stream_data[0].get("type") == "live":
                            return stream_data[0]
                        else:
                            return False
                    else:
                        logger.error(f"Failed to check Twitch stream. Status: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error checking Twitch stream: {e}")
            return False
    
    async def send_live_notification(self, stream_data=None):
        """Send a live notification to the announcement channel."""
        for guild in self.bot.guilds:
            # Find the announcement channel
            channel = discord.utils.get(guild.channels, name=self.announcement_channel_name)
            
            if not channel:
                # Try to find a channel with "live" or "announcement" in the name
                for ch in guild.channels:
                    if isinstance(ch, discord.TextChannel) and ("live" in ch.name.lower() or "announcement" in ch.name.lower()):
                        channel = ch
                        break
            
            if channel:
                try:
                    # Build the embed
                    embed = discord.Embed(
                        title="🔴 ChessSafari is Live on Twitch!",
                        description=f"**{stream_data.get('title', 'Chess adventures await!')}**",
                        color=discord.Color.purple(),
                        url=f"https://twitch.tv/{self.twitch_channel_name}"
                    )
                    
                    if stream_data and stream_data.get("thumbnail_url"):
                        # Replace width and height in thumbnail URL
                        thumbnail = stream_data.get("thumbnail_url")
                        thumbnail = thumbnail.replace("{width}", "640").replace("{height}", "360")
                        embed.set_image(url=thumbnail)
                    
                    embed.add_field(
                        name="Playing", 
                        value=stream_data.get("game_name", "Chess") if stream_data else "Chess",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Viewers", 
                        value=stream_data.get("viewer_count", "0") if stream_data else "0",
                        inline=True
                    )
                    
                    embed.set_footer(text="Join the safari adventure! 🦁")
                    
                    # Build the message content with @everyone mention
                    content = "@everyone 🦁 ChessSafari is live on Twitch! Come join the jungle adventure!"
                    
                    await channel.send(content=content, embed=embed)
                    logger.info(f"Sent live notification to {guild.name}")
                    return True
                except Exception as e:
                    logger.error(f"Error sending live notification to {guild.name}: {e}")
            else:
                logger.warning(f"Announcement channel not found in {guild.name}")
        
        return False
    
    @tasks.loop(minutes=5.0)
    async def check_twitch_stream(self):
        """Check if the stream is live every 5 minutes."""
        await self.bot.wait_until_ready()
        
        # Skip check if credentials aren't valid
        if not self.twitch_client_id or not self.twitch_client_secret or self.twitch_client_id == "your_twitch_client_id":
            return
        
        try:
            stream_data = await self.check_if_live()
            
            if stream_data and not self.is_live:
                # Stream just went live
                self.is_live = True
                await self.send_live_notification(stream_data)
                logger.info(f"Stream went live: {stream_data.get('title', 'No title')}")
            elif not stream_data and self.is_live:
                # Stream went offline
                self.is_live = False
                logger.info("Stream went offline")
        except Exception as e:
            logger.error(f"Error in check_twitch_stream task: {e}")

def setup(bot):
    return bot.add_cog(TwitchNotifier(bot))