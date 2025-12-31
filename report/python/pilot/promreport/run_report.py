#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
from modules.config_loader import load_config, resolve_date
from modules.prom_client import make_prometheus_client
from modules.fetcher import query_range
from modules.plotter import plot_timeseries, plot_summary_bar
from modules.reporter import render_html, font_data_uri
from modules.pdfgen import html_to_pdf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", default="promreport/config/config_test.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    test_mode = cfg.get("report", {}).get("test_mode", False)

    start_dt, end_dt = resolve_date(cfg)
    step = cfg.get("time_range", {}).get("step_seconds", 60)

    prom = None
    if not test_mode:
        prom = make_prometheus_client(cfg)

    metrics_cfg = cfg.get("metrics", [])
    output_dir = cfg.get("report", {}).get("output_dir", "promreport/output")
    font_path = cfg.get("report", {}).get("font_path", "")

    metrics_results = []
    summary_counts = {}

    for m in metrics_cfg:
        title = m.get("title")
        query = m.get("query")
        threshold = m.get("threshold")
        metric_id = m.get("id")
        series = query_range(prom if not test_mode else None, query, start_dt, end_dt, step, test_mode=test_mode, metric_id=metric_id)
        img, anom = plot_timeseries(series, title=title, threshold=threshold, font_path=font_path)
        metrics_results.append({
            "title": title,
            "query": query,
            "threshold": threshold,
            "image": img
        })
        summary_counts[title] = anom

    summary_img = plot_summary_bar(summary_counts, font_path=font_path)

    subject = f"{cfg.get('email', {}).get('subject_prefix','[Monitor Report]')} {start_dt.strftime('%Y-%m-%d')}"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_range = f"{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%Y-%m-%d %H:%M')}"

    font_url = ""
    if font_path and os.path.exists(font_path):
        font_url = font_data_uri(font_path)

    context = {
        "subject": subject,
        "department": cfg.get("report", {}).get("department", ""),
        "generated_at": generated_at,
        "time_range": time_range,
        "summary_chart": summary_img,
        "summary_list": [{"title": k, "count": v} for k, v in summary_counts.items()],
        "metrics": metrics_results,
        "font_url": font_url,
        "font_family": "CustomReportFont" if font_url else "Arial"
    }

    template_path = os.path.join("promreport", "templates", "report_template.html")
    html_out = os.path.join(output_dir, f"monitor_report_{start_dt.strftime('%Y%m%d')}.html")
    render_html(template_path, context, html_out)

    pdf_out = os.path.join(output_dir, f"monitor_report_{start_dt.strftime('%Y%m%d')}.pdf")
    html_to_pdf(html_out, pdf_out)

    # send email if enabled
    from modules.emailer import send_mail
    body_text = f"请查收 {start_dt.strftime('%Y-%m-%d')} 的监控日报（00:00-18:00）。"
    attachments = [html_out, pdf_out]
    send_mail(cfg, subject, body_text, attachments)

    print("报告生成完成：", html_out, pdf_out)

if __name__ == "__main__":
    main()