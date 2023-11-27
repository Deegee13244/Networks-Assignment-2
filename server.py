import socket
import threading
import json
import random
from datetime import datetime

# Global Variables
activeConnections = []
activeAddresses = []
usernames = ["UsernameError"] #possible race condition if clients enter usernames in different order than connected?
threads = [0]
groups = ["Main", "Group_1", "Group_2", "Group_3", "Group_4"]
data = {}

# --- functions ---

#send a message to client. Client is determind by information passed into connectionInfo array
def send_message(connectionInfo, serverMessage):
    if not isinstance(serverMessage, list):
        serverMessage = [serverMessage]

    serverMessageStr = ''
    for item in serverMessage:
        print("Sending", item)
        if isinstance(item, list):
            for subitem in item:
                serverMessageStr += ' ' + subitem
        else:
            serverMessageStr += ' ' + item

    serverMessageStr = serverMessageStr[1:].encode()
    connectionInfo[0].send(serverMessageStr)
    print(connectionInfo[2], "client:", connectionInfo[1], 'send:', serverMessage)
    
#receive a message from a connected client. Client to listen to is determind by information passed into connnectionInfo array
def receive_message(connectionInfo):
    clientMessage = connectionInfo[0].recv(1024)
    clientMessage = clientMessage.decode()
    print(connectionInfo[2], "client:", connectionInfo[1], 'recv:', clientMessage)
    return clientMessage

#send a given message to all active clients 
#actually, this should be rewritten to only send messages to active clients WITHIN THE SAME group as current operation
def send_to_group(message, groupKey):
    for i in range(len(activeConnections)):
        if activeConnections[i] in data[groupKey]['Conns'] or groupKey == -1:
            connectionInfo = [activeConnections[i], activeAddresses[i], threads[i + 1]]
            send_message(connectionInfo, message)
        
#to be called when a client disconnects. Scrubs them from all arrays that keep track of them
def cleanup(connectionInfo, username):
    print(threads[connectionInfo[2]], "ending")
    for group in data.values():
        if username in group["Users"]:
            group["Users"].remove(username)
    activeConnections.remove(connectionInfo[0])
    activeAddresses.remove(connectionInfo[1])
    threads.remove(connectionInfo[2])
    usernames.remove(username)
    
def create_message(username, groupKey, subject, content):
    messageId = str(random.randint(1000, 9999))
    postDate = datetime.now().isoformat()
    message = {
        "ID": messageId,
        "Sender": username,
        "Post Date": postDate,
        "Subject": subject,
        "Content": content
    }
    #store entire message, including content to be retrieved later
    data[groupKey]["Messages"].update({messageId: message})
    
    #gets rid of the content field before message notification is sent
    #message.pop("Content")

    return json.dumps(message)

