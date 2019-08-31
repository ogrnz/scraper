import re
import smtplib
import logging

logging.basicConfig(filename = 'crawls.log', format = '%(asctime)s:%(levelname)s: %(message)s', level = logging.DEBUG)

"""Analyse crawls.log and detect if there was an error in the last import"""

class AnalyseLogHandler:

    """Regex to use to detect errors in logs"""
    PATTERN = 'ERROR|CRITICAL'

    def __init__(self, log_path):
        self.log_path = log_path

    def getLogPath(self):
        return self.log_path

    def analyseLastLines(self, logFile):
        lines = logFile.readlines()
        
        """How many last lines should we go back and check in the log file"""
        last_lines = lines[-4:]
        errors = []

        for line in last_lines:
            is_error = re.search(self.PATTERN, line)
            if(is_error is not None):
                errors.append(line)
        return errors

    def getLog(self):
        with open(self.getLogPath(), "r") as f:
            return self.analyseLastLines(f)
                  
x = AnalyseLogHandler('crawls.log')
errors = x.getLog()

"""Prepare to send email if we have error(s)"""

sender = 'web@whenwillibe10000daysold.icu'
mail_pwd = ''
receiver = 'olivier.grognuz@gmail.com'
message = """From: From Pi <web@whenwillibe10000daysold.icu>
To: To Olivier <olivier.grognuz@gmail.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Crawler errors detected

<h2>Some errors were detected:</h2>
"""

if(len(errors) > 0):
    for error in errors:
        message += error
        message += "\n"
    try:
        mail = smtplib.SMTP('mail.infomaniak.com', 587)
        mail.starttls()
        mail.login(sender, mail_pwd)
        mail.sendmail(sender, receiver, message)
        mail.quit()         
        logging.info('Successfully sent email')
    except smtplib.SMTPException as e:
        logging.error(f"Error: unable to send email : {e}")
