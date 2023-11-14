import socket
import threading
import time
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
#for now, while only using 1 group, it's cool i guess
def send_to_all(message):
    for conn in activeConnections:

        i = 0
        connectionInfo = [conn, activeAddresses[i], threads[i + 1]]
        send_message(connectionInfo, message)
        
#to be called when a client disconnects. Scrubs them from all arrays that keep track of them
def cleanup(connectionInfo, username):
    print(threads[connectionInfo[2]], "ending")
    for group in groups:
        if username in group:
            group.remove(username)
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
                send_to_all("EXIT_NOTICE: " + currentUsername + " has disconnected from the server")
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

                print(currentUsername, f"wants to join Group {clientMessageList[1]}")

                key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])

                if currentUsername not in data[key]["Users"]:
                    data[key]["Users"].append(currentUsername)
                    print(currentUsername, f"has joined group {clientMessageList[1]}")
                    send_message(connectionInfo, ["GROUP_JOINED", key])
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
                    print("Posting message...")
                    send_to_all("NEW_POST" + message)
                else:
                    print(currentUsername, f"tried to post a message to group {key}, but isn't in it")
                    send_message(connectionInfo, "POST_ERROR")


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
                    send_to_all("LEAVE_NOTICE: " + currentUsername + " has left the group")
                else:
                    send_message(connectionInfo, "LEAVE_ERROR")

            
            elif clientMessageList[0] == "GROUPMESSAGE":
                key = (clientMessageList[1] if not clientMessageList[1].isdigit() else list(data.keys())[int(clientMessageList[1])])
                messageID = clientMessageList[2]

                if currentUsername in data[key]["Users"]:
                    send_message(connectionInfo, json.dumps(data[key]["Messages"][messageID]))
                else:
                    send_message(connectionInfo, "MESSAGE_ERROR")
                
    conn.close()
   
# --- main ---

def main():
    host = '127.0.0.1'
    port = 8080

    for group in groups:
        data.update({group: {
            "Users": [],
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
