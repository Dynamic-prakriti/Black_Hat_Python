import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])  #contains ASCII printable characters


# hexdump function to display the communication between the local and remote machine to the console
def hexdump (src, length=16, show=True):
    if isinstance(src, bytes):                    
        src = src.decode()              #decode the bytes if a byte string was passed
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])        #grab a piece of string to dump & put it in the word variable
        printable = word.translate(HEX_FILTER) #translate the word to printable characters
        hexa = ' '.join([f'{ord(c):02X}' for c in word])  #convert the word to hex
        hexwidth = length*3                 #calculate the width of the hex column  
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}') #append the results to the list
    if show:
        for line in results:
            print(line)
    else:
        return results
    
#receive_from function to receive data from the socket 
def receive_from(connection):
    buffer = b""                #initialize the buffer to an empty byte string
    connection.settimeout(5)    #set the timeout to 5 seconds
    try:
        while True:
            data = connection.recv(4096)  #receive data from the connection
            if not data:
                break
            buffer += data             #append the data to the buffer
    except Exception as e:
       pass
    return buffer
    
    
#to modify the request and response packet before the proxy send packets to the remote server or the local client
#you can modify the packet contents,perform fuzzing tasks, or any other packet manipulation tasks
def request_handler(buffer):
    #perform packet modifications
    return buffer

def response_handler(buffer):
    #perform packet modifications
    return buffer


#to manage traffic direction between the local and remote machine
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a new socket object
    remote_socket.connect((remote_host, remote_port))  #connect to the remote host
    if receive_first:
        remote_buffer = receive_from(remote_socket)  #receive data from the remote host
        hexdump(remote_buffer)  #display the data received from the remote host
        remote_buffer = response_handler(remote_buffer)  #modify the data received from the remote host
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)  #send the modified data to the local client
    while True:
        local_buffer = receive_from(client_socket)  #receive data from the local client
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)  #display the data received from the local client
            
            local_buffer = request_handler(local_buffer)  #modify the data received from the local client
            remote_socket.send(local_buffer)  #send the modified data to the remote host
            print("[==>] Sent to remote.")
            
        remote_buffer = receive_from(remote_socket)  #receive data from the remote host
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)  #display the data received from the remote host
            
            remote_buffer = response_handler(remote_buffer)  #modify the data received from the remote host
            client_socket.send(remote_buffer)  #send the modified data to the local client
            print("[<==] Sent to localhost.")
            
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()  #close the client socket
            remote_socket.close()  #close the remote socket
            print("[*] No more data. Closing connections.")
            break
        
#to set up listening socket and pass it to our proxy_handler
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a new socket object
    try:
        server.bind((local_host, local_port))  #bind the socket to the local host and port
    except Exception as e:
        print('problem in binding the socket: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
        
    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)  #listen for incoming connections
    while True:
        client_socket, addr = server.accept()  #accept incoming connections
        # print out the local connection information
        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))
        
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))  #create a new thread
        proxy_thread.start()  #start the thread
        
#main function to parse the command line arguments and call the server_loop function
def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./TCP_Proxy.py [localhost] [localport]", end="")
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./TCP_Proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
        
    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    # this tells our proxy to connect and receive data before sending to the remote host
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
        
    # now spin up our listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
    
if __name__ == "__main__":
    main()
    
    
    
# Test it in ftp server
# python3 TCP_Proxy.py
# Usage: ./TCP_Proxy.py [localhost] [localport][remotehost] [remoteport] [receive_first]
# Example: ./TCP_Proxy.py localhost_ip 21 ftp_server_ip 21 True
#initiate the connection to the ftp server
# ftp ftp_server_ip