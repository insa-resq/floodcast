import httpx
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO

# TODO
BASE_URL = "https://..."

class UnavailableData(Exception):
    pass

async def fetch_rainfall(time: datetime, span: timedelta) -> BytesIO:
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL)
        return BytesIO(r.content)

def fetch_rainfall_local(time: datetime, span: timedelta) -> Path:
    if span != timedelta(hours=1):
        raise UnavailableData()
    path = Path(__file__).parent.parent / "comephores" / time.strftime("%Y%m%d%H_ERR.gtif")
    if not path.is_file():
        raise UnavailableData()
    return path

