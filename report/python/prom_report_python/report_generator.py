import requests
from datetime import datetime, timedelta
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
def mock_series(name):
    times = [datetime.now() - timedelta(minutes=30*i) for i in range(12, -1, -1)]
    if "CPU" in name:
        values1 = [70, 72, 75, 78, 92, 88, 85, 80, 78, 75, 72, 70, 68]  # node1 突刺
        values2 = [68, 70, 72, 75, 78, 80, 78, 75, 72, 70, 68, 65, 64]  # node2
        return [
            {"labels": "node1", "times": times, "values": values1},
            {"labels": "node2", "times": times, "values": values2}
        ]
    if "磁盘" in name:
        values = [84, 85, 86, 86.5, 87, 87.5, 88, 87.8, 87.5, 87, 86.5, 86, 85.5]
        return [{"labels": "node1", "times": times, "values": values}]
    # 内存正常
    values = [75, 76, 77, 76.5, 76, 77, 78, 77.5, 77, 76.5, 76, 75.5, 75]
    return [{"labels": "node1", "times": times, "values": values}]

def query_range(promql, start, end):
    if config['report']['test_mode']:
        for name, cfg in METRICS.items():
            if cfg['promql'] in promql or promql in cfg['promql']:
                return mock_series(name)
        return []
    
    params = {
        'query': promql,
        'start': start.timestamp(),
        'end': end.timestamp(),
        'step': '300'  # 5分钟
    }
    resp = requests.get(f"{config['prometheus']['url']}/api/v1/query_range", params=params)
    resp.raise_for_status()
    results = resp.json()['data']['result']
    series = []
    for r in results:
        labels = str(r['metric'])
        values = r['values']
        times = [datetime.fromtimestamp(t) for t, _ in values]
        vals = [float(v) for _, v in values]
        series.append({"labels": labels, "times": times, "values": vals})
    return series

def plot_to_base64(series_list, title, threshold):
    if not series_list:
        return None
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for s in series_list:
        ax.plot(s['times'], s['values'], marker='o', label=s['labels'])
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(title.split('(')[1])
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    fig.autofmt_xdate()
    if threshold:
        ax.axhline(y=threshold, color='r', linestyle='--', linewidth=2, label=f'阈值 {threshold}')
    ax.legend()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_report():
    start, end = get_time_range()
    alerts = get_active_alerts()
    metrics_data = []

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    for name, cfg in METRICS.items():
        series = query_range(cfg['promql'], start, end)
        if not series:
            continue
        all_values = [v for s in series for v in s['values']]
        avg = sum(all_values) / len(all_values) if all_values else 0
        state = 'alert' if avg > cfg['threshold'] else 'normal'
        chart = None
        if cfg['draw_chart']:
            chart = plot_to_base64(series, f"{name} 趋势图", cfg['threshold'])
        metrics_data.append({
            'name': name,
            'avg': avg,
            'threshold': cfg['threshold'],
            'unit': cfg['unit'],
            'state': state,
            'chart': chart
        })

    html_content = template.render(
        date=start.strftime("%Y年%m月%d日"),
        start="00:00",
        end=end.strftime("%H:%M"),
        metrics=metrics_data,
        alerts=alerts
    )

    html_path = config['report']['html_path']
    pdf_path = config['report']['pdf_path']
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    HTML(html_path).write_pdf(pdf_path)

    print(f"PDF 报告生成成功：{pdf_path}")
    return pdf_path
