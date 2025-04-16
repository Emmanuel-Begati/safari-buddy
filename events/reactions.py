import discord
from discord.ext import commands
import logging
import re

logger = logging.getLogger("safari_buddy.reactions")

class Reactions(commands.Cog):
    """Handles emoji reactions to messages with certain keywords."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Define keyword-to-emoji mappings
        self.reaction_triggers = {
            r"checkmate": "🫡",
            r"chess": "♟️",
            r"queen": "👑", 
            r"king": "🤴",
            r"safari": "🦁",
            r"jungle": "🌴",
            r"banana": "🍌",
            r"victory": "🏆",
            r"tournament": "🏅",
            r"rating": "📈",
            r"blunder": "😱",
            r"brilliant": "💫",
            r"puzzle": "🧩"
        }
        
        # Compile regex patterns for efficiency
        self.patterns = {keyword: re.compile(rf"\b{keyword}\b", re.IGNORECASE) 
                        for keyword in self.reaction_triggers}
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and add reactions based on keywords."""
        # Skip bot messages
        if message.author.bot:
            return
        
        # Skip command messages
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        
        # Check for trigger words and add reactions
        for keyword, pattern in self.patterns.items():
            if pattern.search(message.content):
                try:
                    emoji = self.reaction_triggers[keyword]
                    await message.add_reaction(emoji)
                    logger.debug(f"Added {emoji} reaction to message containing '{keyword}'")
                except discord.errors.HTTPException as e:
                    logger.error(f"Error adding reaction: {e}")

def setup(bot):
    return bot.add_cog(Reactions(bot))