package config

import (
    "os"

    "gopkg.in/yaml.v3"
)

type MetricConfig struct {
    PromQL    string  `yaml:"promql"`
    Threshold float64 `yaml:"threshold"`
    Unit      string  `yaml:"unit"`
    DrawChart bool    `yaml:"draw_chart"`
}

type Config struct {
    Prometheus struct {
        URL string `yaml:"url"`
    } `yaml:"prometheus"`
    Email struct {
        From       string `yaml:"from"`
        To         string `yaml:"to"`
        Password   string `yaml:"password"`
        SMTPServer string `yaml:"smtp_server"`
    } `yaml:"email"`
    Report struct {
        HTMLPath string `yaml:"html_path"`
        TestMode bool   `yaml:"test_mode"`
    } `yaml:"report"`
    Metrics map[string]MetricConfig `yaml:"metrics"`
}

var Global Config

func Load(path string) error {
    data, err := os.ReadFile(path)
    if err != nil {
        return err
    }
    if err := yaml.Unmarshal(data, &Global); err != nil {
        return err
    }
    if pwd := os.Getenv("EMAIL_PASSWORD"); pwd != "" {
        Global.Email.Password = pwd
    }
    return nil
}

