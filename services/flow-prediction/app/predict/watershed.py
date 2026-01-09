from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import rasterio
from rasterio.io import DatasetReader


@contextmanager
def watershed_dataset() -> Iterator[DatasetReader]:
    ds = rasterio.open(
        Path(__file__).parents[2] / "watershed" / "garonne" / "dist.tiff"
    )
    try:
        yield ds
    finally:
        ds.close()
