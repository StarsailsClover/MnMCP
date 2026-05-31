"""
Room-only launcher: auth + create room + heartbeat.
Does NOT start aiorak server - use with mn2mc_proxy.exe
"""
import asyncio
import sys
from loguru import logger

import mn2mc.config as config
import mn2mc.mini.auth
import mn2mc.mini.room
import mn2mc.mini.wsconn


async def main():
    logger.add("logs/{time}.log")
    config.load()

    logger.info("=== Room-Only Mode (for mn2mc_proxy) ===")

    await mn2mc.mini.wsconn.fetch_s2()
    await mn2mc.mini.room.create_room()

    logger.info(f"Room ready. Host UID: {mn2mc.mini.auth.uin}")
    logger.info("Start mn2mc_proxy.exe --port 19132 --guid %d" % mn2mc.mini.auth.uin)
    logger.info("Press Ctrl+C to close room and exit.")

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        logger.info("Closing room...")
        await mn2mc.mini.room.close_room()
        logger.info("Done.")


if __name__ == "__main__":
    asyncio.run(main())
