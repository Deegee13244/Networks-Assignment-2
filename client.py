import socket

def main():
    #host = '127.0.0.1'
    #port = 8080

    s = socket.socket()
    shutdown = False

    print('Client Started. Available Commands:')
    print('%connect HostIP Port')
    print('%exit')

    command = ""
    ipAddress = ""
    port = ""
    while command != "%connect" and (not shutdown):
        command = input("Enter a command: ")
        
        commandComponents = command.split(" ") #split for each space
        if len(commandComponents) == 3:
            command = commandComponents[0]
            ipAddress = commandComponents[1]
            port = commandComponents[2]
        
        if command == "%connect":
            if ipAddress != '127.0.0.1':
                print('No server available at provided host address')
            if port != '8080':
                print('Invalid port number')
            s.connect((ipAddress, port))
            print("Successfully connected to server")

            message = "Client Connected"
            print('send:', message)
            message = message.encode()
            s.send(message)

            message = s.recv(1024)
            message = message.decode()
            print('recv:', message)
        
        elif command == "%exit":
            print("Client will be terminated, goodbye")
            shutdown = True
        else:
            print("Invalid command")
            command = ""
        
        
