import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

SENDER_EMAIL   = os.environ.get("SENDER_EMAIL", "")
APP_PASSWORD   = os.environ.get("APP_PASSWORD", "")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "")

if not (SENDER_EMAIL and APP_PASSWORD and RECEIVER_EMAIL):
    print("SENDER_EMAIL / APP_PASSWORD / RECEIVER_EMAIL not set - skipping email")
    raise SystemExit(0)

msg = MIMEMultipart()
msg['From']    = SENDER_EMAIL
msg['To']      = RECEIVER_EMAIL
msg['Subject'] = f"Retail Sales & Inventory Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"

body = """Hello,

Please find attached the Retail Sales & Inventory Analysis Report
generated using Apache Hadoop MapReduce on a 3-Node Distributed Cluster (Docker).

Cluster Setup:
  - 1 NameNode (Master)
  - 3 DataNodes (Workers)
  - Data distributed across HDFS
  - Parallel MapReduce execution with 3 reducers

Report includes:
  Job 1: Total Revenue per Product Category
  Job 2: Inventory Gap Analysis (Understock / Overstock / Balanced)

Regards,
Hadoop Retail Analytics Pipeline
"""
msg.attach(MIMEText(body, 'plain'))

try:
    with open("/opt/results/sales_report.pdf", "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=sales_report.pdf')
    msg.attach(part)
except Exception as e:
    print("Error attaching file:", e)
    raise SystemExit(1)

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    print("Sales report email sent successfully!")
except Exception as e:
    print("Email sending failed:", e)
