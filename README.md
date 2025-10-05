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

The easiest way to run the bot:

```bash
./run.sh listen          # Listen for YouTube URLs
./run.sh schedule        # Run scheduler (automated mode)
./run.sh video-summary   # Process today's videos once
```

### Alternative: Direct Execution

You can also run using `uv run` directly:

```bash
# 1. Listen Mode (Interactive)
uv run python -m video_summary_bot listen

# 2. Scheduler Mode (Automated)
uv run python -m video_summary_bot schedule

# 3. One-time Video Summary
uv run python -m video_summary_bot video-summary
```

### Mode Descriptions

- **listen** - Interactive mode that listens for YouTube URLs from configured users
  - Accepts messages from all users defined in `config/users.py`
  - Automatically checks if video has been processed before
  - If video exists in database, retrieves cached summary (no API calls)
  - If video is new, generates summary and saves to database
  - Each user receives personalized responses
- **schedule** - Runs scheduled checks for new videos automatically
- **video-summary** - Process today's videos from configured channels once

## Configuration

### Channel Configuration

Edit [src/video_summary_bot/config/settings.py](src/video_summary_bot/config/settings.py) to configure monitored channels:

```python
youtube_channels = [
    "@channelhandle1",
    "@channelhandle2",
]
```

### User Preferences

Edit [src/video_summary_bot/config/users.py](src/video_summary_bot/config/users.py) to configure user subscriptions:

```python
user_preferences = {
    'CHAT_ID': {
        'channels': ['@channel1', '@channel2'],
        'user_name': 'User Name'
    }
}
```

**Note**: In production, user preferences should be moved to the database.

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
