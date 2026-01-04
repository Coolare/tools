import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64
import numpy as np
from matplotlib.dates import DateFormatter
from datetime import datetime
import pandas as pd
from matplotlib import font_manager

def _register_font_if_needed(font_path):
    """
    If font_path exists, add it to matplotlib font manager and set global rcParams.
    Returns a FontProperties instance or None.
    """
    if not font_path:
        return None
    try:
        # matplotlib >=3.2: addfont registers the font file
        font_manager.fontManager.addfont(font_path)
    except Exception:
        # fallback: try to load via FontProperties (still will work for individual texts)
        pass
    try:
        prop = font_manager.FontProperties(fname=font_path)
        font_name = prop.get_name()
        # set global rcParams to use this font for sans-serif
        plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams.get('font.sans-serif', [])
        plt.rcParams['font.family'] = 'sans-serif'
        # ensure minus sign rendered correctly
        plt.rcParams['axes.unicode_minus'] = False
        return prop
    except Exception:
        return None

def plot_timeseries(df_dict, title, threshold=None, legend_title=None, font_path=None):
    """
    df_dict: dict label -> pandas.Series (index datetime)
    returns base64 PNG data URI and anomaly_count
    """
    font_prop = _register_font_if_needed(font_path)

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=120)
    # title with fontprop if available
    if font_prop:
        ax.set_title(title, fontproperties=font_prop, fontsize=14)
    else:
        ax.set_title(title, fontsize=14)

    # plot each series
    anomaly_count = 0
    for label, series in df_dict.items():
        if series is None or len(series) == 0:
            continue
        x = series.index
        y = series.values
        ax.plot(x, y, label=str(label), linewidth=1.5)

        if threshold is not None:
            exceed = series > threshold
            if exceed.any():
                anomaly_count += int(exceed.sum())
                ax.scatter(series.index[exceed], series[exceed], color='red', s=20, zorder=5)
                # annotate up to top 3 points
                try:
                    top_idx = series[exceed].nlargest(3).index
                    for idx in top_idx:
                        if font_prop:
                            ax.annotate(f"{series.loc[idx]:.1f}", xy=(idx, series.loc[idx]),
                                        xytext=(0,6), textcoords="offset points",
                                        fontsize=8, color='red', fontproperties=font_prop)
                        else:
                            ax.annotate(f"{series.loc[idx]:.1f}", xy=(idx, series.loc[idx]),
                                        xytext=(0,6), textcoords="offset points",
                                        fontsize=8, color='red')

                except Exception:
                    pass

    # threshold line
    if threshold is not None:
        ax.axhline(threshold, color='orange', linestyle='--', linewidth=1.5, label=f"阈值 {threshold}")

    ax.grid(alpha=0.2)
    if font_prop:
        # legend with fontprop
        leg = ax.legend(loc='upper right', fontsize=8, prop=font_prop)
    else:
        leg = ax.legend(loc='upper right', fontsize=8)
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}", anomaly_count

def plot_summary_bar(summary_dict, title="异常统计", font_path=None):
    font_prop = _register_font_if_needed(font_path)

    names = list(summary_dict.keys())
    vals = [summary_dict[k] for k in names]
    y_pos = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8, max(3, 0.4*len(names))), dpi=120)
    bars = ax.barh(y_pos, vals, color='salmon')
    ax.set_yticks(y_pos)
    if font_prop:
        ax.set_yticklabels(names, fontproperties=font_prop, fontsize=10)
        ax.set_title(title, fontproperties=font_prop)
    else:
        ax.set_yticklabels(names, fontsize=10)
        ax.set_title(title)
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
