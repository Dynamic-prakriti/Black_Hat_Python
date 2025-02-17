
import socket

IP = ' '  #place IP address here
PORT = [...]  #replace port with the port number you want to listen on
def main():
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((IP,PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client,address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        handle_client(client)

def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*]Received: {request.decode("utf-8")}')
        sock.send(b'ACK')
        
if __name__=="__main__":
    main()
