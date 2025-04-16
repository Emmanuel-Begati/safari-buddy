import os
import logging
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("safari_buddy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("safari_buddy")

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize bot with slash commands
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="the safari 🦁"
        )
    )
    
    # Register the application commands
    try:
        synced = await bot.sync_commands()
        if synced:
            logger.info(f"Synced {len(synced)} command(s)")
        else:
            logger.info("Command sync completed, but no commands were returned")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
    
    logger.info("Bot is ready!")

async def load_extensions():
    """Load all cogs from the commands and events directories."""
    # Load command cogs
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            bot.load_extension(f'commands.{filename[:-3]}')
            logger.info(f'Loaded command extension: {filename[:-3]}')
    
    # Load event cogs
    for filename in os.listdir('./events'):
        if filename.endswith('.py'):
            bot.load_extension(f'events.{filename[:-3]}')
            logger.info(f'Loaded event extension: {filename[:-3]}')
    
    # Load API extension if exists
    if os.path.exists('./utils/api.py'):
        bot.load_extension('utils.api')
        logger.info('Loaded API extension')

async def main():
    """Main entry point for the bot."""
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    if not TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables. Please check your .env file.")
        exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)