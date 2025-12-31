import pandas as pd
import numpy as np
from datetime import timezone
from prometheus_api_client import PrometheusConnect
from typing import Dict
from . import fake_prom

def query_range(prom_or_cfg, query, start_dt, end_dt, step_seconds=60, test_mode=False, metric_id=None):
    """
    If test_mode True, returns synthetic data (dict label->pd.Series).
    Otherwise prom_or_cfg is PrometheusConnect instance and real query is executed.
    """
    if test_mode:
        return fake_prom.generate_series(start_dt, end_dt, step_seconds, metric_id or "custom")
    prom = prom_or_cfg
    # prometheus_api_client get_metric_range_data returns list of metrics
    resp = prom.get_metric_range_data(query=query, start_time=start_dt, end_time=end_dt, chunk_size=step_seconds)
    series_dict = {}
    for item in resp:
        metric = item.get("metric", {})
        # choose label
        if "instance" in metric:
            key = metric["instance"]
        elif "job" in metric:
            key = metric["job"]
        else:
            if metric:
                key = ",".join([f"{k}={v}" for k, v in metric.items()])
            else:
                key = "value"
        vals = item.get("values", [])
        times = [pd.to_datetime(float(t), unit='s') for t, v in vals]
        values = [float(v) if v not in (None, "NaN", "") else np.nan for t, v in vals]
        series_dict[key] = pd.Series(data=values, index=times)
    # normalize into pandas Series dict (may be empty)
    return series_dict