import os
import smtplib
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


    def send_email(self, to_email, description, module_name, hostname, timestamp,severity):
        try: 
            self.SUBJECT= f"{module_name} Alert - on {hostname}"
            body = f"""Dear Administrator,

    We hope this message finds you well. We are writing to bring your attention to a recent event in the {module_name} system. Below are the details of the alert:

Module Name: {module_name}

Hostname: {hostname}

Severity: {severity}

Timestamp: {timestamp}

Description:
{description}

Best regards,
Kmitl Cyber Security Operation Center"""

            em = EmailMessage()
            em['From'] = self.userid
            em['To'] = to_email
            em['Subject'] = self.SUBJECT
            em.set_content(body)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp_service:
                smtp_service.login(self.userid,self.userpass)
                smtp_service.sendmail(self.userid,to_email,em.as_string())
                smtp_service.quit()
                print("Sent Email Successfully ;)")
        except Exception as ex :
            print(":(  ERROR...", ex)   

