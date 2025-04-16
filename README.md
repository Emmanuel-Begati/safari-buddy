# ChessSafari Discord Bot 🐘♟️

A custom Discord bot for managing the ChessSafari community with chess-jungle vibes and helpful commands! This bot uses FastAPI to provide a web interface in addition to Discord functionality.

## 🌴 Features

- **Custom Commands**:
  - `!coach` - Sends information about chess coaching services
  - `!discord` - Shares the Discord server invite link
  - `!twitch` - Links to the Twitch channel for chess streams
  - `!youtube` - Links to the YouTube channel for chess content
  - `!insta` - Shares the Instagram profile
  - `!live` - Announces when the stream is live on Twitch

- **Automatic Welcome Messages**:
  - Sends a personalized welcome message in the `#welcome` channel when new members join
  - Safari-themed emojis and friendly messages

- **Activity Logging**:
  - Logs member joins, leaves, and deleted messages in a dedicated `#logs` channel
  - Keeps track of server activity for moderation purposes

- **Web API and Interface**:
  - FastAPI integration for a web presence
  - REST API endpoints to check bot status and control functions
  - Web dashboard for basic monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- A Discord Bot Token (from the [Discord Developer Portal](https://discord.com/developers/applications))
- Proper bot permissions and intents enabled

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/chess-safari-bot.git
cd chess-safari-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory with the following content:

```
# Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# Links for Commands
COACH_LINK=https://example.com/chess-coaching
DISCORD_INVITE=https://discord.gg/yourinvite
TWITCH_CHANNEL=https://twitch.tv/chesssafari
YOUTUBE_CHANNEL=https://youtube.com/c/chesssafari
INSTAGRAM_PROFILE=https://instagram.com/chesssafari
```

Replace the placeholders with your actual links and token.

### 4. Enable required intents in Discord Developer Portal

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to the "Bot" section
4. Under "Privileged Gateway Intents", enable:
   - Server Members Intent
   - Message Content Intent
5. Save changes

### 5. Run the bot

```bash
python main.py
```

The bot will start running on Discord, and the FastAPI web server will be available at http://localhost:8000.

## 💻 Using the Web API

The bot includes a FastAPI web server with several endpoints:

- `GET /` - Homepage with bot information
- `GET /status` - Check the bot's online status
- `GET /servers` - List the servers the bot is in
- `POST /go-live` - Trigger a stream notification (requires proper authentication)

You can access the web dashboard by navigating to http://localhost:8000 in your browser.

## 🛠️ Customizing and Extending

### Adding New Commands

1. Open `bot/commands/general_commands.py` (or create a new commands file)
2. Add a new command using the Discord.py command decorator format:

```python
@commands.command(name="command_name")
async def your_command(self, ctx):
    """Command description for help text"""
    # Your command logic here
    await ctx.send("Your response")
```

3. For more complex commands, use Discord embeds for better formatting

### Modifying Welcome Messages

Edit the `bot/events/welcome_events.py` file to customize the welcome message format, content, and appearance.

## 🌐 Deployment Options

### Replit

1. Create a new Replit project
2. Upload your bot files or connect to your Git repository
3. Add your `.env` variables in the Replit Secrets tab
4. Set the "Run" command to `python main.py`
5. Use Replit's Always On feature (or UptimeRobot) to keep your bot running

### Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Add environment variables in the Railway dashboard
4. Railway will automatically deploy your bot
5. Railway provides enough free resources to keep your bot online

### Hosting with FastAPI

To expose your bot's API to the internet safely, consider:

1. Using a reverse proxy like Nginx
2. Adding proper authentication to API endpoints
3. Setting up HTTPS with a service like Let's Encrypt

## 📚 Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Discord Developer Portal](https://discord.com/developers/applications)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with 🧡 for the ChessSafari community
