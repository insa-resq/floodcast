from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import rasterio  # pyright: ignore[reportMissingTypeStubs]
from rasterio.io import DatasetReader  # pyright: ignore[reportMissingTypeStubs]

# WATERSHED_PATH = (
#     Path(__file__).parents[4]
#     / "models"
#     / "watershed"
#     / "data"
#     / "garonne"
#     / "dist.tiff"
# )
WATERSHED_PATH = Path(__file__).parents[2] / "watershed" / "garonne" / "dist.tiff"


@contextmanager
def watershed_dataset() -> Iterator[DatasetReader]:
    ds = rasterio.open(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        WATERSHED_PATH
    )
    try:
        yield ds
    finally:
        ds.close()  # pyright: ignore[reportUnknownMemberType]
