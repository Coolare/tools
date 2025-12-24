package main

import (
    "log"
    "os"

    "prometheus-daily-report-go/config"
    "prometheus-daily-report-go/email"
    "prometheus-daily-report-go/report"
)

func main() {
    if err := config.Load("config.yaml"); err != nil {
        log.Fatal("加载配置失败:", err)
    }

    reportPath, err := report.Generate()
    if err != nil {
        log.Fatal("生成报告失败:", err)
    }

    if config.Global.Email.Password != "" {
        if err := email.Send(reportPath); err != nil {
            log.Println("发送邮件失败:", err)
        } else {
            log.Println("报告已发送邮件")
        }
    }

    os.Exit(0)
}
