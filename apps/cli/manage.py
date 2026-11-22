import sys

from loguru import logger


def main() -> None:
    """Management CLI script for administrative operations."""
    if len(sys.argv) < 2:
        print("Usage: python -m apps.cli.manage <command>")
        print("Available commands: ping, info")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "ping":
        logger.info("Pong!")
    elif cmd == "info":
        logger.info("Modular Monolith Boilerplate Manager CLI")
    else:
        logger.error(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
