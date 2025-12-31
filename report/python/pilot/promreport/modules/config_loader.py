import os
import yaml
from datetime import datetime, timezone, timedelta

def load_config(path="promreport/config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # Ensure defaults
    cfg.setdefault("report", {})
    cfg["report"].setdefault("output_dir", "promreport/output")
    cfg.setdefault("time_range", {})
    cfg["time_range"].setdefault("step_seconds", 60)
    # Create output dir
    os.makedirs(cfg["report"]["output_dir"], exist_ok=True)
    return cfg

def resolve_date(cfg):
    tz = cfg.get("report", {}).get("timezone", "local")
    specified_date = cfg.get("report", {}).get("date", "")
    if specified_date:
        base_date = datetime.strptime(specified_date, "%Y-%m-%d")
    else:
        if tz == "local":
            base_date = datetime.now()
        else:
            try:
                import pytz
                base_date = datetime.now(tz=pytz.timezone(tz))
            except Exception:
                base_date = datetime.now()
    start_hour = cfg.get("time_range", {}).get("start_hour", 0)
    end_hour = cfg.get("time_range", {}).get("end_hour", 18)
    start_dt = datetime(base_date.year, base_date.month, base_date.day, start_hour, 0, 0)
    end_dt = datetime(base_date.year, base_date.month, base_date.day, end_hour, 0, 0)
    # Prometheus expects UTC datetimes for its API; return naive UTC datetimes
    # Convert local to UTC if tz not 'local'
    return start_dt, end_dt