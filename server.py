import socket
import threading

# Global Variables
usernames = ["UsernameError"] #possible race condition if clients enter usernames in different order than connected?
threads = [0]

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

#runs each time a client connects
def handle_client(conn, addr):
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
        send_message(connectionInfo, "Welcome to the server.")
                
    conn.close()

    print(threads[threadNumber], "ending")
   
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