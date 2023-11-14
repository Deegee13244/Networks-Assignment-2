import socket
import threading

# Global Variables
activeConnections = []
activeAddresses = []
usernames = ["UsernameError"] #possible race condition if clients enter usernames in different order than connected?
threads = [0]
group1Users = []
group2Users = []
group3Users = []
group4Users = []
group5Users = []

# --- functions ---

#send a message to client. Client is determind by information passed into connectionInfo array
def send_message(connectionInfo, serverMessage):
    serverMessage = serverMessage.encode()
    connectionInfo[0].send(serverMessage)
    print(connectionInfo[2], "client:", connectionInfo[1], 'send:', serverMessage)
    
#receive a message from a connected client. Client to listen to is determind by information passed into connnectionInfo array
def receive_message(connectionInfo):
    clientMessage = connectionInfo[0].recv(1024)
    clientMessage = clientMessage.decode()
    print(connectionInfo[2], "client:", connectionInfo[1], 'recv:', clientMessage)
    return clientMessage

#send a given message to all active clients
#this successfully sends a message, but how do we get clients to always be listening for a NOTICE message? 
def send_to_all(message):
    for conn in activeConnections:
        i = 0
        connectionInfo = [conn, activeAddresses[i], threads[i + 1]]
        send_message(connectionInfo, message)
        
#to be called when a client disconnects. Scrubs them from all arrays that keep track of them
def cleanup(connectionInfo, username):
    print(threads[connectionInfo[2]], "ending")
    groups = [group1Users, group2Users, group3Users, group4Users, group5Users]
    for group in groups:
        if username in group:
            group.remove(username)
    activeConnections.remove(connectionInfo[0])
    activeAddresses.remove(connectionInfo[1])
    threads.remove(connectionInfo[2])
    usernames.remove(username)

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
            
            if clientMessageList[0] == "EXIT":
                print(currentUsername, "has left the server")
                cleanup(connectionInfo, currentUsername)
                send_to_all("NOTICE: " + currentUsername + " has disconnected from the server")
                clientConnected = False
                break
            elif clientMessageList[0] == "JOIN":
                print(currentUsername, "wants to join Group 1")
                if currentUsername not in group1Users:
                    group1Users.append(currentUsername)
                    print(currentUsername, "has joined group 1")
                    send_message(connectionInfo, "GROUP_JOINED")
                else:
                    print(currentUsername, "tried to join group 1, but is already in it")
                    send_message(connectionInfo, "GROUP_JOIN_ERROR")
            elif clientMessageList[0] == "USERS":
                print(currentUsername, "wants a list of users")
                
    conn.close()
   
# --- main ---

def main():
    host = '127.0.0.1'
    port = 8080

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