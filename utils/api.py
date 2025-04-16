import discord
from discord.ext import commands
import os
import logging
import asyncio
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("safari_buddy.api")

# Get API key from environment variables
API_KEY = os.getenv("API_KEY", "")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Initialize FastAPI app
app = FastAPI(
    title="Safari Buddy API",
    description="API for ChessSafari Discord Bot",
    version="1.0.0"
)

# Global variable to store a reference to the bot
BOT_INSTANCE = None

# Models
class StatusResponse(BaseModel):
    status: str
    guilds: int
    uptime: str

class LiveNotificationRequest(BaseModel):
    message: Optional[str] = None
    title: Optional[str] = None
    game: Optional[str] = None

# Dependency to check API key
async def get_api_key(api_key: str = Security(api_key_header)):
    if not API_KEY:
        # If no API key is set, allow all requests (not recommended for production)
        logger.warning("No API key set. All API requests will be allowed.")
        return True
    
    if api_key == API_KEY:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API key",
    )

# API routes
@app.get("/", tags=["General"])
async def root():
    return {"message": "Safari Buddy API is running"}

@app.get("/status", tags=["Bot"], response_model=StatusResponse, dependencies=[Depends(get_api_key)])
async def get_status():
    """Get current bot status"""
    if not BOT_INSTANCE:
        raise HTTPException(status_code=503, detail="Bot not connected")
    
    uptime = discord.utils.utcnow() - BOT_INSTANCE.user.created_at
    days, remainder = divmod(int(uptime.total_seconds()), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return {
        "status": "online",
        "guilds": len(BOT_INSTANCE.guilds),
        "uptime": f"{days}d {hours}h {minutes}m {seconds}s"
    }

@app.post("/go-live", tags=["Twitch"], dependencies=[Depends(get_api_key)])
async def trigger_live_notification(request: LiveNotificationRequest = None):
    """Trigger a live notification in all servers"""
    if not BOT_INSTANCE:
        raise HTTPException(status_code=503, detail="Bot not connected")
    
    # Find the TwitchNotifier cog
    twitch_cog = BOT_INSTANCE.get_cog("TwitchNotifier")
    if not twitch_cog:
        raise HTTPException(status_code=503, detail="Twitch notifier not loaded")
    
    # Create a minimal stream data object with the provided information
    stream_data = None
    if request:
        stream_data = {
            "title": request.title or "Chess adventures await!",
            "game_name": request.game or "Chess",
            "viewer_count": 0
        }
    
    # Send the notification
    success = await twitch_cog.send_live_notification(stream_data)
    
    if success:
        return {"status": "success", "message": "Live notification sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification")

def run_api(bot, host="0.0.0.0", port=8000):
    """Run the FastAPI application in a separate thread"""
    global BOT_INSTANCE
    BOT_INSTANCE = bot
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    
    asyncio.create_task(server.serve())
    logger.info(f"API server running at http://{host}:{port}")

class API(commands.Cog):
    """API integration for external services."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Get API configuration from environment variables
        self.api_enabled = os.getenv("API_ENABLED", "false").lower() == "true"
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # Start API if enabled
        if self.api_enabled:
            run_api(bot, self.api_host, self.api_port)
            logger.info(f"API server started on {self.api_host}:{self.api_port}")
        else:
            logger.info("API server disabled")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Log API status when bot is ready."""
        if self.api_enabled:
            logger.info(f"API is available at http://{self.api_host}:{self.api_port}")

def setup(bot):
    return bot.add_cog(API(bot))