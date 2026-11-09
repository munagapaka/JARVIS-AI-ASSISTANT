# main.py

import asyncio
from live_test import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("🛑 J.A.R.V.I.S. shutting down.")
        print("=" * 60)
