import datetime
from email.mime.text import MIMEText
import smtplib
import os

COMMASPACE = ', '

class EmailGenerator:
    def __init__(self, outputString):
        self.outputString = outputString

    def sendEmail(self, from_email, to_emails):
        if self.outputString == '':
            self.outputString = 'No patterns detected today'
        email = MIMEText(self.outputString)
        current_time = datetime.datetime.now()
        email['Subject'] = f'Pattern Detector Report ({current_time.strftime("%m/%d/%Y")})'
        email['From'] = f'Pattern Detector <{from_email}>'
        email['To'] = COMMASPACE.join(to_emails)

        email_password = self.getEmailPass()

        s = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        s.login(from_email, email_password)
        s.sendmail(from_email, to_emails, email.as_string())
        s.quit()

    def getEmailPass(self):
        try:
            return os.environ['EMAIL_PASS']
        except:
            password_file = open('app_pass.txt', 'r')
            password = password_file.read()
            password_file.close()
            return password