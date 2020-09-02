import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

from patterndetector.result import Results

COMMASPACE = ', '

class EmailGenerator:
    def __init__(self, results: Results):
        self.results = results
        self.getEmailPass()
        self.outputString = ''
        self.outputHTML = '''\
<html>
  <head></head>
  <body>
'''
        self.renderOutput()

    def sendEmail(self, from_email, to_emails):
        if self.outputString == '':
            self.outputString = 'No patterns detected today'
            self.outputHTML = '<h1>No patterns detected today</h1>'
        email = MIMEMultipart('alternative')
        current_time = datetime.datetime.now()
        email['Subject'] = f'Pattern Detector Report ({current_time.strftime("%m/%d/%Y")})'
        email['From'] = f'Pattern Detector <{from_email}>'
        email['To'] = COMMASPACE.join(to_emails)

        plaintext = MIMEText(self.outputString, 'text')
        html = MIMEText(self.outputHTML, 'html')

        email.attach(plaintext)
        email.attach(html)

        email_password = self.getEmailPass()

        s = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        s.login(from_email, email_password)
        s.sendmail(from_email, to_emails, email.as_string())
        s.quit()

    def addDataToOutput(self, data):
        self.outputString += f"""\
Ticker: {data['ticker']}
Change: { data['percent_change']:.2f}%
Volume: {data['volume']}
RelativeVol: {data['relative_vol']:.2f}

"""
        self.outputHTML += f"""\
                <tr>
                    <td><a href="https://www.tradingview.com/chart?symbol={data['ticker']}">{data['ticker']}</a></td>
                    <td>{data['percent_change']:.2f}%</td>
                    <td>{data['volume']}</td>
                    <td>{data['relative_vol']:.2f}</td>
                </tr>
"""

    def beginSection(self, pattern):
        self.outputHTML += f"""\
        <h2>Tickers matching "{pattern}" pattern</h2>
        <table class="pure-table pure-table-horizontal">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Change</th>
                    <th>Volume</th>
                    <th>RelVol</th>
                </tr>
            </thead>
            <tbody>
"""
        self.outputString += f"\nTickers matching '{pattern}' pattern\n\n"

    def endSection(self):
        self.outputHTML += """\
            </tbody>
        </table>
"""

    def beginEmail(self):
        self.outputHTML += """\
<html>
    <body>
"""

    def endEmail(self):
        self.outputHTML += """\
    </body>
</html>
"""

    def renderOutput(self):
        results = self.results.getAllResults()
        for pattern in results:
            self.beginSection(pattern)
            for data in results[pattern].values():
                self.addDataToOutput(data)
            self.endSection()
        self.endEmail()

    def getEmailPass(self):
        try:
            return os.environ['EMAIL_PASS']
        except:
            password_file = open('app_pass.txt', 'r')
            password = password_file.read()
            password_file.close()
            return password