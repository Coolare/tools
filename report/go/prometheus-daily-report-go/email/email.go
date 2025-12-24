package email

import (
    "net/smtp"

    "github.com/jordan-wright/email"
    "prometheus-daily-report-go/config"
)

func Send(reportPath string) error {
    e := email.NewEmail()
    e.From = config.Global.Email.From
    e.To = []string{config.Global.Email.To}
    e.Subject = "每日监控报告 - " + time.Now().Format("2006-01-02")
    e.Text = []byte("请查看附件中的监控日报。")
    _, err := e.AttachFile(reportPath)
    if err != nil {
        return err
    }
    auth := smtp.PlainAuth("", config.Global.Email.From, config.Global.Email.Password, "smtp.gmail.com")
    return e.Send(config.Global.Email.SMTPServer, auth)
}
