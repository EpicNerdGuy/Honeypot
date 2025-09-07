import logging
import socket
from logging.handlers import RotatingFileHandler
import paramiko 

logging_format= logging.Formatter('%(message)s')

funnel_logger=logging.getLogger("funnel logger")
funnel_logger.setLevel(logging.INFO)
funnel_handler= RotatingFileHandler('audit.log',maxBytes=2000,backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

creds_logger=logging.getLogger("creds logger")
creds_logger.setLevel(logging.INFO)
creds_handler= RotatingFileHandler('cmd_audit.log',maxBytes=2000,backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_logger)

def emulated_shell(channel,client_ip):
    channel.send(b'corporate-jumpbox2$')
    command= b""
    while True:
        char=channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()
        command+=char
        if char==b'\r':
            if command.strip()==b'exit':
                response=b'\nBye\n'
                channel.close()
            elif command.strip()==b'pwd':
                response=b'\n\usr\local\\' + b'\r\n'
            elif command.strip()==b'whoami':
                response=b'\n' + b'corpuser' + b'\r\n'
            elif command.strip()==b'ls':
                response=b'\n' + b'jumpbox.conf1' + b'\r\n'
            else:
                response=b'sudo: command not found:' + b'\r\n'
        channel.send(response)
        channel.send(b'corporate-jumpbox2$')
        command=b""

# SSH server 
class Server(paramiko.ServerInterface):
    def __init__(self,client_ip,input_username=None,input_password=None):
        self.client_ip=client_ip
        self.input_username=input_username
        self.input_password=input_password
        
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind=='session':
            return paramiko.OPEN_SUCCEEDED
        
    def get_allowed_auths(self):
        return 'password'
    
    def check_auth_password(self,username,password):
        if self.input_username is None and self.input_password is None:
            if username=='username' and password=='password':
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
    
    def check_channel_shell_request(self,channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def check_channel_exec_request(self, channel, command):
        command=str(command)
        return True   
    
                
            
                