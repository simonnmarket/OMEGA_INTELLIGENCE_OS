
# Configuration for MPI prototype
MPI_CONFIG = {
    "weights": {
        "delta": 0.35,
        "liquidity": 0.25,
        "volume_profile": 0.20,
        "velocity": 0.15,
        "regime": 0.05
    },
    "mpi_thresholds": {
        "green": 30,
        "yellow": 60,
        "orange": 80,
        "red": 100
    },
    "rolling_window_seconds": 60,
    "profile_window_bars": 60  # bars for volume profile
}
