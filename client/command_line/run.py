import asyncio
from client.command_line.base import JobStreamerCLI


def main():
    def handle_command(text: str):
        # Placeholder — wire up real command routing here later
        cli.notify(f"[command received]: {text}")

    cli = JobStreamerCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()