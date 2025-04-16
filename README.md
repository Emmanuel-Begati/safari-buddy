# 🦁 Safari Buddy

A high-quality Discord bot for the ChessSafari community, built using py-cord.

## 🌴 Features

- **Slash Commands & Traditional Commands**
  - `/coach` (or `!coach`): Get coaching information
  - `/discord` (or `!discord`): Get invite link to the Discord server 
  - `/twitch` (or `!twitch`): Get link to ChessSafari's Twitch channel
  - `/youtube` (or `!youtube`): Get link to ChessSafari's YouTube channel
  - `/instagram` (or `!instagram`): Get link to ChessSafari's Instagram
  - `/status` (or `!status`): Check the bot's current status
  - `/chessfact` (or `!chessfact`): Get a random chess fact
  - `/puzzle` (or `!puzzle`): Get today's daily chess puzzle from Lichess

- **Auto-welcome New Members**
  - Sends a fun welcome message in the `#welcome` channel
  - Includes a custom safari-themed greeting with emoji branding

- **Activity Logging**
  - Logs joins, leaves, message deletes, and edits in `#mod-logs`
  - Detailed logging with timestamps and user information

- **Twitch Stream Notifications**
  - Automatically detects when ChessSafari goes live on Twitch
  - Posts an announcement in the `#live-now` channel with stream details
  - Admin command `/go-live` to manually trigger stream notifications

- **Daily Chess Puzzles**
  - Automatically posts the Lichess daily puzzle at a scheduled time
  - Includes puzzle image, rating, and instructions
  - Spoiler-free format with reaction-based solution reveal
  - Manual `/puzzle` command to get today's puzzle on demand

- **API Endpoint**
  - Secure `/go-live` endpoint for triggering stream notifications from external tools
  - `/status` endpoint to check the bot's status

- **Fun Extras**
  - Emoji reactions to chess and safari-themed keywords
  - Chess facts command for random chess trivia

## 📋 Requirements

- Python 3.8 or higher
- Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)
- Twitch API credentials (for stream notifications)

## 🛠️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/safari-buddy.git
cd safari-buddy
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Copy the example .env file and modify it with your own values:

```bash
cp .env.example .env
```

Then edit the `.env` file to add your:
- Discord bot token
- Twitch API credentials
- Social media links
- Other configuration options

## 🚀 Running the Bot

### Local Hosting

```bash
python main.py
```

### Hosting on Replit

1. Create a new Replit project and import your code
2. Add your `.env` values in the Replit Secrets tab
3. Set the run command to `python main.py`

### Hosting on Railway

1. Connect your GitHub repository to Railway
2. Add your `.env` variables in the Railway environment variables
3. Railway will automatically deploy your bot

## 🔧 Configuration

All bot configuration is done through environment variables in the `.env` file:

### Discord Configuration
- `DISCORD_TOKEN`: Your Discord bot token
- `COMMAND_PREFIX`: Prefix for traditional commands (default: `!`)

### Social Links
- `COACH_LINK`: Link to ChessSafari's coaching page
- `DISCORD_LINK`: Discord invite link
- `TWITCH_LINK`: Link to Twitch channel
- `YOUTUBE_LINK`: Link to YouTube channel
- `INSTAGRAM_LINK`: Link to Instagram profile

### Twitch Configuration
- `TWITCH_CLIENT_ID`: Your Twitch application client ID
- `TWITCH_CLIENT_SECRET`: Your Twitch application client secret
- `TWITCH_CHANNEL`: Twitch channel name to monitor
- `ANNOUNCEMENT_CHANNEL`: Discord channel for live announcements

### Daily Chess Puzzle Configuration
- `PUZZLE_CHANNEL_ID`: The channel ID where daily puzzles will be posted
- `PUZZLE_TIMEZONE`: The timezone for scheduling puzzle posts (default: "Africa/Johannesburg")
- `PUZZLE_TIME`: The time of day to post puzzles in 24h format (default: "09:00")

### API Configuration
- `API_ENABLED`: Set to "true" to enable the API (default: "false")
- `API_HOST`: Host to bind the API server to (default: "0.0.0.0")
- `API_PORT`: Port for the API server (default: 8000)
- `API_KEY`: Security key for API access

## 🧩 Daily Chess Puzzles

Safari Buddy can automatically post the Lichess daily puzzle to your Discord server:

### Setup
1. Create a dedicated channel for puzzles (e.g., `#daily-puzzle`)
2. Get the channel ID by right-clicking the channel and selecting "Copy ID" (requires Developer Mode enabled)
3. Add the channel ID to your `.env` file: `PUZZLE_CHANNEL_ID=your_channel_id_here`
4. Set your desired timezone and time if different from the defaults

### Usage
- Puzzles will automatically post at the configured time each day
- Users can use the `/puzzle` command to get today's puzzle on demand
- To see the solution, users can click the 🔍 reaction
- Solutions are posted as replies to maintain spoiler-free experience

### Troubleshooting
- If puzzles aren't posting, check that:
  - Your `PUZZLE_CHANNEL_ID` is correct and the bot has permission to post in that channel
  - The bot has permission to embed links and add reactions
  - The timezone setting is correct for your location

## 📡 API Usage

When enabled, the bot provides a REST API that can be accessed:

### Check Bot Status

```
GET /status
Header: X-API-Key: your_api_key
```

### Trigger Live Notification

```
POST /go-live
Header: X-API-Key: your_api_key
Content-Type: application/json

{
  "title": "Chess Analysis with ChessSafari",
  "game": "Chess",
  "message": "Optional custom message"
}
```

This endpoint allows OBS, Stream Deck, or other tools to trigger stream notifications.

## 🔑 Permissions

To use the bot correctly, it needs the following permissions:

- Read Messages/View Channels
- Send Messages
- Embed Links
- Add Reactions
- Use External Emojis
- Read Message History
- View Server Insights

## 📚 Extending the Bot

The bot uses a modular structure organized into cogs:

- `commands/`: For user commands
- `events/`: For bot event listeners
- `utils/`: For utilities and API

To add new features, create new files in these directories. The bot will automatically load all .py files from these directories.

## 🆘 Support

If you encounter any issues, please open an issue on GitHub or contact ChessSafari on Discord.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created with 🦁 for ChessSafari