import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from dotenv import load_dotenv

import ssl
load_dotenv("../.env")
SUBJECT=os.getenv("SUBJECT")

class EmailSender:
    def __init__(self,USERID,USERPASS,SUBJECT):
        self.userid= USERID
        self.userpass=USERPASS
        self.subject=SUBJECT

    def __init__(self,USERID,USERPASS):
        self.userid= USERID
        self.userpass=USERPASS
        self.subject=SUBJECT


    def send_email(self, to_email, message):
        try: 
            em = EmailMessage()
            em['From'] = self.userid
            em['To'] = to_email
            em['Subject'] = self.subject
            em.set_content(message)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp_service:
                smtp_service.login(self.userid,self.userpass)
                smtp_service.sendmail(self.userid,to_email,em.as_string())
                smtp_service.quit()
                print("Sent Email Successfully ;)")
        except Exception as ex :
            print(":(  ERROR...", ex)   

