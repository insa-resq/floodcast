from datetime import datetime, timedelta

import httpx
import matplotlib.pyplot as plt
import numpy as np
import rasterio  # pyright: ignore[reportMissingTypeStubs]
from app.predict.reproject import pixel_area_m2, reproject_to_match
from app.predict.watershed import watershed_dataset
from app.predict.weather import AvailabilityPeriod, rainfall_data


async def volume_for_time_bin(
    *,
    outlet_time: datetime,
    bin_start_hr: int,
    bin_end_hr: int,
    watershed_ds: rasterio.DatasetReader,
    watershed_array: np.ndarray,
    pixel_area: float,
    client: httpx.AsyncClient | None,
) -> float:
    """
    Compute volume contributed by watershed pixels whose travel time
    is in [bin_start_hr, bin_end_hr).
    """

    # Rainfall must have occurred earlier so it arrives at outlet_time
    rainfall_start = outlet_time - timedelta(hours=bin_end_hr)
    rainfall_span = timedelta(hours=(bin_end_hr - bin_start_hr))

    rainfall_period = AvailabilityPeriod(
        start=rainfall_start,
        span=rainfall_span,
    )

    async with rainfall_data(rainfall_period, client) as rain_ds:
        # raw_rain_array = rain_ds.read(1)
        # raw_rain_array[raw_rain_array >= 1000] = np.nan

        # print("total rain: ", np.nansum(raw_rain_array))

        rain_array = reproject_to_match(rain_ds, watershed_ds)
        assert np.max(rain_array) <= 9000

    # Mask watershed pixels belonging to this time bin
    mask = (watershed_array >= bin_start_hr * 3600) & (
        watershed_array < bin_end_hr * 3600
    )

    # fig, axs = plt.subplots(1, 2)
    # axs[0].imshow(mask)
    # axs[1].imshow(rain_array)
    # plt.draw()

    # Rainfall depth in meters
    rainfall_m = rain_array * 0.001  # kg/m² → m

    # Volume per pixel
    volume_m3 = rainfall_m * pixel_area

    # Total volume from this bin
    return float(np.nansum(volume_m3[mask]))


async def estimate_outlet_flow_rate(
    outlet_time: datetime,
    bin_size_hours: int,
    max_travel_time_hours: int,
    client: httpx.AsyncClient | None = None,
) -> float:
    """
    Estimate rainfall flow rate (m³/h) reaching outlet at outlet_time.
    """

    total_volume = 0.0

    with watershed_dataset() as watershed_ds:
        watershed_array = watershed_ds.read(1)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        pixel_area = pixel_area_m2(watershed_ds)

        for bin_start in range(0, max_travel_time_hours, bin_size_hours):
            bin_end = bin_start + bin_size_hours

            volume = await volume_for_time_bin(
                outlet_time=outlet_time,
                bin_start_hr=bin_start,
                bin_end_hr=bin_end,
                watershed_ds=watershed_ds,
                watershed_array=watershed_array,  # pyright: ignore[reportUnknownArgumentType]
                pixel_area=pixel_area,
                client=client,
            )

            total_volume += volume

            # Debug logging
            # print(f"Bin {bin_start}-{bin_end} hr: {volume:,.2f} m³")

    # print(f"FLOW RATE: {total_volume / bin_size_hours:,.2f} m³/h")
    return total_volume / bin_size_hours


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        estimate_outlet_flow_rate(
            outlet_time=datetime.now().replace(
                hour=1, minute=0, second=0, microsecond=0
            )
            + timedelta(days=1),
            bin_size_hours=3,
            max_travel_time_hours=48,
        )
    )
    plt.show()
