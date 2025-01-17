import argparse    # Importing the argparse module(CLI Arguments)
import socket      # Importing the socket module(IP+Port)
import shlex       # Importing the shlex module(lexical Analyzers)
import subprocess  # Importing the subprocess module(Execute the command)
import sys         # Importing the sys module(Interacting with the Python Interpreter)
import textwrap    # Importing the textwrap module(Formatting the text)
import threading   # Importing the threading module(Threading)

def execute(cmd):
    cmd = cmd.strip()    # Removing the leading and trailing whitespaces
    if not cmd:
        return
   
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
   
    return output.decode()

class NetCat:     # Creating the NetCat class
    def __init__(self, args, buffer=None):  # Defining the __init__ method to initialize the attributes
        self.args = args                    # Assigning the args to the self.args for the class
        self.buffer = buffer                
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Creating the socket object
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Setting the socket options
   
    def run(self):                                                      # Defining the run method
        if self.args.listen:
            self.listen()
        else:
            self.send()
   
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
           
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()
           
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()
           
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
           
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
           
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()
                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(                 # Creating the ArgumentParser object
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,   # Formatting the text
        # Example of the usage of the script
        epilog=textwrap.dedent('''Example:                      
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e =\"cat /etc/passwd\" # command shell
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')   # Adding the command shell argument
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    if args.listen:
        buffer = ''
        
    else:
        buffer = sys.stdin.read()
        
    nc = NetCat(args, buffer.encode())
    nc.run()
   
   
   
#Run
# python3 ReplacingNetcat.py --help
# python3 ReplacingNetcat.py -t server_IP -p port -l -c
# python3 ReplacingNetcat.py -t server_IP -p port -l -u=file_to_upload
# on client side/local machine
# python3 ReplacingNetcat.py -t server_IP -p port or nc server_IP port