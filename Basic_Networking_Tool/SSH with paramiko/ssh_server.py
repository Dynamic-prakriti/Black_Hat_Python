import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOST_KEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key')) # This is the private key, place path to your private key file here

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()     
        
    def check_channel_request(self, kind, chanid):         # This method is called when a new channel is requested by the client
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED                  # This method returns a value of paramiko.OPEN_SUCCEEDED if the channel request is accepted
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if(username == 'test') and (password == 'test'):
            return paramiko.AUTH_SUCCESSFUL
        
if __name__ == '__main__':
    server : '[server_IP]'    # Enter the server IP here
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # This line creates a socket object
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # This line allows the server to reuse the same port number
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!',client,addr)
        
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOST_KEY)
    server = Server()
    bhSession.start_server(server=server)
    
    chan = bhSession.accept(20)
    if chan is None:
        print('*** No channel.')
        sys.exit(1)
        
    print('[+] Authenticated!')
    print(chan.recv(1024))
    chan.send('Welcome to bh_ssh')
    try:
        while True:
            command = input('Enter command: ')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024).decode() + '\n')
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()
       