import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
PREFIX = "!"
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# Links for commands
COACH_LINK = os.getenv("COACH_LINK")
DISCORD_INVITE = os.getenv("DISCORD_INVITE")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
YOUTUBE_CHANNEL = os.getenv("YOUTUBE_CHANNEL")
INSTAGRAM_PROFILE = os.getenv("INSTAGRAM_PROFILE")

# Channel names
WELCOME_CHANNEL = "welcome"
LOGS_CHANNEL = "logs"

# Bot customization
BOT_NAME = "ChessSafari Buddy"
BOT_DESCRIPTION = "Your friendly jungle companion for all things chess!"
