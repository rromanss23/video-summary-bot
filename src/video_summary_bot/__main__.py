"""Entry point for running the video summary bot package"""

import sys
import argparse


def main():
    """Main entry point with command line options"""
    parser = argparse.ArgumentParser(description='Video Summary Bot')
    parser.add_argument(
        'command',
        choices=['listen', 'schedule', 'video-summary', 'financial-news'],
        help='Command to run'
    )

    args = parser.parse_args()

    if args.command == 'listen':
        from video_summary_bot.bots.listen import main as listen_main
        listen_main()
    elif args.command == 'schedule':
        from video_summary_bot.scheduler import main as scheduler_main
        scheduler_main()
    elif args.command == 'video-summary':
        from video_summary_bot.bots.video_summary import main as video_summary_main
        video_summary_main()
    elif args.command == 'financial-news':
        from video_summary_bot.bots.financial_news import main as financial_news_main
        financial_news_main()


if __name__ == '__main__':
    main()
