from __future__ import annotations

import argparse
import logging

from .config import load_config
from .messages import load_messages
from .bot import run_bot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Auto Message Discord bot")
    parser.add_argument("--config", default="config.example.yml", help="Path to YAML config")
    parser.add_argument("--dry-run", action="store_true", help="Print messages without connecting to Discord")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")
    config = load_config(args.config)

    if args.dry_run or config.dry_run:
        messages = load_messages(config.messages_file)
        for index, message in enumerate(messages, start=1):
            print(f"[{index}] {message}")
        return

    run_bot(config)


if __name__ == "__main__":
    main()
