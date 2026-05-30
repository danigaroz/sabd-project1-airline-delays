"""Small helpers shared between query scripts."""
import time
from contextlib import contextmanager
from typing import Optional


# Columns actually consumed by Q1 and Q2.
RELEVANT_COLS = [
    "YEAR", "MONTH", "DAY_OF_MONTH",
    "OP_UNIQUE_CARRIER",
    "CRS_DEP_TIME",
    "DEP_DELAY", "ARR_DELAY",
    "CANCELLED", "DIVERTED",
    "CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY",
    "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY",
]


@contextmanager
def timer(label: str, registry: Optional[dict] = None):
    """Time a block of code. Optionally accumulate the result in `registry`."""
    t0 = time.perf_counter()
    yield
    elapsed = time.perf_counter() - t0
    print(f"[TIMER] {label}: {elapsed:.3f}s")
    if registry is not None:
        registry[label] = elapsed
