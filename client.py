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
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        global serverMessage
        try:
            while not self.stopped():
                # Wait for a message
                serverMessage = self.socket.recv(1024).decode()
                if (
                    serverMessage.startswith("EXIT_NOTICE")
                    or serverMessage.startswith("NEW_POST")
                    or serverMessage.startswith("LEAVE_NOTICE")
                ):
                    print("\n" + serverMessage)
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

def runClient(username):
    global shutdown
    global serverMessage
    help()

    reader_thread = ReaderThread(s)
    reader_thread.start()

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

        # groups command
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

        # join and groupjoin commmand
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
                    #time to show list of users in that group
                    print("Getting list of users...")
                    send_message("GROUPUSERS " + group)
                    wait_for_server()
                    serverMessageList = serverMessage.split(" ")
                    print(f"{serverMessageList[1]} users:")
                    for userName in serverMessageList[2:]:
                        print(userName)
                elif serverMessageList[0] == "GROUP_JOIN_ERROR":
                    print("Error: You may already be in this group")
                else:
                    print("Error: Unexpected response from server")

        #users and groupusers command
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

        # post and grouppost command
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

        # leave and groupleave commands
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

        # message and groupmessage commands
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
def main():
    global shutdown

    print('Client Started. Please use "%connect host# port#" to start or %exit')
    print('If running on local machine, use 127.0.0.1 and 8080 as host and port numbers')

    command = ""
    while command != "%connect" and (not shutdown):
        try:
            command = input("Enter a command: ")
            commandList = command.split(" ")
            if len(commandList) != 3 and commandList[0] == "%connect":
                print("Error: Please provide required arguments to the connect command")
                command = ""
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
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    main()
