import discord
from discord.ext import commands
import asyncio
import os
import config

# Set up intents (permissions)
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member events

# Initialize bot with prefix and intents
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, description=config.BOT_DESCRIPTION)

# List of cogs (extensions) to load
initial_extensions = [
    'bot.commands.general_commands',
    'bot.events.welcome_events',
    'bot.events.logging_events'
]

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord"""
    print(f'\n🌴 {bot.user.name} is online! 🌴')
    print(f'Bot ID: {bot.user.id}')
    print(f'Connected to {len(bot.guilds)} server(s)')
    print('-' * 50)
    
    # Set custom status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="chess in the jungle! 🐘♟️"
        )
    )

async def load_extensions():
    """Load all extensions (cogs)"""
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'Loaded extension: {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')

async def main():
    """Main entry point for the bot"""
    async with bot:
        await load_extensions()
        await bot.start(config.BOT_TOKEN)

# Run the bot
if __name__ == '__main__':
    # Check if token is set
    if not config.BOT_TOKEN:
        print("Error: No bot token found. Please set the DISCORD_TOKEN in your .env file.")
        exit(1)
        
    asyncio.run(main())
