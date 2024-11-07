import smtplib
from email.mime.text import MIMEText

def send_email_via_sendgrid():
    msg = MIMEText("This is a test email sent via SendGrid SMTP relay.")
    msg['Subject'] = "Hello from SendGrid"
    msg['From'] = "your_verified_email@your_domain.com"
    msg['To'] = "recipient@example.com"

    # SendGrid SMTP relay configuration
    relay_host = "smtp.sendgrid.net"  # SendGrid’s SMTP server
    relay_port = 587  # Standard SMTP port for TLS
    username = "apikey"  # SendGrid recommends using "apikey" as the username
    password = "your_sendgrid_api_key"  # Replace with your actual SendGrid API Key

    with smtplib.SMTP(relay_host, relay_port) as server:
        server.starttls()  # Initiate a secure connection
        server.login(username, password)  # Log in to the SMTP server
        server.send_message(msg)

send_email_via_sendgrid()
