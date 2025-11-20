from pathlib import Path
import argparse
import numpy as np
import rasterio

# Constants
CHANNEL_ACCUMULATION = 100
N_CHANNEL = 0.1
N_HILL = 0.12
R_CHANNEL = 1.0
H_HILL = 0.02


def compute_weights(
    facc: Path,
    slope: Path,
    out: Path,
):
    """
    Compute downslope flow length for each outlet point.
    """
    # Load slope and accumulation arrays
    with rasterio.open(slope) as src:
        slope_data = src.read(1)
        profile = src.profile
    with rasterio.open(facc) as src:
        acc_data = src.read(1)
    slope_data = np.tan(np.deg2rad(slope_data))
    v = np.where(
        acc_data >= CHANNEL_ACCUMULATION,
        np.clip((1 / N_CHANNEL) * (R_CHANNEL ** (2 / 3)) * np.sqrt(slope_data), 0.2, 5.0),
        np.clip((1 / N_HILL) * (H_HILL ** (2 / 3)) * np.sqrt(slope_data), 0.05, 0.2),
    )
    v = np.nan_to_num(v, nan=0.01)
    # v = np.clip(v, 0.01, 5.0)
    
    print(
        "Average velocity (channel, hillslope)",
        v[acc_data >= CHANNEL_ACCUMULATION].mean(),
        v[acc_data < CHANNEL_ACCUMULATION].mean(),
    )

    # Save velocity weights raster
    with rasterio.open(out, "w", **profile) as dst:
        dst.write(1.0 / v, 1)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate watershed downslope flow length using WhiteboxTools."
    )
    parser.add_argument("facc", type=Path, help="Path to the flow accumulation file")
    parser.add_argument("slopes", type=Path, help="Path to the slopes file")
    parser.add_argument("out", type=Path, help="Path to the out file")
    args = parser.parse_args()

    compute_weights(
        Path(args.facc),
        Path(args.slopes),
        Path(args.out),
    )


if __name__ == "__main__":
    main()
