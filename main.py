import discord
from discord.ext import commands
import asyncio
import os
import config
import api
import threading

# Initialize bot with all intents
intents = discord.Intents.default()
intents.message_content = True  # For reading message content
intents.members = True          # For member join/leave events
intents.guilds = True           # For server information

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, description=config.BOT_DESCRIPTION)

# Load extensions on startup
async def load_extensions():
    """Load all command and event handlers"""
    # Commands
    await bot.load_extension("bot.commands.general_commands")
    
    # Events
    await bot.load_extension("bot.events.welcome_events")
    await bot.load_extension("bot.events.logging_events")
    
    print("All extensions loaded!")

@bot.event
async def on_ready():
    """Called when the bot is fully logged in and ready to use"""
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f'Connected to {len(bot.guilds)} servers')
    print('------')
    print('🐘 ChessSafari Bot is now online! 🐘')
    
    # Set bot status to show help command info
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{config.PREFIX}help | Chess in the Jungle 🌴"
        )
    )

async def main():
    """Main entry point for the bot"""
    async with bot:
        # Load all extensions before logging in
        await load_extensions()
        
        # Start the bot
        await bot.start(config.BOT_TOKEN)

# Start the API server in a separate thread
def start_api_server():
    """Starts the FastAPI server"""
    api.run_api(bot)  # Make sure you're passing the 'bot' variable here

if __name__ == "__main__":
    # Start API server in a separate thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Run the Discord bot in the main thread
    asyncio.run(main())
