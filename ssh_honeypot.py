import logging
import socket
from logging.handlers import RotatingFileHandler
import paramiko 
import threading 
import sys

logging_format= logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"
host_key = paramiko.RSAKey(filename="server.key")

funnel_logger=logging.getLogger("funnel logger")
funnel_logger.setLevel(logging.INFO)
funnel_handler= RotatingFileHandler('audit.log',maxBytes=2000,backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

creds_logger=logging.getLogger("creds logger")
creds_logger.setLevel(logging.INFO)
creds_handler= RotatingFileHandler('cmd_audit.log',maxBytes=2000,backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

def emulated_shell(channel, client_ip):
    channel.send(b'corporate-jumpbox2$')
    command = b""
    while True:
        char = channel.recv(1)
        if not char:
            channel.close()
            break
        channel.send(char)
        command += char

        if char == b'\r':
            cmd = command.strip()

            if cmd == b'exit':
                channel.send(b'\nBye\n')
                channel.close()
                break
            elif cmd == b'pwd':
                response = b'\n/usr/local/\r\n'
            elif cmd == b'whoami':
                response = b'\ncorpuser\r\n'
            elif cmd == b'ls':
                response = b'\njumpbox.conf1\r\n'
            else:
                response = b'sudo: command not found\r\n'

            channel.send(response)
            channel.send(b'corporate-jumpbox2$')
            command = b""


# SSH server 
class Server(paramiko.ServerInterface):
    def __init__(self,client_ip,input_username=None,input_password=None):
        self.client_ip=client_ip
        self.event=threading.Event()
        self.input_username=input_username
        self.input_password=input_password
        
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind=='session':
            return paramiko.OPEN_SUCCEEDED
        
    def get_allowed_auths(self,username):
        return 'password'
    
    def check_auth_password(self, username, password):
        if username == self.input_username and password == self.input_password:
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
    
def client_handle(client,addr,username,password):
      client_ip=addr[0]
      print(f'Connection from {client_ip}')
      try:
          transport=paramiko.Transport(client )
          server=Server(client_ip=client_ip,input_username=username,input_password=password)
          transport.add_server_key(host_key)
          transport.start_server(server=server)
          channel=transport.accept(100)
          if channel is None:
              print("No channel was opened")
          channel.send("Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-144-generic x86_64)\r\n")
          emulated_shell(channel,client_ip=client_ip )
      except Exception as error:
          print(error) 
      finally:
          try:
              transport.close()
          except Exception as error:
              print(error)
          client.close()

def honeypot(username,password,port,address):
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind((address,port))
        sock.listen(100)
        print(f'SSH Server is listening on port {port}')
    except socket.error as e:
        print(f'Socket error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error occoured: {e}")
        sys.exit(1)
    while True:
        try:
            client,addr=sock.accept()
            ssh_honeypot_thread=threading.Thread(target=client_handle,args=(client,addr,username,password))
            ssh_honeypot_thread.start()
        except Exception as e:
            print(e)
honeypot('username','password',2222,'127.0.0.1')
            
        
    
    
    
              
          
          
          
          
        
    
          
          
      
    
                
            
                