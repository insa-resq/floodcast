import numpy as np
import rasterio  # pyright: ignore[reportMissingTypeStubs]
from rasterio.warp import (  # pyright: ignore[reportMissingTypeStubs ]
    Resampling,
    reproject,  # pyright: ignore[reportUnknownVariableType]
)


def pixel_area_m2(dataset: rasterio.DatasetReader) -> float:
    """
    Assumes projected CRS in meters.
    """
    return abs(dataset.transform.a * dataset.transform.e)


# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
def reproject_to_match(
    src: rasterio.DatasetReader,
    dst: rasterio.DatasetReader,
) -> np.ndarray:
    """
    Reproject src raster to exactly match dst raster grid.
    Returns a numpy array aligned with dst.
    """
    dst_array = np.zeros(
        (dst.height, dst.width),
        dtype=np.float32,
    )

    reproject(
        source=rasterio.band(src, 1),
        destination=dst_array,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=dst.transform,
        dst_crs=dst.crs,
        resampling=Resampling.average,  # rainfall should be averaged
    )

    return dst_array


if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta
    from pathlib import Path

    import httpx

    from app.predict.watershed import watershed_dataset
    from app.predict.weather import AvailabilityPeriod, rainfall_data

    async def test() -> None:
        """
        Fetch watershed + rainfall, reproject rainfall to watershed grid,
        and write result to disk for visual inspection.
        """

        # ---- Pick a small, known rainfall window ----
        rainfall_period = AvailabilityPeriod(
            start=datetime(2026, 1, 13, 6),
            span=timedelta(hours=1),
        )

        async with httpx.AsyncClient(timeout=None) as client:
            # ---- Open watershed ----
            with watershed_dataset() as watershed_ds:
                print("Watershed CRS:", watershed_ds.crs)
                print("Watershed shape:", watershed_ds.height, watershed_ds.width)
                print("Watershed transform:", watershed_ds.transform)

                # ---- Fetch rainfall ----
                async with rainfall_data(rainfall_period, client) as rainfall_ds:
                    print("Rainfall CRS:", rainfall_ds.crs)
                    print("Rainfall shape:", rainfall_ds.height, rainfall_ds.width)
                    print("Rainfall transform:", rainfall_ds.transform)

                    write_rainfall_to_disk(rainfall_ds)

                    # ---- Reproject rainfall ----
                    reprojected = reproject_to_match(
                        src=rainfall_ds,
                        dst=watershed_ds,
                    )

                # ---- Write output raster ----
                profile = watershed_ds.profile.copy()
                profile.update(
                    dtype="float32",
                    count=1,
                    compress="lzw",
                    nodata=None,
                )

                with rasterio.open(
                    "./reprojected_rainfall.tiff", "w", **profile
                ) as dst:
                    dst.write(reprojected, 1)

    def write_rainfall_to_disk(
        rainfall_ds: rasterio.DatasetReader,
    ) -> None:
        """
        Write the rainfall DatasetReader to disk exactly as read.
        """

        profile = rainfall_ds.profile.copy()
        profile.update(
            compress="lzw",
        )

        with rasterio.open("rainfall.tiff", "w", **profile) as dst:
            dst.write(rainfall_ds.read(1), 1)

    asyncio.run(test())
