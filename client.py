import socket
import threading
import time

# -- global variables --
s = socket.socket()
shutdown = False
serverMessage = ""


# -- classes --
class ReaderThread(threading.Thread):
    
    #initialize socket
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self._stop_event = threading.Event()
        
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    #readerThread class receives server message after it starts and until it is stopped
    def run(self):
        global serverMessage
        try:
            while not self.stopped():
                # Wait for a message
                serverMessage = self.socket.recv(1024).decode()
                # Messages starting with these may come from server at any moment
                # when they come, print the message to all clients in that group
                if (
                    serverMessage.startswith("EXIT_NOTICE")
                    or serverMessage.startswith("NEW_POST")
                    or serverMessage.startswith("LEAVE_NOTICE")
                ):
                    print("\n" + serverMessage)
        except Exception as e:
            print(f"Exception: {e}")


# -- functions ---
#give the server time to compute and process
def wait_for_server():
    time.sleep(0.5)

#encode and send a message to the server
def send_message(clientMessage):
    clientMessage = clientMessage.encode()
    s.send(clientMessage)

#receive a message from the server. This functionality is later replaced by the use of the ReaderThread class
def receive_message():
    serverMessage = s.recv(1024)
    serverMessage = serverMessage.decode()
    return serverMessage


# Prints out the available commands that the user may enter with their respective arguments and description
def help():
    print("Available Commands:")
    print("Part 1 Commands")
    print('"%join" --> joins the default group message board')
    print('"%post subject content" --> posts a message to the default board')
    print('"%users" --> retrieves a list of all users in default group')
    print('"%message messageID" --> retrieves contents of specified message')
    print('"%leave" --> leaves the current group')
    print('"%exit" --> disconnect from the server and shutdown the client')
    print("Part 2 Commands")
    print('"%groups" --> retrieve a list of all groups that can be joined')
    print('"%groupjoin groupID" --> join the specified group')
    print('"%grouppost groupID subject content" --> posts a message to the specified group')
    print('"%groupusers groupID" --> retrieves a list of users in the specified group')
    print('"%groupleave groupID" --> leave a specific group.')
    print('"%groupmessage groupID messageID" --> retrieves the content of the message posted earlier on a message board in the specified group')


