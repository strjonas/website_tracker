import time
import hashlib
from urllib.request import urlopen, Request
from send_email import send
import logging
from logging.handlers import RotatingFileHandler

def get_logger():
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file  = RotatingFileHandler('app.log', maxBytes=5*1024*1024, backupCount=5)
    file.setFormatter(formater)
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    logger.addHandler(file)
    return logger


# takes parameters: url, interval, email, message
class Tracker:
    def __init__(self, url=None, interval=None, email=None, message=None, remove=None):
        self.url = url
        self.interval = interval
        self.email = email
        self.message = message
        self.running = True
        self.remove = remove

        self.logger = get_logger()
        self.last_hash = self.get_hash()

    def remove_url(self):
        self.remove(self.url)
    
    def get_hash(self):
        # get the content of the url
        try:
            content = urlopen(Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})).read()
        except Exception as e:
            self.logger.error(f"Error getting content of {self.url}: {e}")
            return None
        # return the hash of the content
        return hashlib.sha256(content).hexdigest()

    def stop(self):
        self.running = False
        self.logger.info(f"Stopped tracker for {self.url}")

    def send_email(self, erorr=False):
        message = self.message if erorr == False else f"Tracker for {self.url} failed"
        subject = "Change detected" if erorr == False else "Tracker failed"
        # send the email
        try:
            send(message, self.email, subject=subject )
            pass
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return
        # send an email to the email address
        self.logger.info("Email sent to {}".format(self.email))

    def check(self):
        # get the current hash
        current_hash = self.get_hash()
        # check if the hash has changed
        if current_hash != self.last_hash:
            self.last_hash = current_hash
            self.send_email()

    def run(self):
        try:
            while self.running:
                # check if something has changed
                self.check()
                self.logger.info(f"Checked {self.url}")
                # sleep for the interval
                time.sleep(self.interval)
                raise Exception("test")
        except Exception as e:
            self.remove_url()
            self.logger.error(f"Tracker for {self.url} failed: {e}")
            try:
                self.send_email(erorr=True)
                self.stop()
            except Exception as e:
                self.logger.error(f"Error sending email: {e}")