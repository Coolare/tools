package alerts

import (
	"context"
	"time"

	"github.com/prometheus/client_golang/api"
	v1 "github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/common/model"
	"prometheus-daily-report-go/config"
)

type Alert struct {
	Name        string
	Severity    string
	Description string
}

func GetActiveAlerts() ([]Alert, error) {
	if config.Global.Report.TestMode {
		return []Alert{
			{Name: "HighCPUUsage", Severity: "critical", Description: "CPU 突刺超过 90%"},
			{Name: "DiskAlmostFull", Severity: "warning", Description: "磁盘使用率超过阈值"},
		}, nil
	}

	client, err := api.NewClient(api.Config{Address: config.Global.Prometheus.URL})
	if err != nil {
		return nil, err
	}
	v1api := v1.NewAPI(client)

	result, _, err := v1api.Query(context.Background(), `ALERTS{alertstate="firing"}`, time.Now())
	if err != nil {
		return nil, err
	}
	vector := result.(model.Vector)
	alerts := []Alert{}
	for _, sample := range vector {
		alerts = append(alerts, Alert{
			Name:        string(sample.Metric["alertname"]),
			Severity:    string(sample.Metric["severity"]),
			Description: string(sample.Metric["description"]),
		})
	}
	return alerts, nil
}
