import smtplib, ssl

port = 587
smtp_server = "smtp.gmail.com"
sender_email = "notifygrupo02@gmail.com"
receiver_email = ""
password = ""
message = """\
Subject: Hi there

This is an investment recommendation."""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    # server.ehlo()
    server.starttls(context=context)
    # server.ehlo()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
