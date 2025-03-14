import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail(subject, recipient, html_content, cc_recipients=None):
    sender = "no-reply@usdtheist.com"
    password = "isjymlxgicvhzlim"

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    if cc_recipients:
        msg['Cc'] = ", ".join(cc_recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    # Connect to SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        return server.sendmail(sender, recipient, msg.as_string())
