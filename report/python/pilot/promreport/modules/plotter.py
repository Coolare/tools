import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64
import numpy as np
from matplotlib.dates import DateFormatter
import pandas as pd

def plot_timeseries(series_dict, title, threshold=None, font_path=None):
    """
    series_dict: mapping label->pd.Series (index datetime)
    returns data:image/png;base64,... and anomaly_count (int)
    """
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=120)
    # set font
    if font_path:
        try:
            from matplotlib import font_manager
            font_prop = font_manager.FontProperties(fname=font_path)
            plt.title(title, fontproperties=font_prop, fontsize=14)
            ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        except Exception:
            plt.title(title, fontsize=14)
    else:
        plt.title(title, fontsize=14)
    anomaly_count = 0
    for label, series in series_dict.items():
        if series.empty:
            continue
        ax.plot(series.index, series.values, label=str(label), linewidth=1.2)
        if threshold is not None:
            exceed = series > threshold
            if exceed.any():
                anomaly_count += int(exceed.sum())
                ax.scatter(series.index[exceed], series[exceed], color='red', s=18, zorder=5)
                # annotate top points
                top_idx = series[exceed].nlargest(3).index
                for idx in top_idx:
                    ax.annotate(f"{series.loc[idx]:.1f}", xy=(idx, series.loc[idx]), xytext=(0,6), textcoords="offset points", fontsize=8, color='red')
    if threshold is not None:
        ax.axhline(threshold, color='orange', linestyle='--', linewidth='1.5', label=f"阈值 {threshold}")
    ax.grid(alpha=0.2)
    ax.legend(loc='upper right', fontsize=8)
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}", anomaly_count

def plot_summary_bar(summary_dict, font_path=None):
    """
    summary_dict: {metric_title: anomaly_count}
    returns data:image/png;base64,...
    """
    import matplotlib.pyplot as plt
    names = list(summary_dict.keys())
    vals = [summary_dict[k] for k in names]
    y_pos = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8, max(3, 0.4*len(names))), dpi=120)
    bars = ax.barh(y_pos, vals, color='salmon')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel("异常次数")
    for i, v in enumerate(vals):
        ax.text(v + 0.1, i, str(v), va='center')
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"
