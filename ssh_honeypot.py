import logging
import socket
from logging.handlers import RotatingFileHandler
import paramiko 
import threading 
import sys
import signal

logging_format= logging.Formatter('%(asctime)s-%(message)s')
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

def signal_handler(sig,frame):
    print("\n...Shutting Down Honeypot...\n")
    sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)
def emulated_shell(channel, client_ip):
    import socket  # needed for socket.timeout
    channel.settimeout(0.5)                # don't block forever
    prompt = b'corporate-jumpbox2$ '
    line_buf = bytearray()
    channel.send(prompt)

    while True:
        try:
            data = channel.recv(1024)
            if not data:
        
                try:
                    channel.close()
                except Exception:
                    pass
                break
        except socket.timeout:
           
            continue
        except Exception:
       
            try:
                channel.close()
            except Exception:
                pass
            break

     
        for byte in data:
            b = bytes([byte])

         
            if byte == 3:
                channel.send(b'^C\r\n')
                line_buf.clear()
                channel.send(prompt)
                continue

            
            if byte == 4:
                channel.send(b'\r\nBye\r\n')
                try:
                    channel.close()
                except Exception:
                    pass
                return

          
            if byte in (8, 127):
                if len(line_buf) > 0:
                   
                    line_buf.pop()
                    channel.send(b'\b \b')
               
                continue

           
            if byte in (10, 13):
                # move cursor to new line first (echo)
                channel.send(b'\r\n')
                cmd = bytes(line_buf).strip()
             
                cmd_str = cmd.decode('utf-8', errors='ignore')
                creds_logger.info(f'Command {cmd_str} from {client_ip}')

                # dispatch fake commands
                if cmd == b'exit':
                    channel.send(b'Bye\r\n')
                    try:
                        channel.close()
                    except Exception:
                        pass
                    return
                elif cmd == b'pwd':
                    channel.send(b'/usr/local/\r\n')
                elif cmd == b'whoami':
                    channel.send(b'corpuser\r\n')
                elif cmd == b'ls':
                    channel.send(b'jumpbox.conf1\r\n')
                elif cmd.startswith(b'cd'):
                  
                    channel.send(b'')
                elif cmd == b'':
                   
                    pass
                else:
                    channel.send(b'command not found\r\n')

           
                channel.send(prompt)
                line_buf.clear()
                continue

            if 32 <= byte <= 126:
                channel.send(b)
                line_buf.append(byte)
            else:
                pass




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
        funnel_logger.info(f'Client {self.client_ip} attempted connection with'+f'username: {username},'+f'password: {password}')
        creds_logger.info(f'{self.client_ip},{username},{password}')
        return paramiko.AUTH_SUCCESSFUL
        

    
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
        sock.settimeout(1)
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
        except socket.timeout:
            continue
        except Exception:
            break
honeypot(None,None,2222,'127.0.0.1')
            
        
    
    
    
              
          
          
          
          
        
    
          
          
      
    
                
            
                