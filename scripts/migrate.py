#!/usr/bin/env python
"""
Database migration helper for job-streamer.

Usage
-----
    poetry run python scripts/migrate.py upgrade          # apply all pending migrations
    poetry run python scripts/migrate.py downgrade        # roll back one migration
    poetry run python scripts/migrate.py downgrade <rev>  # roll back to a specific revision
    poetry run python scripts/migrate.py revision "msg"   # auto-generate a new migration
    poetry run python scripts/migrate.py history          # show migration history
    poetry run python scripts/migrate.py current          # show current revision
    poetry run python scripts/migrate.py heads            # show latest revisions

All commands delegate to Alembic using the project's alembic.ini.
"""
from __future__ import annotations

import sys
import os

# Ensure the project root is on sys.path.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from alembic.config import Config
from alembic import command as alembic_cmd


ALEMBIC_INI = os.path.join(PROJECT_ROOT, "alembic.ini")


def get_alembic_config() -> Config:
    cfg = Config(ALEMBIC_INI)
    return cfg


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0].lower()
    cfg = get_alembic_config()

    if cmd == "upgrade":
        revision = args[1] if len(args) > 1 else "head"
        print(f"Upgrading to: {revision}")
        alembic_cmd.upgrade(cfg, revision)

    elif cmd == "downgrade":
        revision = args[1] if len(args) > 1 else "-1"
        print(f"Downgrading to: {revision}")
        alembic_cmd.downgrade(cfg, revision)

    elif cmd == "revision":
        message = args[1] if len(args) > 1 else "migration"
        print(f"Generating new migration: '{message}'")
        alembic_cmd.revision(cfg, message=message, autogenerate=True)

    elif cmd == "history":
        alembic_cmd.history(cfg, verbose=True)

    elif cmd == "current":
        alembic_cmd.current(cfg, verbose=True)

    elif cmd == "heads":
        alembic_cmd.heads(cfg, verbose=True)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