#runs each time a client connects
def handle_client(conn, addr):
    activeConnections.append(conn)
    activeAddresses.append(addr)
    threads.append(threads[-1] + 1)
    threadNumber = threads[-1]
    print(threads[threadNumber], "starting")
    
    connectionInfo = [conn, addr, threadNumber]

    clientMessage = receive_message(connectionInfo)
    
    if clientMessage == "Connected":
        send_message(connectionInfo, "Enter a username to connect:") #tell client to input username
        
        clientMessage = receive_message(connectionInfo) #receive inputted username from client side
        
        try:

            #if username exists, tell client to pick another username
            while clientMessage in usernames:
                send_message(connectionInfo, "Error: Username already in use. \nPlease provide valid username:")
                clientMessage = receive_message(connectionInfo)
                
            #add new user's username to usernames array
            usernames.append(clientMessage)
            currentUsername = clientMessage
            send_message(connectionInfo, "Welcome to the server.")
            
            clientConnected = True
            while clientConnected:
                clientMessage = receive_message(connectionInfo)
                
                clientMessageList = clientMessage.split(" ")
                
                #handle %exit command
                if clientMessageList[0] == "EXIT":
                    print(currentUsername, "has left the server")
                    cleanup(connectionInfo, currentUsername)
                    send_to_group("EXIT_NOTICE: " + currentUsername + " has disconnected from the server", key)
                    clientConnected = False
                    break

                elif clientMessageList[0] == "GROUPS":
                    print(currentUsername, "wants a list of groups")
                    print("Sending groups")
                    send_message(connectionInfo, ["SENDING_GROUPS", list(data.keys())])

                elif clientMessageList[0] == "GROUPJOIN":
                    if not clientMessageList[1]:
                        print(currentUsername, "%groupjoin command requires group id/name")
                        send_message(connectionInfo, "GROUP_JOIN_ERROR")
                        continue

                    print(currentUsername, f"wants to join Group {clientMessageList[1]}")

                    # Get the index pf a group if the input is an integer
                    key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])

                    if key not in data:
                        print(currentUsername, f"Group {clientMessageList[1]} does not exist")
                        send_message(connectionInfo, "GROUP_JOIN_ERROR")
                        continue

                    if currentUsername not in data[key]["Users"]:
                        data[key]["Users"].append(currentUsername)
                        data[key]["Conns"].append(conn)
                        print(currentUsername, f"has joined group {clientMessageList[1]}")
                        message_list = ["GROUP_JOINED", key]

                        # Prints out the two most recent messages when the group is joined
                        for i in range(min(2, len(data[key]["Messages"]))):
                            message_list.append(json.dumps(list(data[key]["Messages"].values())[-i]))

                        send_message(connectionInfo, message_list)

                    else:
                        print(currentUsername, f"tried to join group {clientMessageList[1]}, but is already in it")
                        send_message(connectionInfo, "GROUP_JOIN_ERROR")
                
                elif clientMessageList[0] == "GROUPPOST":
                    key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])
                    subject = clientMessageList[2]
                    content = clientMessageList[3]
                    print(currentUsername, f"wants to post in Group {key}")
                    if currentUsername in data[key]["Users"]:
                        message = create_message(currentUsername, key, subject, content)
                        #remove the content field from the message when it's sent as a notification
                        contentIndex = message.find("Content")
                        message = message[:contentIndex]
                        print("Posting message...")
                        send_to_group("NEW_POST" + message, key)
                    else:
                        print(currentUsername, f"tried to post a message to group {key}, but isn't in it")
                        send_message(connectionInfo, "POST_ERROR")
                        continue


                elif clientMessageList[0] == "GROUPUSERS":
                    print(currentUsername, "wants a list of users in their group")

                    key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])

                    if currentUsername in data[key]["Users"]:
                        print(f"Sending users in Group {key}")
                        send_message(connectionInfo, ["SENDING_USERS", key, data[key]["Users"]])
                    else:
                        print(currentUsername, f"tried to get group {key} users, but is not in the group")
                        send_message(connectionInfo, "USERS_ERROR")
                

                elif clientMessageList[0] == "GROUPLEAVE":
                    key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])
                    
                    if currentUsername in data[key]["Users"]:
                        data[key]["Users"].remove(currentUsername)
                        print(currentUsername, "has left the group")
                        send_to_group("LEAVE_NOTICE: " + currentUsername + " has left the group", key)
                    else:
                        send_message(connectionInfo, "LEAVE_ERROR")

                
                elif clientMessageList[0] == "GROUPMESSAGE":
                    key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])
                    messageID = clientMessageList[2]

                    if currentUsername in data[key]["Users"]:
                        print(messageID, messageID == "ALL")
                        if messageID == "ALL":
                            message_list = ["SENDING_MESSAGES", key]

                            for message in list(data[key]["Messages"].values()):
                                print(message)
                                message_list.append(json.dumps(message).replace(' ', '%20'))

                            if len(message_list) == 2:
                                message_list.append("No_Messages")
                                                       
                            send_message(connectionInfo, message_list)
                        else:
                            send_message(connectionInfo, json.dumps(data[key]["Messages"][messageID]))
                    else:
                        send_message(connectionInfo, "MESSAGE_ERROR")
        except Exception as e:
            print(str(e))
            print(f"Connection lost with {currentUsername}")
            print(currentUsername, "has left the server")
            cleanup(connectionInfo, currentUsername)
            send_to_group("EXIT_NOTICE: " + currentUsername + " has disconnected from the server", -1)
                
    conn.close()
   
# --- main ---

def main():
    host = '127.0.0.1'
    port = 8080

    for group in groups:
        data.update({group: {
            "Users": [],
            "Conns": [],
            "Messages": {}
        }})


    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)

    all_threads = []

    try:
        while True:
            print("Waiting for client")
            conn, addr = s.accept()
    
            print("Client:", addr)
        
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
    
            all_threads.append(t)
    except KeyboardInterrupt:
        print("Stopped by Ctrl+C")
    finally:
        if s:
            s.close()
        for t in all_threads:
            t.join()
            
if __name__ == '__main__':
    main()
