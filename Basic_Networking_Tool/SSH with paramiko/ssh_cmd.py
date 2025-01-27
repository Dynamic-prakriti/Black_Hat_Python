import paramiko

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())      # This line sets the policy for the client to automatically add the server to the list of known hosts
    client.connect(ip, port = int(port), username=user, password=passwd)   # This line connects to the server using the IP address, port number, username, and password provided by the user
    
    __, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())
            
    if __name__ == '__main__':
        import getpass
        # user = getpass.getuser()
        user = input('Username: ')
        password =  getpass.getpass()
        
        ip = input('Enter server IP: ') or '192.168.1.203'
        port = input('Enter port number: ') or 2222
        cmd = input('Enter command: ') or 'id'
        ssh_command(ip, user, password, cmd)
        
        