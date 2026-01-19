import asyncio
import time
from pathlib import Path
from typing import Dict

import aiofiles

from app.fetch import fetch_rainfall
from app.models import AvailabilityPeriod

CACHE_DIR = Path(__file__).parents[1] / "cache"
CACHE_TTL_SECONDS = 60 * 60  # 1 hour
MAX_CACHE_FILES = 50

lock = asyncio.Lock()


def _is_expired(path: Path) -> bool:
    return (time.time() - path.stat().st_mtime) > CACHE_TTL_SECONDS


def _evict_if_needed():
    files = list(CACHE_DIR.glob("*.tiff"))
    if len(files) <= MAX_CACHE_FILES:
        return

    # Sort by last modified (oldest first)
    files.sort(key=lambda p: p.stat().st_mtime)

    for path in files[: len(files) - MAX_CACHE_FILES]:
        path.unlink(missing_ok=True)


async def fetch_rainfall_cached(period: AvailabilityPeriod) -> bytes:
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"{repr(period)}.tiff"
    print(path)
    async with lock:
        if path.exists() and not _is_expired(path):
            print("Cache hit")
            async with aiofiles.open(path, "rb") as f:
                return await f.read()

        print("Cache miss")
        # Cache miss or expired
        data = await fetch_rainfall(period)

        tmp_path = path.with_suffix(".tmp")

        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(data)

        # Atomic replace
        tmp_path.replace(path)

        # Evict old entries
        _evict_if_needed()

        return data
