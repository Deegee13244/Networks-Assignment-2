import socket
import threading
import time

# -- global variables --
s = socket.socket()
shutdown = False
serverMessage = ""


# -- classes --
class ReaderThread(threading.Thread):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        
    def run(self):
        global serverMessage
        try:
            while True:
                #Wait for a message
                serverMessage = self.socket.recv(1024).decode()
                if serverMessage.startswith("NOTICE"):
                    print('\n' + serverMessage)
        except Exception as e:
            print(f"Exception: {e}")

# -- functions ---
def wait_for_server():
    time.sleep(0.5)
    
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
    print('"%users" --> retrieves a list of all users in the group')
    print('"%message messageID" --> retrieves contents of specified message')
    print('"%leave" --> leaves the current group')
    print('"%exit" --> disconnect from the server and shutdown the client')

def runClient(username):
    global shutdown
    global serverMessage
    help()
    
    reader_thread = ReaderThread(s)
    reader_thread.start()
    
    while not shutdown:
        
        command = input("Enter a commmand: ")
        
        commandList = command.split(" ")
        
        #exit command
        if commandList[0] == "%exit":
            print("Disconnecting from server...")
            print("Goodbye!")
            send_message("EXIT " + username)
            shutdown = True
            break
        
        #join commmand
        elif commandList[0] == "%join":
            print("Requesting to join group 1...")
            send_message("JOIN " + username)
            wait_for_server()
            if serverMessage == "GROUP_JOINED":
                print("Successfully joined Group 1")
            elif serverMessage == "GROUP_JOIN_ERROR":
                print("Error: You may already be in this group")
            else:
                print("Error: Unexpected response from server")
                
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