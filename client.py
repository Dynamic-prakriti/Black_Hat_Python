import socket
target_host = "127.0.0.1"
target_port = 9999
def main():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((target_host,target_port))

    message = "Hello, server!"
    client.send(message.encode())

    response = client.recv(1024)
    print(f"[*] Received: {response.decode('utf-8')}")

    client.close()

if __name__=="__main__":
    main()