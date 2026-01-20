from datetime import datetime, time

from app.predict.compute_flow_rate import estimate_outlet_flow_rate
from app.predict.get_flow_rate import (
    FlowInfo,
    LatestFlowQueryParams,
    get_flow_rate_data,
)

FLOW_RATE_DIV = 12
BIN_SIZE = 3
MAX_TRAVEL_TIME = 24


async def get_baseline_flow() -> float:
    flow_info = await get_flow_rate_data(
        LatestFlowQueryParams(latitude=43.520681, longitude=1.411743, max_distance=5)
    )
    baseline_date = flow_info.obs_date.replace(
        minute=0, second=0, microsecond=0, tzinfo=None
    )
    print(f"{baseline_date=}")
    baseline_rainfall_flow = await estimate_outlet_flow_rate(
        outlet_time=baseline_date,
        bin_size_hours=BIN_SIZE,
        max_travel_time_hours=MAX_TRAVEL_TIME,
    )
    return (flow_info.value / 1000 * 3600) - (baseline_rainfall_flow / FLOW_RATE_DIV)


async def predict_flow_rate(date: datetime) -> float:
    baseline_flow = await get_baseline_flow()
    predicted_rainfall_flow_rate = await estimate_outlet_flow_rate(
        outlet_time=date, bin_size_hours=BIN_SIZE, max_travel_time_hours=MAX_TRAVEL_TIME
    )
    print(baseline_flow / 3600)
    return baseline_flow + (predicted_rainfall_flow_rate / FLOW_RATE_DIV)


if __name__ == "__main__":
    import asyncio

    print(
        asyncio.run(
            predict_flow_rate(
                datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
            )
        )
        / 3600
    )
