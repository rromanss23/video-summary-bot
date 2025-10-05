"""Combined bot - Runs both scheduler and listen bot in separate threads"""

import threading
import logging
from video_summary_bot.bots.listen import main as listen_main
from video_summary_bot.scheduler import main as scheduler_main

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_listen_bot():
    """Run listen bot in a separate thread"""
    try:
        logger.info("🎧 Starting listen bot thread...")
        listen_main()
    except Exception as e:
        logger.error(f"Listen bot error: {e}")


def run_scheduler():
    """Run scheduler in a separate thread"""
    try:
        logger.info("⏰ Starting scheduler thread...")
        scheduler_main()
    except Exception as e:
        logger.error(f"Scheduler error: {e}")


def main():
    """Main function - runs both bots in parallel"""
    print("🚀 Starting Video Summary Bot in COMBINED mode")
    print("=" * 60)
    print("Running both scheduler and listen bot simultaneously...")
    print("=" * 60)

    # Create threads
    listen_thread = threading.Thread(target=run_listen_bot, name="ListenBot", daemon=True)
    scheduler_thread = threading.Thread(target=run_scheduler, name="Scheduler", daemon=True)

    # Start both threads
    listen_thread.start()
    scheduler_thread.start()

    print("\n✅ Both bots are running!")
    print("   - Scheduler: Checking channels every 10 minutes")
    print("   - Listen Bot: Waiting for YouTube URLs from users")
    print("\nPress Ctrl+C to stop both bots...\n")

    try:
        # Keep main thread alive
        listen_thread.join()
        scheduler_thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping both bots...")
        print("Goodbye! 👋")


if __name__ == "__main__":
    main()
