import requests
from config_loader import config


def get_active_alerts():
    if config["report"]["test_mode"]:
        return [
            {
                "name": "HighCPUUsage",
                "severity": "critical",
                "description": "CPU 使用率突刺到 92%",
            },
            {
                "name": "DiskAlmostFull",
                "severity": "warning",
                "description": "磁盘使用率超过阈值",
            },
        ]

    url = f"{config['prometheus']['url']}/api/v1/query"
    query = 'ALERTS{alertstate="firing"}'
    resp = requests.get(url, params={"query": query})
    resp.raise_for_status()
    results = resp.json()["data"]["result"]
    alerts = []
    for r in results:
        m = r["metric"]
        alerts.append(
            {
                "name": m.get("alertname", "Unknown"),
                "severity": m.get("severity", "unknown"),
                "description": m.get("description", m.get("summary", "")),
            }
        )
    return alerts
