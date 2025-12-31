"""
Generate synthetic time series data for testing.

Returns a dict mapping 'label'->pandas.Series (index=DatetimeIndex)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_series(start_dt, end_dt, step_seconds=60, metric_id="cpu_usage"):
    times = pd.date_range(start=start_dt, end=end_dt, freq=f"{step_seconds}S")
    # create three instances
    instances = ["hostA:9100", "hostB:9100", "hostC:9100"]
    series = {}
    rng = np.random.default_rng(12345)
    for inst in instances:
        if metric_id == "cpu_usage":
            base = 20 + 10 * rng.standard_normal(len(times))
            # create a spike
            if inst == "hostB:9100":
                base[len(times)//3:len(times)//3+5] += 70
        elif metric_id == "mem_usage":
            base = 40 + 5 * rng.standard_normal(len(times))
            if inst == "hostC:9100":
                base[len(times)//2:len(times)//2+10] += 45
        elif metric_id == "disk_used_percent":
            base = 50 + 2 * rng.standard_normal(len(times))
            if inst == "hostA:9100":
                base[-5:] += 45
        elif metric_id == "mysql_threads":
            base = 20 + 10 * np.abs(rng.standard_normal(len(times)))
            if inst == "hostC:9100":
                base[len(times)//4:len(times)//4+8] += 220
        else:
            base = rng.integers(0, 50, size=len(times)).astype(float)
        s = pd.Series(base.clip(min=0), index=times)
        series[inst] = s
    return series