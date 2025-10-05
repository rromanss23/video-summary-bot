#!/bin/bash
# Helper script to run the video summary bot with the correct environment

set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if command is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh <command>"
    echo ""
    echo "Available commands:"
    echo "  listen          - Listen for YouTube URLs from Telegram"
    echo "  schedule        - Run the scheduler (automated mode)"
    echo "  video-summary   - Process today's videos once"
    echo "  financial-news  - Send financial news once"
    exit 1
fi

# Run the bot with uv
echo "🚀 Running video-summary-bot in '$1' mode..."
uv run python -m video_summary_bot "$1"
