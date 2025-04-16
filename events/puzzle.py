import discord
from discord.ext import commands
import os
import logging
import aiohttp
import asyncio
from datetime import datetime, time, timezone
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("safari_buddy.puzzle")

class ChessPuzzle(commands.Cog):
    """Daily chess puzzles from Lichess."""
    
    def __init__(self, bot):
        self.bot = bot
        self.puzzle_channel_id = os.getenv('PUZZLE_CHANNEL_ID')
        self.scheduler = AsyncIOScheduler()
        self.puzzle_timezone = os.getenv('PUZZLE_TIMEZONE', 'Africa/Johannesburg')  # CAT timezone by default
        self.puzzle_time = os.getenv('PUZZLE_TIME', '08:06')  # Default to 9AM
        
        # Store API base URL
        self.lichess_api_base = "https://lichess.org/api"
        
        # Convert time string to hour and minute
        hour, minute = map(int, self.puzzle_time.split(':'))
        
        # Schedule the daily puzzle
        self.scheduler.add_job(
            self.post_daily_puzzle,
            CronTrigger(hour=hour, minute=minute, timezone=self.puzzle_timezone),
            name="daily_puzzle"
        )
        
        # Start the scheduler
        self.scheduler.start()
        logger.info(f"Daily puzzle scheduler started, will post at {self.puzzle_time} {self.puzzle_timezone}")
    
    def cog_unload(self):
        """Clean up when the cog is unloaded."""
        self.scheduler.shutdown()
    
    async def fetch_daily_puzzle(self):
        """Fetch the daily puzzle from Lichess API."""
        url = f"{self.lichess_api_base}/puzzle/daily"
        headers = {"Accept": "application/json"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Log the entire response for debugging
                        logger.debug(f"Daily puzzle response: {data}")
                        
                        # Check if we have puzzle data with ID
                        if 'puzzle' in data and 'id' in data['puzzle']:
                            logger.info(f"Successfully fetched daily puzzle: {data['puzzle']['id']}")
                            return data
                        else:
                            logger.error(f"Puzzle data structure is unexpected: {data}")
                            return None
                    else:
                        logger.error(f"Failed to fetch daily puzzle. Status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching daily puzzle: {e}")
            return None
    
    async def fetch_puzzle_by_id(self, puzzle_id):
        """Fetch a specific puzzle by ID from Lichess API."""
        url = f"{self.lichess_api_base}/puzzle/{puzzle_id}"
        headers = {"Accept": "application/json"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Log the entire response for debugging
                        logger.debug(f"Puzzle by ID response: {data}")
                        
                        # Check if we have puzzle data
                        if 'puzzle' in data:
                            logger.info(f"Successfully fetched puzzle by ID: {puzzle_id}")
                            return data
                        else:
                            logger.error(f"Puzzle data structure is unexpected for ID {puzzle_id}: {data}")
                            return None
                    else:
                        logger.error(f"Failed to fetch puzzle by ID {puzzle_id}. Status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching puzzle by ID: {e}")
            return None
    
    async def fetch_random_puzzle(self, rating_min=1500, rating_max=2000):
        """Fetch a random puzzle within rating range from Lichess API."""
        url = f"{self.lichess_api_base}/puzzle/random"
        headers = {"Accept": "application/json"}
        params = {"min": rating_min, "max": rating_max}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Log the entire response for debugging
                        logger.debug(f"Random puzzle response: {data}")
                        
                        # Check if we have puzzle data with ID
                        if 'puzzle' in data and 'id' in data['puzzle']:
                            logger.info(f"Successfully fetched random puzzle: {data['puzzle']['id']}")
                            return data
                        else:
                            logger.error(f"Random puzzle data structure is unexpected: {data}")
                            return None
                    else:
                        logger.error(f"Failed to fetch random puzzle. Status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching random puzzle: {e}")
            return None
    
    async def post_daily_puzzle(self):
        """Post the daily puzzle to the designated channel."""
        if not self.puzzle_channel_id:
            logger.warning("No puzzle channel ID configured. Skipping daily puzzle.")
            return
        
        # Try to get the channel from all guilds
        channel = None
        for guild in self.bot.guilds:
            channel = guild.get_channel(int(self.puzzle_channel_id))
            if channel:
                break
        
        if not channel:
            logger.error(f"Could not find channel with ID {self.puzzle_channel_id}")
            return
        
        # Fetch the puzzle
        puzzle_data = await self.fetch_daily_puzzle()
        if not puzzle_data:
            logger.error("Failed to post daily puzzle due to fetch error.")
            # Schedule a retry in 30 minutes
            asyncio.create_task(self.retry_post_puzzle(30))
            return
        
        try:
            # Extract puzzle information with error handling
            if 'puzzle' not in puzzle_data:
                logger.error(f"Unexpected puzzle data format: {puzzle_data}")
                # Schedule a retry in 15 minutes
                asyncio.create_task(self.retry_post_puzzle(15))
                return
                
            puzzle = puzzle_data['puzzle']
            puzzle_id = puzzle.get('id', 'Unknown')
            
            # Log the data structure for debugging
            logger.debug(f"Daily puzzle data structure: {puzzle_data}")
            
            # Extract data with proper error handling
            puzzle_fen = puzzle.get('fen')
            
            if not puzzle_fen:
                # Try alternative field names or structure
                if 'game' in puzzle_data and 'fen' in puzzle_data['game']:
                    puzzle_fen = puzzle_data['game']['fen']
                else:
                    # Use a default message if FEN is not available
                    puzzle_fen = "FEN not available"
            
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_plays = puzzle.get('plays', 0)
            puzzle_solution = puzzle.get('solution', [])
            game_url = puzzle_data.get('game', {}).get('url', f"https://lichess.org/training/{puzzle_id}")
            
            # Create puzzle image URL
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            
            # Create the embed
            embed = discord.Embed(
                title=f"🧩 Daily Chess Puzzle - {datetime.now().strftime('%B %d, %Y')}",
                description="Test your skills with today's chess puzzle from Lichess!",
                color=discord.Color.gold(),
                url=f"https://lichess.org/training/{puzzle_id}"
            )
            
            embed.add_field(name="Rating", value=str(puzzle_rating), inline=True)
            embed.add_field(name="Played", value=f"{puzzle_plays} times", inline=True)
            embed.add_field(name="Puzzle ID", value=f"`{puzzle_id}`", inline=True)
            
            if puzzle_fen and puzzle_fen != "FEN not available":
                embed.add_field(name="Position (FEN)", value=f"`{puzzle_fen}`", inline=False)
                
            embed.add_field(name="Instructions", value="Find the best move sequence! Click the link in the title to solve on Lichess. React with 🔍 to reveal the solution.", inline=False)
            embed.set_image(url=puzzle_image_url)
            embed.set_footer(text=f"Puzzle ID: {puzzle_id} • From a game played on Lichess")
            
            # Send the initial message
            message = await channel.send(embed=embed)
            
            # Add reaction for solution
            await message.add_reaction("🔍")
            
            # Store the solution for later
            self.bot.puzzle_solutions = getattr(self.bot, "puzzle_solutions", {})
            self.bot.puzzle_solutions[message.id] = {
                "solution": puzzle_solution, 
                "puzzle_id": puzzle_id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"Posted daily puzzle {puzzle_id} to {channel.name}")
        except Exception as e:
            logger.error(f"Error posting daily puzzle: {e}", exc_info=True)
            # Schedule a retry in 15 minutes
            asyncio.create_task(self.retry_post_puzzle(15))
    
    async def retry_post_puzzle(self, minutes):
        """Retry posting the puzzle after a delay."""
        logger.info(f"Scheduling puzzle post retry in {minutes} minutes")
        await asyncio.sleep(minutes * 60)
        await self.post_daily_puzzle()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions to reveal puzzle solutions."""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is a reaction to a puzzle
        if not hasattr(self.bot, "puzzle_solutions") or payload.message_id not in self.bot.puzzle_solutions:
            return
        
        # Check if this is the solution reaction
        if str(payload.emoji) != "🔍":
            return
        
        # Get the solution data
        solution_data = self.bot.puzzle_solutions[payload.message_id]
        puzzle_id = solution_data["puzzle_id"]
        solution = solution_data["solution"]
        
        # Get the channel and message
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        # Create solution embed
        embed = discord.Embed(
            title=f"🧩 Solution for Puzzle {puzzle_id}",
            description="Here's the solution to the daily puzzle:",
            color=discord.Color.green()
        )
        
        # Format solution moves
        solution_text = ""
        for i, move in enumerate(solution):
            solution_text += f"{i+1}. {move}\n"
        
        embed.add_field(name="Winning Sequence", value=f"```{solution_text}```", inline=False)
        embed.add_field(name="Play on Lichess", value=f"[Click here to try this puzzle](https://lichess.org/training/{puzzle_id})", inline=False)
        
        # Send as reply to original message
        await message.reply(embed=embed)
        
        # Remove the user's reaction to keep things tidy
        try:
            await message.remove_reaction("🔍", payload.member)
        except Exception:
            pass
    
    @discord.slash_command(name="puzzle", description="Get today's daily chess puzzle from Lichess")
    async def puzzle_slash(self, ctx):
        # Only defer if this is an interaction (slash command)
        if hasattr(ctx, "defer") and callable(ctx.defer):
            try:
                await ctx.defer()
            except Exception:
                pass  # Ignore if already responded or can't defer
        try:
            # Fetch the puzzle
            puzzle_data = await self.fetch_daily_puzzle()
            if not puzzle_data:
                await ctx.respond("❌ Failed to fetch today's puzzle from Lichess. Please try again later.")
                return
            
            # Post the puzzle (reusing same code as scheduled function)
            # Extract puzzle information with error handling
            puzzle_id = puzzle_data.get('puzzle', {}).get('id', 'Unknown')
            
            # Debug the puzzle data structure
            logger.debug(f"Puzzle data structure: {puzzle_data}")
            
            # Check if the puzzle data has the expected structure
            if 'puzzle' not in puzzle_data:
                await ctx.followup.send("❌ Received unexpected data format from Lichess API. Please try again later.")
                logger.error(f"Unexpected puzzle data format: {puzzle_data}")
                return
            
            # Extract data with proper error handling
            puzzle = puzzle_data['puzzle']
            puzzle_fen = puzzle.get('fen')
            
            if not puzzle_fen:
                # Try alternative field names or structure
                if 'game' in puzzle_data and 'fen' in puzzle_data['game']:
                    puzzle_fen = puzzle_data['game']['fen']
                else:
                    # Use a default message if FEN is not available
                    puzzle_fen = "FEN not available"
            
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_plays = puzzle.get('plays', 0)
            puzzle_solution = puzzle.get('solution', [])
            game_url = puzzle_data.get('game', {}).get('url', f"https://lichess.org/training/{puzzle_id}")
            
            # Create puzzle image URL
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            
            # Create the embed
            embed = discord.Embed(
                title=f"🧩 Daily Chess Puzzle - {datetime.now().strftime('%B %d, %Y')}",
                description="Test your skills with today's chess puzzle from Lichess!",
                color=discord.Color.gold(),
                url=f"https://lichess.org/training/{puzzle_id}"
            )
            
            embed.add_field(name="Rating", value=str(puzzle_rating), inline=True)
            embed.add_field(name="Played", value=f"{puzzle_plays} times", inline=True)
            embed.add_field(name="Puzzle ID", value=f"`{puzzle_id}`", inline=True)
            
            if puzzle_fen:
                embed.add_field(name="Position (FEN)", value=f"`{puzzle_fen}`", inline=False)
                
            embed.add_field(name="Instructions", value="Find the best move sequence! Click the link in the title to solve on Lichess. React with 🔍 to reveal the solution.", inline=False)
            embed.set_image(url=puzzle_image_url)
            embed.set_footer(text=f"Puzzle ID: {puzzle_id} • From a game played on Lichess")
            
            # Send the message using followup since we deferred earlier
            message = await ctx.followup.send(embed=embed)
            
            # Add reaction for solution
            await message.add_reaction("🔍")
            
            # Store the solution for later
            self.bot.puzzle_solutions = getattr(self.bot, "puzzle_solutions", {})
            self.bot.puzzle_solutions[message.id] = {
                "solution": puzzle_solution, 
                "puzzle_id": puzzle_id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"Posted puzzle {puzzle_id} via command")
        except Exception as e:
            logger.error(f"Error posting puzzle via command: {e}", exc_info=True)
            # Use followup for error message since we deferred earlier
            try:
                await ctx.followup.send("❌ An error occurred while posting the puzzle. Please try again later.")
            except:
                logger.error("Failed to send error message to user")
    
    @discord.slash_command(name="puzzleid", description="Get a specific puzzle by ID from Lichess")
    async def puzzle_id_slash(self, ctx, puzzle_id: discord.Option(str, "Lichess puzzle ID", required=True)):
        """Slash command to fetch and post a specific puzzle by ID."""
        # Defer first to give us time to fetch the puzzle
        await ctx.defer()
        
        # Fetch the puzzle by ID
        puzzle_data = await self.fetch_puzzle_by_id(puzzle_id)
        if not puzzle_data:
            await ctx.followup.send(f"❌ Failed to fetch puzzle with ID `{puzzle_id}` from Lichess. Please check the ID and try again.")
            return
        
        # Post the puzzle with the same format as the daily puzzle
        try:
            # Log the data structure for debugging
            logger.debug(f"Puzzle ID data structure: {puzzle_data}")
            
            # Check if the puzzle data has the expected structure
            if 'puzzle' not in puzzle_data:
                await ctx.followup.send(f"❌ Received unexpected data format from Lichess API for puzzle ID {puzzle_id}. Please try again later.")
                logger.error(f"Unexpected puzzle data format for ID {puzzle_id}: {puzzle_data}")
                return
            
            # Extract data with proper error handling
            puzzle = puzzle_data['puzzle']
            puzzle_fen = puzzle.get('fen')
            
            if not puzzle_fen:
                # Try alternative field names or structure
                if 'game' in puzzle_data and 'fen' in puzzle_data['game']:
                    puzzle_fen = puzzle_data['game']['fen']
                else:
                    # Use a default message if FEN is not available
                    puzzle_fen = "FEN not available"
            
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_plays = puzzle.get('plays', 0)
            puzzle_solution = puzzle.get('solution', [])
            
            # Create puzzle image URL
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            
            # Create the embed
            embed = discord.Embed(
                title=f"🧩 Chess Puzzle {puzzle_id}",
                description="Test your skills with this chess puzzle from Lichess!",
                color=discord.Color.gold(),
                url=f"https://lichess.org/training/{puzzle_id}"
            )
            
            embed.add_field(name="Rating", value=str(puzzle_rating), inline=True)
            if puzzle_plays:
                embed.add_field(name="Played", value=f"{puzzle_plays} times", inline=True)
            embed.add_field(name="Puzzle ID", value=f"`{puzzle_id}`", inline=True)
            
            if puzzle_fen and puzzle_fen != "FEN not available":
                embed.add_field(name="Position (FEN)", value=f"`{puzzle_fen}`", inline=False)
                
            embed.add_field(name="Instructions", value="Find the best move sequence! Click the link in the title to solve on Lichess. React with 🔍 to reveal the solution.", inline=False)
            embed.set_image(url=puzzle_image_url)
            embed.set_footer(text=f"Puzzle ID: {puzzle_id} • From a game played on Lichess")
            
            # Send the message using followup since we deferred earlier
            message = await ctx.followup.send(embed=embed)
            
            # Add reaction for solution
            await message.add_reaction("🔍")
            
            # Store the solution for later
            self.bot.puzzle_solutions = getattr(self.bot, "puzzle_solutions", {})
            self.bot.puzzle_solutions[message.id] = {
                "solution": puzzle_solution, 
                "puzzle_id": puzzle_id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"Posted puzzle {puzzle_id} via ID command")
        except Exception as e:
            logger.error(f"Error posting puzzle via ID command: {e}", exc_info=True)
            # Use followup for error since we deferred earlier
            try:
                await ctx.followup.send("❌ An error occurred while posting the puzzle. Please try again later.")
            except:
                logger.error("Failed to send error message to user")
    
    @discord.slash_command(name="randompuzzle", description="Get a random puzzle from Lichess")
    async def random_puzzle_slash(self, ctx, 
                                  min_rating: discord.Option(int, "Minimum rating", required=False, default=1500),
                                  max_rating: discord.Option(int, "Maximum rating", required=False, default=2000)):
        """Slash command to fetch and post a random puzzle within a rating range."""
        # Defer first to give us time to fetch the puzzle
        await ctx.defer()
        
        # Validate rating range
        if min_rating < 600 or min_rating > 3000:
            min_rating = 1500
        if max_rating < 600 or max_rating > 3000 or max_rating < min_rating:
            max_rating = min_rating + 500
            if max_rating > 3000:
                max_rating = 3000
        
        # Fetch a random puzzle
        puzzle_data = await self.fetch_random_puzzle(min_rating, max_rating)
        if not puzzle_data:
            await ctx.followup.send("❌ Failed to fetch a random puzzle from Lichess. Please try again later.")
            return
        
        # Post the random puzzle with the same format as the daily puzzle
        try:
            # Log the data structure for debugging
            logger.debug(f"Random puzzle data structure: {puzzle_data}")
            
            # Check if the puzzle data has the expected structure
            if 'puzzle' not in puzzle_data:
                await ctx.followup.send("❌ Received unexpected data format from Lichess API. Please try again later.")
                logger.error(f"Unexpected random puzzle data format: {puzzle_data}")
                return
            
            # Extract data with proper error handling
            puzzle = puzzle_data['puzzle']
            puzzle_id = puzzle.get('id', 'Unknown')
            puzzle_fen = puzzle.get('fen')
            
            if not puzzle_fen:
                # Try alternative field names or structure
                if 'game' in puzzle_data and 'fen' in puzzle_data['game']:
                    puzzle_fen = puzzle_data['game']['fen']
                else:
                    # Use a default message if FEN is not available
                    puzzle_fen = "FEN not available"
            
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_solution = puzzle.get('solution', [])
            
            # Create puzzle image URL
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            
            # Create the embed
            embed = discord.Embed(
                title=f"🧩 Random Chess Puzzle (Rating: {puzzle_rating})",
                description=f"Test your skills with this random puzzle from Lichess!",
                color=discord.Color.gold(),
                url=f"https://lichess.org/training/{puzzle_id}"
            )
            
            embed.add_field(name="Rating", value=str(puzzle_rating), inline=True)
            embed.add_field(name="Rating Range", value=f"{min_rating}-{max_rating}", inline=True)
            embed.add_field(name="Puzzle ID", value=f"`{puzzle_id}`", inline=True)
            
            if puzzle_fen and puzzle_fen != "FEN not available":
                embed.add_field(name="Position (FEN)", value=f"`{puzzle_fen}`", inline=False)
                
            embed.add_field(name="Instructions", value="Find the best move sequence! Click the link in the title to solve on Lichess. React with 🔍 to reveal the solution.", inline=False)
            embed.set_image(url=puzzle_image_url)
            embed.set_footer(text=f"Puzzle ID: {puzzle_id} • From a game played on Lichess")
            
            # Send the message using followup since we deferred earlier
            message = await ctx.followup.send(embed=embed)
            
            # Add reaction for solution
            await message.add_reaction("🔍")
            
            # Store the solution for later
            self.bot.puzzle_solutions = getattr(self.bot, "puzzle_solutions", {})
            self.bot.puzzle_solutions[message.id] = {
                "solution": puzzle_solution, 
                "puzzle_id": puzzle_id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"Posted random puzzle {puzzle_id} with rating {puzzle_rating}")
        except Exception as e:
            logger.error(f"Error posting random puzzle: {e}", exc_info=True)
            # Use followup for error since we deferred earlier
            try:
                await ctx.followup.send("❌ An error occurred while posting the puzzle. Please try again later.")
            except:
                logger.error("Failed to send error message to user")
    
    # Traditional prefix commands for compatibility
    @commands.command(name="puzzle")
    async def puzzle_prefix(self, ctx):
        """Traditional command to manually fetch and post today's puzzle."""
        # Do NOT call the slash command handler directly
        try:
            puzzle_data = await self.fetch_daily_puzzle()
            if not puzzle_data:
                await ctx.send("❌ Failed to fetch today's puzzle from Lichess. Please try again later.")
                return
            if 'puzzle' not in puzzle_data:
                await ctx.send("❌ Received unexpected data format from Lichess API. Please try again later.")
                logger.error(f"Unexpected puzzle data format: {puzzle_data}")
                return
            puzzle = puzzle_data['puzzle']
            puzzle_id = puzzle.get('id', 'Unknown')
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            await ctx.send(f"🧩 **Today's Chess Puzzle**\nRating: {puzzle_rating}\nPuzzle ID: `{puzzle_id}`\nSolve: https://lichess.org/training/{puzzle_id}\n{puzzle_image_url}")
        except Exception as e:
            logger.error(f"Error posting puzzle via prefix command: {e}")
            await ctx.send("❌ An error occurred while posting the puzzle. Please try again later.")
    
    @commands.command(name="puzzleid")
    async def puzzle_id_prefix(self, ctx, puzzle_id: str = None):
        """Traditional command to fetch and post a specific puzzle by ID."""
        if not puzzle_id:
            await ctx.send("⚠️ Please provide a puzzle ID. Example: `!puzzleid 12345`")
            return
        
        try:
            # Fetch the puzzle by ID
            puzzle_data = await self.fetch_puzzle_by_id(puzzle_id)
            if not puzzle_data:
                await ctx.send(f"❌ Failed to fetch puzzle with ID `{puzzle_id}` from Lichess. Please check the ID and try again.")
                return
            
            # Post the puzzle with the same format as the daily puzzle
            # Log the data structure for debugging
            logger.debug(f"Puzzle ID data structure: {puzzle_data}")
            
            # Check if the puzzle data has the expected structure
            if 'puzzle' not in puzzle_data:
                await ctx.send(f"❌ Received unexpected data format from Lichess API for puzzle ID {puzzle_id}. Please try again later.")
                logger.error(f"Unexpected puzzle data format for ID {puzzle_id}: {puzzle_data}")
                return
            
            # Extract data with proper error handling
            puzzle = puzzle_data['puzzle']
            puzzle_fen = puzzle.get('fen')
            
            if not puzzle_fen:
                # Try alternative field names or structure
                if 'game' in puzzle_data and 'fen' in puzzle_data['game']:
                    puzzle_fen = puzzle_data['game']['fen']
                else:
                    # Use a default message if FEN is not available
                    puzzle_fen = "FEN not available"
            
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_plays = puzzle.get('plays', 0)
            puzzle_solution = puzzle.get('solution', [])
            
            # Create puzzle image URL
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            
            # Create the embed
            embed = discord.Embed(
                title=f"🧩 Chess Puzzle {puzzle_id}",
                description="Test your skills with this chess puzzle from Lichess!",
                color=discord.Color.gold(),
                url=f"https://lichess.org/training/{puzzle_id}"
            )
            
            embed.add_field(name="Rating", value=str(puzzle_rating), inline=True)
            if puzzle_plays:
                embed.add_field(name="Played", value=f"{puzzle_plays} times", inline=True)
            embed.add_field(name="Puzzle ID", value=f"`{puzzle_id}`", inline=True)
            
            if puzzle_fen and puzzle_fen != "FEN not available":
                embed.add_field(name="Position (FEN)", value=f"`{puzzle_fen}`", inline=False)
                
            embed.add_field(name="Instructions", value="Find the best move sequence! Click the link in the title to solve on Lichess. React with 🔍 to reveal the solution.", inline=False)
            embed.set_image(url=puzzle_image_url)
            embed.set_footer(text=f"Puzzle ID: {puzzle_id} • From a game played on Lichess")
            
            # Send the message
            message = await ctx.send(embed=embed)
            
            # Add reaction for solution
            await message.add_reaction("🔍")
            
            # Store the solution for later
            self.bot.puzzle_solutions = getattr(self.bot, "puzzle_solutions", {})
            self.bot.puzzle_solutions[message.id] = {
                "solution": puzzle_solution, 
                "puzzle_id": puzzle_id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"Posted puzzle {puzzle_id} via ID command")
        except Exception as e:
            logger.error(f"Error posting puzzle via ID command: {e}", exc_info=True)
            await ctx.send("❌ An error occurred while posting the puzzle. Please try again later.")
    
    @commands.command(name="randompuzzle")
    async def random_puzzle_prefix(self, ctx, min_rating: int = 1500, max_rating: int = 2000):
        """Traditional command to fetch and post a random puzzle within a rating range."""
        try:
            # Validate rating range
            if min_rating < 600 or min_rating > 3000:
                min_rating = 1500
            if max_rating < 600 or max_rating > 3000 or max_rating < min_rating:
                max_rating = min_rating + 500
                if max_rating > 3000:
                    max_rating = 3000
            
            # Fetch a random puzzle
            puzzle_data = await self.fetch_random_puzzle(min_rating, max_rating)
            if not puzzle_data:
                await ctx.send("❌ Failed to fetch a random puzzle from Lichess. Please try again later.")
                return
            
            # Post the random puzzle with the same format as the daily puzzle
            # Log the data structure for debugging
            logger.debug(f"Random puzzle data structure: {puzzle_data}")
            
            # Check if the puzzle data has the expected structure
            if 'puzzle' not in puzzle_data:
                await ctx.send("❌ Received unexpected data format from Lichess API. Please try again later.")
                logger.error(f"Unexpected random puzzle data format: {puzzle_data}")
                return
            
            # Extract data with proper error handling
            puzzle = puzzle_data['puzzle']
            puzzle_id = puzzle.get('id', 'Unknown')
            puzzle_fen = puzzle.get('fen')
            
            if not puzzle_fen:
                # Try alternative field names or structure
                if 'game' in puzzle_data and 'fen' in puzzle_data['game']:
                    puzzle_fen = puzzle_data['game']['fen']
                else:
                    # Use a default message if FEN is not available
                    puzzle_fen = "FEN not available"
            
            puzzle_rating = puzzle.get('rating', 'Unknown')
            puzzle_solution = puzzle.get('solution', [])
            
            # Create puzzle image URL
            puzzle_image_url = f"https://lichess1.org/game/export/gif/puzzle/{puzzle_id}.gif"
            
            # Create the embed
            embed = discord.Embed(
                title=f"🧩 Random Chess Puzzle (Rating: {puzzle_rating})",
                description=f"Test your skills with this random puzzle from Lichess!",
                color=discord.Color.gold(),
                url=f"https://lichess.org/training/{puzzle_id}"
            )
            
            embed.add_field(name="Rating", value=str(puzzle_rating), inline=True)
            embed.add_field(name="Rating Range", value=f"{min_rating}-{max_rating}", inline=True)
            embed.add_field(name="Puzzle ID", value=f"`{puzzle_id}`", inline=True)
            
            if puzzle_fen and puzzle_fen != "FEN not available":
                embed.add_field(name="Position (FEN)", value=f"`{puzzle_fen}`", inline=False)
                
            embed.add_field(name="Instructions", value="Find the best move sequence! Click the link in the title to solve on Lichess. React with 🔍 to reveal the solution.", inline=False)
            embed.set_image(url=puzzle_image_url)
            embed.set_footer(text=f"Puzzle ID: {puzzle_id} • From a game played on Lichess")
            
            # Send the message
            message = await ctx.send(embed=embed)
            
            # Add reaction for solution
            await message.add_reaction("🔍")
            
            # Store the solution for later
            self.bot.puzzle_solutions = getattr(self.bot, "puzzle_solutions", {})
            self.bot.puzzle_solutions[message.id] = {
                "solution": puzzle_solution, 
                "puzzle_id": puzzle_id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"Posted random puzzle {puzzle_id} with rating {puzzle_rating}")
        except Exception as e:
            logger.error(f"Error posting random puzzle: {e}", exc_info=True)
            await ctx.send("❌ An error occurred while posting the puzzle. Please try again later.")

def setup(bot):
    return bot.add_cog(ChessPuzzle(bot))