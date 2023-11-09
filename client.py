import socket

# -- globab variables --
s = socket.socket()

# -- functions ---
def send_message(clientMessage):
    clientMessage = clientMessage.encode()
    s.send(clientMessage)
    
def receive_message():
    serverMessage = s.recv(1024)
    serverMessage = serverMessage.decode()
    print(serverMessage)
    return serverMessage

# --- main ---
def main():
    host = '127.0.0.1'
    port = 8080
    
    shutdown = False

    print('Client Started. Please use %connect to start or %exit')

    command = ""
    while command != "%connect" and (not shutdown):
        command = input("Enter a command: ")
        if command == "%connect":
            s.connect((host, port))
            print("Successfully connected to server")
        
            messageToServer = "Connected"
            send_message(messageToServer)

            serverMessage = receive_message()
        
            username = input()
            send_message(username)
            
            serverMessage = receive_message()
        
            while serverMessage.startswith("Error"):
                username = input()
                send_message(username)
                serverMessage = receive_message()
            
            serverMessage = receive_message()
        
        elif command == "%exit":
            print("Client will be terminated")
            shutdown = True
        else:
            print("Invalid command")
            command = ""
        
        
if __name__ == '__main__':
    main()