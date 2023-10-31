import socket

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set socket options (optional)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Define the host and port
host = '127.0.0.1'  # localhost
port = 12345

# Bind the socket to the host and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)

print("Server is listening on", host, "port", port)

# Accept a client connection
client_socket, client_address = server_socket.accept()

print("Received connection from", client_address)
# Send a response to the client
response_message = "Hello, client! Thank you for connecting."
client_socket.send(response_message.encode())

# Close the client and server sockets when done
client_socket.close()
server_socket.close()
