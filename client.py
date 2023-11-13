import socket

# -- globab variables --
s = socket.socket()
shutdown = False

# -- functions ---
def send_message(clientMessage):
    clientMessage = clientMessage.encode()
    s.send(clientMessage)
    
def receive_message():
    serverMessage = s.recv(1024)
    serverMessage = serverMessage.decode()
    return serverMessage

def help():
    print('Available Commands:')
    print('"%join" --> joins the default group message board (Group 1)')
    print('"%post subject content" --> posts a message to the board')
    print('"%users" --> retrievs a list of all users in the group')
    print('"%message messageID" --> retrieves contents of specified message')
    print('"%leave" --> leaves the current group')
    print('"%exit" --> disconnect from the server and shutdown the client')

def runClient(username):
    global shutdown
    help()
    serverMessage = ""
    
    while not shutdown:
        command = input("Enter a commmand: ")
        
        commandList = command.split(" ")
        
        #exit command
        if commandList[0] == "%exit":
            print("Disconnecting from server...")
            send_message("EXIT " + username)
            shutdown = True
            break
        
        #join commmand
        elif commandList[0] == "%join":
            print("Requesting to join group 1...")
            send_message("JOIN " + username)
            serverMessage = receive_message()
            if serverMessage == "GROUP_JOINED":
                print("Successfully joined Group 1")
            elif serverMessage == "GROUP_JOIN_ERROR":
                print("Error: You may already be in this group")
            else:
                print("Error: Unexpected response from server")
            serverMessage = ""
                
        else:
            print("Command not recognized. Please enter valid command")
            
# --- main ---
def main():
    global shutdown
    host = '127.0.0.1'
    port = 8080

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
            print(serverMessage)
        
            username = input()
            send_message(username)
            
            serverMessage = receive_message()
            print(serverMessage)
        
            while serverMessage.startswith("Error"):
                username = input()
                send_message(username)
                serverMessage = receive_message()
                print(serverMessage)
            
            runClient(username)
        
        elif command == "%exit":
            print("Client will be terminated")
            shutdown = True
        else:
            print("Invalid command")
            command = ""
        
        
if __name__ == '__main__':
    main()