import socket

# --- main ---

host = '127.0.0.1'
port = 8080

s = socket.socket()
shutdown = False

print('Client Started. Please use %connect to start or %exit')

command = ""
while command != "%connect" and (not shutdown):
    command = input("Enter a command: ")
    if command == "%connect":
        s.connect((host, port))
        print("Successfully connected to server")
        
        message = "Connected"
        print('send:', message)
        message = message.encode()
        s.send(message)

        message = s.recv(1024)
        message = message.decode()
        print(message)
        
        username = input()
        username = username.encode()
        s.send(username)
        
        while message.startswith("Error"):
            username = input()
            username = username.encode()
            s.send(username)
            
        message = s.recv(1024)
        message = message.decode()
        print(message)
        
    elif command == "%exit":
        print("Client will be terminated")
        shutdown = True
    else:
        print("Invalid command")
        command = ""
        
        
