import socket

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server's host and port to connect to
server_host = '127.0.0.1'  # Replace with the server's IP address or hostname
server_port = 12345       # Replace with the server's port

# Connect to the server
client_socket.connect((server_host, server_port))

# Send data to the server
message = "Hello, server!"
client_socket.send(message.encode('utf-8'))

# Receive data from the server
data = client_socket.recv(1024)  # 1024 is the buffer size
print("Received from server:", data.decode('utf-8'))

# Close the client socket when done
client_socket.close()