#runs once the client has been connected and picked a username
def runClient(username):
    global shutdown
    global serverMessage
    help()

    reader_thread = ReaderThread(s)
    reader_thread.start()

    #loop that runs until client wishes to disconnect from the server
    while not shutdown:
        command = input("Enter a commmand: ")

        commandList = command.split(" ")

        # exit command
        if commandList[0] == "%exit":
            print("Disconnecting from server...")
            print("Goodbye!")
            send_message("EXIT " + username)
            shutdown = True
            break

        # groups command - gets a list of groups from a server message
        # and prints them to the client
        elif commandList[0] == "%groups":
            print("Getting list of groups...")
            send_message("GROUPS " + username)
            wait_for_server()
            serverMessageList = serverMessage.split(" ")
            if serverMessageList[0] == "SENDING_GROUPS":
                print("Group names:")
                for groupName in serverMessageList[1:]:
                    print(groupName)
            else:
                print("Error: Unexpected response from server")

        # join and groupjoin commmand - sends a request to the server to join 
        # a specified group. If successful message comes back from server, show
        # the client other users in that group and recent messages
        elif commandList[0] == "%join" or commandList[0] == "%groupjoin":
            if commandList[0] == "%groupjoin" and len(commandList) != 2:
                print("Error: Please provide 1 argument to %groupjoin command")
            else:
                group = commandList[1] if commandList[0] == "%groupjoin" else "0"

                print(f"Requesting to join group {group}...")
                send_message("GROUPJOIN " + group)
                wait_for_server()
                serverMessageList = serverMessage.split(" ")

                if serverMessageList[0] == "GROUP_JOINED":
                    print(f"Successfully joined {serverMessageList[1]} ")

                    # Time to show list of users in that group
                    print("Getting list of users...")
                    send_message("GROUPUSERS " + group)
                    wait_for_server()
                    serverMessageList = serverMessage.split(" ")
                    print(f"{serverMessageList[1]} users:")
                    for userName in serverMessageList[2:]:
                        print(userName)

                    # Time to show list of recent messages in that group
                    print("Getting recent messages...")
                    send_message("GROUPMESSAGE " + group + " ALL")
                    wait_for_server()
                    serverMessageList = serverMessage.split(" ")
                    print(f"{serverMessageList[1]} recent messages:")
                    for message in serverMessageList[-min(len(serverMessageList) - 2, 2):]:
                        print(message.replace('%20', ' '))

                elif serverMessageList[0] == "GROUP_JOIN_ERROR":
                    print("Error: You may already be in this group")
                else:
                    print("Error: Unexpected response from server")

        # users and groupusers command - gets the list of users in a specified group
        # from the server, server looks at users in that group and returns a list
        elif commandList[0] == "%users" or commandList[0] == "%groupusers":
            if commandList[0] == "%groupusers" and len(commandList) != 2:
                print("Error: Please provide 1 argument to %groupusers command")
            else:
                group = commandList[1] if commandList[0] == "%groupusers" else "0"
                print("Getting list of users...")
                send_message("GROUPUSERS " + group)
                wait_for_server()
                serverMessageList = serverMessage.split(" ")
                if serverMessageList[0] == "SENDING_USERS":
                    print(f"{serverMessageList[1]} users:")
                    for userName in serverMessageList[2:]:
                        print(userName)
                elif serverMessageList[0] == "USERS_ERROR":
                    print(f"Error: Please join Group {group} to view its users")
                else:
                    print("Error: Unexpected response from server")

        # post and grouppost command - creates a new message that gets sent to
        # the server to then be sent to clients in the same group
        elif commandList[0] == "%post" or commandList[0] == "%grouppost":
            if commandList[0] == "%post" and len(commandList) != 3:
                print("Error: Please provide 2 arguments to %post command")
            elif commandList[0] == "%grouppost" and len(commandList) != 4:
                print("Error: Please provide 3 arguments to %grouppost command")
            else:
                group = commandList[1] if commandList[0] == "%grouppost" else "0"
                subject = commandList[2 - (commandList[0] == "%post")]
                content = commandList[3 - (commandList[0] == "%post")]

                print("Posting message...")
                send_message("GROUPPOST " + group + " " + subject + " " + content)
                wait_for_server()
                serverMessageList = serverMessage.split(" ")
                if serverMessageList[0] == "POST_ERROR":
                    print("Error: Please join group to post in it")
                elif serverMessage.startswith("NEW_POST"):
                    print(f"Your message was successfully posted in the group")
                else:
                    print("Error: Unexpected response from server")

        # leave and groupleave commands - leaves a specified group,
        # the server removes that user from the group on it's end and sends a
        # message to all clients in that group that the user has left
        elif commandList[0] == "%leave" or commandList[0] == "%groupleave":
            if commandList[0] == "%groupleave" and len(commandList) != 2:
                print("Error: Please provide 1 argument to %groupleave command")
            else:
                group = commandList[1] if commandList[0] == "%groupleave" else "0"

                print("Leaving group...")
                send_message("GROUPLEAVE " + group)
                wait_for_server()
                if serverMessage.startswith("LEAVE_NOTICE"):
                    print("You have been removed from the group")
                elif serverMessage == "LEAVE_ERROR":
                    print("Error: You must be in a group to leave it")
                else:
                    print("Error: Unexpected response from server")

        # message and groupmessage commands - tells the server to look for a message
        # corresponding to the ID given, the server then sends the entire message content back
        elif commandList[0] == "%message" or commandList[0] == "%groupmessage":
            if commandList[0] == "%message" and len(commandList) != 2:
                print("Error: Please provide 1 argument to %message command")
            if commandList[0] == "%groupmessage" and len(commandList) != 3:
                print("Error: Please provide 2 arguments to %groupmessage command")
            else:
                group = commandList[1] if commandList[0] == "%groupmessage" else "0"
                messageID = commandList[2 - (commandList[0] == "%message")]

                send_message("GROUPMESSAGE " + group + " " + messageID)
                wait_for_server()

                print(serverMessage)


# --- main ---
#program start point
def main():
    global shutdown

    print('Client Started. Please use "%connect host# port#" to start or %exit')
    print('If running on local machine, use 127.0.0.1 and 8080 as host and port numbers')

    command = ""
    
    #loop to run while user is attempting to get connected or exits client
    while command != "%connect" and (not shutdown):
        try:
            command = input("Enter a command: ")
            commandList = command.split(" ")
            if len(commandList) != 3 and commandList[0] == "%connect":
                print("Error: Please provide required arguments to the connect command")
                command = ""
            #connect to the server using host and port numbers
            elif commandList[0] == "%connect" and len(commandList) == 3:
                command = commandList[0]
                host = commandList[1]
                port = commandList[2]
                try:
                    s.connect((host, int(port)))
                except:
                    print("Server is not currently available")
                    command = ""
                    continue

                print("Successfully connected to server")

                #the following section up until the runClient call allows the user to choose a username
                messageToServer = "Connected"
                send_message(messageToServer)

                serverMessage = receive_message()
                print(serverMessage)

                username = input()
                send_message(username)

                serverMessage = receive_message()
                print(serverMessage)

                #the user picked a username that is already connected to the server
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
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    main()
