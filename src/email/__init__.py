
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import smtplib
import time

class EMailService():
    def __init__(self, fromaddr, toaddr, server, port, password):
        self.subject_prefix = "Raspberry Pi Movement Detection"
        self.fromaddr = fromaddr
        self.toaddr = self._init_toadress(toaddr)
        self.server, self.server_port = server, port
        self.password = password
        self.time_FMT = '%Y-%m-%d %H:%M:%S\t(%Z %z)'
        self.start_time = time.strftime(self.time_FMT)

        self.send_email(f"The room occupancy observation service has been initialized!\n\n{self.start_time}", "Startup", filename=None)
        print(f"[{self.start_time}] EMail-Service has been started with following configuration:\nSender:\t\t{self.fromaddr}\nAdresse(s)\t{self.toaddr}\nSMTP-Settings:\t{self.server}, Port: {self.server_port}\n\n")

    def _init_toadress(self, toaddr):
        if type(self.toaddr) is not list:
            self.toaddr = [toaddr]
        else:
            self.toaddr = toaddr

    def __exit__(self):
        timestring = time.strftime(self.time_FMT)
        tdelta = datetime.strptime(timestring, self.time_FMT) - datetime.strptime(self.start_time, self.time_FMT)
        self.send_email(f"The room occupancy observation service has been shut down!\n\n{timestring}\n\nService has been up for {tdelta} (hours:minutes:seconds)", "Shutdown")

    def create_message(self, address, msg_body, subject, filename): 
        message = MIMEMultipart()
        message['From'] = self.fromaddr
        message['To'] = address
        message['Subject'] = " - ".join((self.subject_prefix,str(subject))) if subject is not None else str(self.subject_prefix)
        body = f"{msg_body}\n\n------\nThis message has been automatically sent from {self.fromaddr} to {address} at {time.strftime(self.time_FMT)}\n------"
        message.attach(MIMEText(body, 'plain'))

        message = self.attach_file_to_message(message, filename)
        return message

    def attach_file_to_message(self, message : MIMEMultipart, filename=None):
        if filename is not None:
            attachment = open(filename, "rb") 
            image = MIMEImage(attachment.read())
            attachment.close()
            image.add_header('Content-ID', f"<{filename}>") 
            message.attach(image)
        
        return message

    def establish_connection(self):
        # creates SMTP session 
        self.smtp_connection = smtplib.SMTP(self.server, self.server_port) 
        self.smtp_connection.starttls()
        self.smtp_connection.login(self.fromaddr, self.password)

    def quit_connection(self):
        self.smtp_connection.quit()

    def send_email_to_addr(self, address, message, subject, filename):
        message = self.create_message(address, message, subject, filename)
        res = self.smtp_connection.sendmail(self.fromaddr, address, message.as_string())
        print(f"result from sendmail: {res, type(res)}")

    def send_email(self, message, subject="Occupancy change", filename=None):        
        self.establish_connection()
        
        for address in self.toaddr:
            self.send_email_to_addr(address, message, subject, filename)
            
        self.quit_connection()
        return True
