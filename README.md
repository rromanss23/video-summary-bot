# Video Summary Bot

Automated YouTube video summarizer bot for Telegram that monitors YouTube channels, generates AI-powered summaries of video content, and delivers them to Telegram users.

## Features

- 🎥 Automated YouTube video monitoring via RSS (quota-free)
- 🤖 AI-powered video summarization using Google Gemini
- 📱 Telegram bot integration for message delivery
- 👂 Interactive mode for on-demand URL processing from multiple users
- 📊 Database tracking and caching of processed videos
- 🔄 Smart caching - reuses existing summaries instead of regenerating
- 🔒 User authorization - only configured users can interact with the bot
- ⏰ Scheduled checks with configurable time windows

## Project Structure

```
video-summary-bot/
├── src/
│   └── video_summary_bot/
│       ├── bots/                    # Bot implementations
│       │   ├── combined.py         # Runs both bots in parallel
│       │   ├── listen.py           # Interactive URL processor
│       │   └── video_summary.py    # Scheduled channel monitor
│       ├── handlers/                # External API integrations
│       │   ├── youtube.py          # YouTube API handler
│       │   ├── youtube_rss.py      # RSS feed handler
│       │   ├── gemini.py           # Gemini AI handler
│       │   └── telegram.py         # Telegram bot handler
│       ├── database/                # Database layer
│       │   └── operations.py       # SQLite operations
│       ├── config/                  # Configuration
│       │   ├── settings.py         # API keys & settings
│       │   └── users.py            # User preferences
│       ├── utils/                   # Utilities
│       │   ├── url_parser.py       # URL extraction
│       │   └── logger.py           # Logging setup
│       └── scheduler.py             # Job scheduler
├── data/                            # Data files
│   └── video_summary.db            # SQLite database
├── scripts/                         # Utility scripts
│   └── migrate_database.py         # Database migration
├── notebooks/                       # Jupyter notebooks
│   └── playground.ipynb            # Development playground
└── tests/                          # Test suite
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd video-summary-bot
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   source .venv/bin/activate
   ```

   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

   Required variables:
   - `YOUTUBE_API_KEY` - YouTube Data API v3 key
   - `GEMINI_API_KEY` - Google Gemini API key
   - `TELEGRAM_BOT_TOKEN` - Telegram bot token from @BotFather
   - `TELEGRAM_CHAT_ID` - Your Telegram chat ID

## Usage

The bot can be run in several modes:

### Quick Start (Using Helper Script)

**Recommended: Run both bots together**

```bash
# Run scheduler + listen bot simultaneously (recommended!)
./run.sh combined   
```

Or run individually:

```bash
# Listen for YouTube URLs only
./run.sh listen          

# Run scheduler (automated mode) only
./run.sh schedule        

# Process today's videos once
./run.sh video-summary   
```

### Alternative: Direct Execution

You can also run using `uv run` directly:

```bash
# Recommended: Combined mode (both scheduler and listen bot)
uv run python -m video_summary_bot combined

# Or run individually:
# 1. Listen Mode (Interactive)
uv run python -m video_summary_bot listen

# 2. Scheduler Mode (Automated)
uv run python -m video_summary_bot schedule

# 3. One-time Video Summary
uv run python -m video_summary_bot video-summary
```

### Mode Descriptions

- **combined** ⭐ - Runs both scheduler and listen bot in parallel threads (RECOMMENDED)
  - Best for production use
  - Handles both automated channel monitoring AND user requests
  - Single process, two threads running simultaneously
  - Press Ctrl+C to stop both bots

- **listen** - Interactive mode that listens for YouTube URLs from configured users
  - Accepts messages from all users defined in `config/users.py`
  - Automatically checks if video has been processed before
  - If video exists in database, retrieves cached summary (no API calls)
  - If video is new, generates summary and saves to database
  - Each user receives personalized responses

- **schedule** - Runs scheduled checks for new videos automatically
  - Checks configured channels every 10 minutes
  - Only processes videos published today

- **video-summary** - Process today's videos from configured channels once
  - One-time execution, then exits

## Configuration

### User Management (Database-based) ✨

**Users are now managed in the database, not config files!**

#### First Time Setup

1. Run the migration script to add your initial users:
   ```bash
   uv run python scripts/migrate_users_to_db.py
   ```

2. This reads from [config/users.py](src/video_summary_bot/config/users.py) and populates the database

#### Adding New Users

```bash
# Open database
sqlite3 data/video_summary.db

# Add a user (use their Telegram chat ID)
INSERT INTO users (user_id, username, active) VALUES ('123456789', 'John Doe', 1);

# Subscribe user to channels
INSERT INTO user_channels (user_id, channel_id) VALUES ('123456789', 1);
```

Or use Python:
```python
from video_summary_bot.database import Database
db = Database()
db.add_user(user_id="123456789", username="John Doe")
db.subscribe_user_to_channel("123456789", channel_id=1)
```

📖 **Full guide:** See [docs/USER_MANAGEMENT.md](docs/USER_MANAGEMENT.md) for detailed instructions

### Channel Configuration

Channels are also managed in the database. Initial setup:

```bash
sqlite3 data/video_summary.db

# Add a channel
INSERT INTO channels (channel_handle, channel_name, youtube_channel_id, language)
VALUES ('@channelhandle', 'Channel Name', 'UCxxxxx', 'es');
```

## Database

The bot uses SQLite to track:
- User subscriptions
- Channel configurations
- Processed video summaries
- Check schedules

Database location: [data/video_summary.db](data/video_summary.db)

## Development

### Running Tests
```bash
pytest tests/
```

### Using the Playground Notebook
```bash
jupyter notebook notebooks/playground.ipynb
```

### Project Commands

Install in development mode:
```bash
pip install -e .
```

## API Quota Management

The bot uses RSS feeds for video discovery (quota-free) and only uses the YouTube API for:
- Initial channel ID lookup (one-time)
- Video metadata retrieval

This approach minimizes API quota usage significantly.

## License

MIT

## Contributing

Pull requests are welcome! Please ensure:
- Code follows the existing structure
- All tests pass
- Documentation is updated
