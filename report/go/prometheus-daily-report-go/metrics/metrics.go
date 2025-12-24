package metrics

import "prometheus-daily-report-go/config"

func GetAll() map[string]config.MetricConfig {
    return config.Global.Metrics
}
