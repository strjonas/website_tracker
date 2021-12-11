import smtplib, ssl
import os

from dotenv import load_dotenv

load_dotenv()

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = os.environ["email"]
password = os.environ["password"]

context = ssl.create_default_context()

def send(message=None, receiver_email=None, subject="Change detected" ):

    if receiver_email == "":
        receiver_email = os.environ["default_email"]

    if message is None or receiver_email is None:
        raise ValueError("message and receiver_email must be set")
    
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, "Subject: {}\n\n{}".format(subject, message))



