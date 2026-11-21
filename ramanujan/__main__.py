"""CLI entrypoint for `python3 -m ramanujan`."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
