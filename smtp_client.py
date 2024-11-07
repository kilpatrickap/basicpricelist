import smtplib
from email.mime.text import MIMEText

def send_email_to_local_server():
    msg = MIMEText("This is a test message.")
    msg['Subject'] = "Test Email"
    msg['From'] = "sender@example.com"
    msg['To'] = "recipient@example.com"

    with smtplib.SMTP('localhost', 1025) as server:
        server.send_message(msg)

send_email_to_local_server()
