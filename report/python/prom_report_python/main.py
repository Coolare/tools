from report_generator import generate_report
from email_sender import send_email

if __name__ == "__main__":
    pdf_path = generate_report()
    # send_email(pdf_path)
