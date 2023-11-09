import socket
import threading

# Global Variables
usernames = ["UsernameError"] #possible race condition if clients enter usernames in different order than connected
threads = [0]

# --- functions ---

def send_message(connectionInfo, serverMessage):
    serverMessage = serverMessage.encode()
    connectionInfo[0].send(serverMessage)
    print(connectionInfo[2], "client:", connectionInfo[1], 'send:', serverMessage)

def handle_client(conn, addr):
    threads.append(threads[-1] + 1)
    threadNumber = threads[-1]
    print(threads[threadNumber], "starting")

    # recv message
    clientMessage = conn.recv(1024)
    clientMessage = clientMessage.decode()
    print(threadNumber, "client:", addr, 'recv:', clientMessage)
    
    connectionInfo = [conn, addr, threadNumber]
    
    if clientMessage == "Connected":
        send_message(connectionInfo, "Enter a username to connect:")
        
        clientMessage = conn.recv(1024)
        clientMessage = clientMessage.decode()
        print(threadNumber, "client:", addr, 'recv:', clientMessage)
        
        while clientMessage in usernames:
            send_message(connectionInfo, "Error: Username already in use. \nPlease provide valid username:")
            clientMessage = conn.recv(1024)
            clientMessage = clientMessage.decode()
            print(threadNumber, "client:", addr, 'recv:', clientMessage)
            
        usernames.append(clientMessage)
        send_message(connectionInfo, "Welcome to the server.")
                
    # simulate longer work
    #time.sleep(5)
    
    conn.close()

    print("[thread] ending")
   
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