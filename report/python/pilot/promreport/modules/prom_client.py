from prometheus_api_client import PrometheusConnect

def make_prometheus_client(cfg):
    url = cfg.get("prometheus", {}).get("url")
    timeout = cfg.get("prometheus", {}).get("timeout", 10)
    # disable_ssl False if using https with valid certs; adjust as needed
    return PrometheusConnect(url=url, disable_ssl=True, headers=None, timeout=timeout)