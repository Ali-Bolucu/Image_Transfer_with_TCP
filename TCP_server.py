import socket
import os
from _thread import *

absolute_path = os.path.dirname(os.path.abspath(__file__))
ThreadCount = 0

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 8079  # Port to listen on (non-privileged ports are > 1023)

# Create a TCP socket and bind it to the server's IP address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
print ("socket binded to %s" %(PORT))

server_socket.listen() # how many ports to listen
print(f"Server is listening on {HOST}:{PORT}...")




def multi_threaded_client(client_socket):
    server_message = ""
    
    while True:
        data = client_socket.recv(1024).decode('latin-1')
        print(f"[Client] {data}")
        
        if not data:
            break
        
        if data[:4] == 'Data':
            picture_path = os.path.join(absolute_path, 'pictures')    
            for child in os.listdir(picture_path):
                server_message += str(child) + ' '

            client_socket.sendall(server_message.encode())
        
        if data[:3] == 'Pic':
            data = data.replace("\0", "")
            print(f"[Pic] {data[3:]}")
        
            relative_path  = f'pictures\\{data[3:]}'
            full_path = os.path.join(absolute_path, relative_path)           

            print(full_path)

            file = open(full_path, 'rb')
            file_size = os.path.getsize(full_path)
            
            print(file_size)
            print(type(file_size))
            
            client_socket.sendall((str(file_size)).encode())
            
            picture_data = file.read(file_size)

            client_socket.sendall(picture_data)
            
            """
            while picture_data:
                server_socket.send(picture_data)
                picture_data = file.read(1024)
            """ 
            file.close()
            
        if data[:3] == 'Rec':
            data = data.replace("\0", "")
            print(f"[Pic] {data[3:]}")
        
            relative_path  = f'pictures\\{data[3:]}'
            full_path = os.path.join(absolute_path, relative_path)           

            file = open(full_path, "wb")

            size = client_socket.recv(1024).decode()
            print(size)

            image = client_socket.recv(int(size))
            file.write(image)
            file.close()

        
        if (server_message == "close") or (server_message == "exit"):
            print("closing")
            server_socket.close()
        
        
#---------------------------------------------------
        
while True:

    client_socket, client_address = server_socket.accept()
    print(f"Connected by {client_address}")
    
    start_new_thread(multi_threaded_client, (client_socket, ))


            

