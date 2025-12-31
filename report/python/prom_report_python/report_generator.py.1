import requests
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
from config_loader import config
from metrics import METRICS
from alerts import get_active_alerts

def get_time_range():
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=18, minute=0, second=0, microsecond=0) if now.hour >= 18 else now
    return start, end

# 测试模式模拟数据
test_series = {
    "CPU 使用率 (%)": [
        {'labels': 'node1', 'times': [datetime.now() - timedelta(hours=i) for i in range(6,0,-1)], 'values': [75, 80, 92, 85, 78, 70]},  # 突刺92%
        {'labels': 'node2', 'times': [datetime.now() - timedelta(hours=i) for i in range(6,0,-1)], 'values': [70, 75, 80, 78, 72, 68]}
    ],
    "内存使用率 (%)": [
        {'labels': 'node1', 'times': [...same times...], 'values': [76, 77, 78, 76, 75, 76]},
        {'labels': 'node2', 'times': [...], 'values': [75, 76, 77, 75, 74, 76]}
    ],
    "磁盘使用率 (%)": [
        {'labels': 'node1', 'times': [...], 'values': [87, 88, 89, 87, 88, 87]},  # 超阈值
        {'labels': 'node2', 'times': [...], 'values': [84, 85, 86, 84, 85, 84]}
    ]
}

def query_range(promql, start, end):
    if config['report']['test_mode']:
        # 返回模拟数据（简化，实际可从 JSON 加载）
        name = [k for k, v in METRICS.items() if v['promql'] == promql][0]
        return test_series.get(name, [])
    # 真实查询
    params = {'query': promql, 'start': start.timestamp(), 'end': end.timestamp(), 'step': '300'}
    resp = requests.get(f'{config["prometheus"]["url"]}/api/v1/query_range', params=params)
    # 解析返回 series （类似之前代码）
    # ... (省略解析逻辑，可参考之前版本)
    return []  # 占位

# 其他函数（plot_to_base64 等）同之前

def generate_report():
    alerts = get_active_alerts()
    # ... 生成 metrics_data、chart、render 模板、写文件、转 PDF
    # 同之前完整逻辑
    return config['report']['pdf_path']
