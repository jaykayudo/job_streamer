import asyncio
from client.command_line.base import JobStreamerCLI


def main():
    cli = JobStreamerCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()