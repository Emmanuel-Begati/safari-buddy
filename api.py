from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import config
import asyncio
import discord
from discord.ext import commands

# Create FastAPI application
app = FastAPI(
    title="ChessSafari Discord Bot API",
    description="API for interacting with the ChessSafari Discord Bot",
    version="1.0.0"
)

# Store a reference to the bot (will be set in main.py)
bot_instance = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic bot info"""
    return f"""
    <html>
        <head>
            <title>ChessSafari Bot</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                h1 {{
                    color: #7CFC00;
                    text-align: center;
                }}
                .container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 0.8em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <h1>🐘 ChessSafari Discord Bot 🐘</h1>
            <div class="container">
                <h2>Bot Status</h2>
                <p>The ChessSafari Discord Bot is {"online" if bot_instance and bot_instance.is_ready() else "offline"}</p>
                
                <h2>API Endpoints</h2>
                <ul>
                    <li><b>/status</b> - Check the bot status</li>
                    <li><b>/servers</b> - View servers the bot is in</li>
                    <li><b>/go-live</b> - Trigger a live notification (requires API key)</li>
                </ul>
                
                <h2>Bot Features</h2>
                <ul>
                    <li>Community management commands (!coach, !discord, !twitch, etc.)</li>
                    <li>Automatic welcome messages</li>
                    <li>Stream notifications (!live)</li>
                    <li>Activity logging</li>
                </ul>
            </div>
            <div class="footer">
                <p>ChessSafari Bot - Your friendly jungle companion for all things chess! 🌴</p>
            </div>
        </body>
    </html>
    """

@app.get("/status")
async def status():
    """Check the bot status"""
    if not bot_instance:
        return {"status": "Bot reference not set"}
    
    return {
        "status": "online" if bot_instance.is_ready() else "starting up",
        "username": str(bot_instance.user) if bot_instance.is_ready() else None,
        "latency": f"{bot_instance.latency * 1000:.2f}ms" if bot_instance.is_ready() else None
    }

@app.get("/servers")
async def servers():
    """List servers the bot is in"""
    if not bot_instance or not bot_instance.is_ready():
        return {"error": "Bot is not ready"}
    
    guild_list = [{"name": guild.name, "id": guild.id, "member_count": guild.member_count} 
                 for guild in bot_instance.guilds]
    
    return {"server_count": len(guild_list), "servers": guild_list}

@app.post("/go-live")
async def go_live(request: Request):
    """Trigger a live notification in all servers"""
    if not bot_instance or not bot_instance.is_ready():
        return {"error": "Bot is not ready"}
    
    # This would need proper authentication in production
    # Basic implementation for demonstration
    try:
        data = await request.json()
        # You should validate an API key here
        
        success_count = 0
        for guild in bot_instance.guilds:
            general_channel = discord.utils.get(guild.text_channels, name="general")
            if general_channel:
                embed = discord.Embed(
                    title="🔴 ChessSafari is LIVE! 🔴",
                    description=f"I'm live on Twitch! Come join 🐘♟️",
                    color=0x6441A4  # Twitch purple
                )
                embed.add_field(name="Watch Now", value=f"[Join the stream]({config.TWITCH_CHANNEL})", inline=False)
                embed.set_footer(text="🦓 Wild chess moves incoming! 🐘")
                
                await general_channel.send("@everyone", embed=embed)
                success_count += 1
        
        return {"success": True, "message": f"Live notification sent to {success_count} servers"}
    except Exception as e:
        return {"error": f"Failed to send live notification: {str(e)}"}

# Function to start the API server
def run_api(bot=None):
    global bot_instance
    bot_instance = bot
    
    # Run with uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)  # This line should be indented

# If this file is run directly
if __name__ == "__main__":
    run_api()
