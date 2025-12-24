from config_loader import config

def get_active_alerts():
    if config['report']['test_mode']:
        return [
            {'name': 'HighCPUUsage', 'severity': 'critical', 'description': 'CPU 使用率突刺到 92%'},
            {'name': 'DiskFull', 'severity': 'warning', 'description': '磁盘使用率超过阈值'}
        ]
    # 真实模式
    import requests
    query = 'ALERTS{alertstate="firing"}'
    resp = requests.get(f'{config["prometheus"]["url"]}/api/v1/query', params={'query': query})
    results = resp.json()['data']['result']
    return [{'name': r['metric'].get('alertname'), 'severity': r['metric'].get('severity'), 'description': r['metric'].get('description', '')} for r in results]
