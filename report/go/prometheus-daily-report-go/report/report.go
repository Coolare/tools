package report

import (
	"bytes"
	"context"
	"fmt"
	"html/template"
	"io/ioutil"
	"time"

	"github.com/go-echarts/go-echarts/v2/charts"
	"github.com/go-echarts/go-echarts/v2/components"
	"github.com/go-echarts/go-echarts/v2/opts"
	"github.com/prometheus/client_golang/api"
	v1 "github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/common/model"
	"prometheus-daily-report-go/alerts"
	"prometheus-daily-report-go/config"
	"prometheus-daily-report-go/metrics"
)


type Series struct {
	Instance string
	Times    []string
	Values   []opts.LineData
}

type MetricData struct {
	Avg       float64
	Threshold float64
	Unit      string
	State     string
}

func getTimeRange() (time.Time, time.Time) {
	now := time.Now()
	start := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())
	end := time.Date(now.Year(), now.Month(), now.Day(), 18, 0, 0, 0, now.Location())
	if now.Hour() < 18 {
		end = now
	}
	return start, end
}

// 测试模式模拟数据
func mockSeries(name string) []Series {
	times := []string{"00:00", "04:00", "08:00", "12:00", "14:00", "16:00", "18:00"}
	base := []float32{70, 72, 75, 78, 85, 80, 75}
	spike := []float32{70, 72, 75, 78, 92, 88, 75} // 14:00 突刺

	if name == "CPU 使用率 (%)" {
		return []Series{
			{Instance: "node1", Times: times, Values: toLineData(spike)},
			{Instance: "node2", Times: times, Values: toLineData(base)},
		}
	}
	if name == "磁盘使用率 (%)" {
		high := []float32{84, 85, 86, 87, 88, 87.5, 87}
		return []Series{
			{Instance: "node1", Times: times, Values: toLineData(high)},
			{Instance: "node2", Times: times, Values: toLineData(base)},
		}
	}
	return []Series{
		{Instance: "node1", Times: times, Values: toLineData(base)},
		{Instance: "node2", Times: times, Values: toLineData(base)},
	}
}

func toLineData(vals []float32) []opts.LineData {
	data := make([]opts.LineData, len(vals))
	for i, v := range vals {
		data[i] = opts.LineData{Value: v}
	}
	return data
}

func queryRange(promql string, start, end time.Time) ([]Series, error) {
	if config.Global.Report.TestMode {
		// 找对应指标名
		for name, cfg := range metrics.GetAll() {
			if cfg.PromQL == promql {
				return mockSeries(name), nil
			}
		}
		return []Series{}, nil
	}

	client, _ := api.NewClient(api.Config{Address: config.Global.Prometheus.URL})
	v1api := v1.NewAPI(client)
	r := v1.Range{Start: start, End: end, Step: time.Minute * 30}
	result, _, err := v1api.QueryRange(context.Background(), promql, r)
	if err != nil {
		return nil, err
	}
	matrix := result.(model.Matrix)
	seriesList := []Series{}
	for _, stream := range matrix {
		instance := string(stream.Metric["instance"])
		times := []string{}
		values := []opts.LineData{}
		for _, v := range stream.Values {
			times = append(times, v.Timestamp.Time().Format("15:04"))
			values = append(values, opts.LineData{Value: float32(v.Value)})
		}
		seriesList = append(seriesList, Series{Instance: instance, Times: times, Values: values})
	}
	return seriesList, nil
}

func createChart(title string, seriesList []Series, threshold float64) *charts.Line {
	line := charts.NewLine()
	line.SetGlobalOptions(
		charts.WithTitleOpts(opts.Title{Title: title}),
		charts.WithTooltipOpts(opts.Tooltip{Show: true, Trigger: "axis"}),
		charts.WithLegendOpts(opts.Legend{Show: true}),
		charts.WithDataZoomOpts(opts.DataZoom{Type: "slider"}),
	)
	if len(seriesList) > 0 {
		line.SetXAxis(seriesList[0].Times)
	}
	for _, s := range seriesList {
		line.AddSeries(s.Instance, s.Values)
	}
	if threshold > 0 {
		threshData := make([]opts.LineData, len(seriesList[0].Times))
		for i := range threshData {
			threshData[i] = opts.LineData{Value: threshold}
		}
		line.AddSeries("阈值线", threshData,
			charts.WithLineStyleOpts(opts.LineStyle{Color: "red", Type: "dashed", Width: 2}),
		)
	}
	return line
}

func Generate() (string, error) {
	start, end := getTimeRange()
	metricsData := make(map[string]MetricData)
	var page *components.Page

	if config.Global.Report.TestMode {
		page = components.NewPage()
	}

	for name, cfg := range metrics.GetAll() {
		if !cfg.DrawChart {
			continue
		}
		seriesList, err := queryRange(cfg.PromQL, start, end)
		if err != nil || len(seriesList) == 0 {
			continue
		}

		// 计算平均
		var total float64
		count := 0
		for _, s := range seriesList {
			for _, v := range s.Values {
				total += float64(v.Value.(float32))
				count++
			}
		}
		avg := total / float64(count)
		state := "normal"
		if avg > cfg.Threshold {
			state = "alert"
		}
		metricsData[name] = MetricData{Avg: avg, Threshold: cfg.Threshold, Unit: cfg.Unit, State: state}

		chart := createChart(name+" 趋势图", seriesList, cfg.Threshold)
		if config.Global.Report.TestMode {
			page.AddCharts(chart)
		}
	}

	var chartsBuf bytes.Buffer
	if config.Global.Report.TestMode {
		page.Render(&chartsBuf)
	}

	alertList, _ := alerts.GetActiveAlerts()

	tmpl := template.Must(template.New("report").Funcs(template.FuncMap{
		"safeHTML": func(s string) template.HTML { return template.HTML(s) },
	}).ParseFiles("templates/report_template.html"))

	data := struct {
		Date        string
		Start       string
		End         string
		MetricsData map[string]MetricData
		ChartsHTML  template.HTML
		Alerts      []alerts.Alert
	}{
		Date:        start.Format("2006年01月02日"),
		Start:       "00:00",
		End:         end.Format("15:04"),
		MetricsData: metricsData,
		ChartsHTML:  template.HTML(chartsBuf.String()),
		Alerts:      alertList,
	}

	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, data); err != nil {
		return "", err
	}

	path := config.Global.Report.HTMLPath
	ioutil.WriteFile(path, buf.Bytes(), 0644)
	fmt.Printf("报告生成成功：%s\n", path)
	return path, nil
}
