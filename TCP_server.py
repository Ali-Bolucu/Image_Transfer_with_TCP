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

def recv(full_path):
     

    file = open(full_path, "wb")

    imageSize = int(client_socket.recv(15).decode('latin-1'))

    
    totalPacketSize = 9 + 10240 + 9
    TCP_PacketNumber = 1
    packetSize = 10240
    localChecksum = 0
    TCP_Checksum = 0

    TCP_BytesReceived = 0
    TCP_TotalBytesReceived = 0
    TCP_TotalPacketNumber = imageSize // packetSize + (1 if imageSize % packetSize > 0 else 0)

    print(imageSize)
    print(TCP_TotalPacketNumber)
    print("\n")
    
    while not (TCP_TotalPacketNumber == int(TCP_PacketNumber)) :
        
        TCP_PacketNumber = client_socket.recv(9).decode('latin-1')
        TCP_PacketNumber = TCP_PacketNumber.lstrip("0")
        
        imageData = client_socket.recv(10240)
        
        TCP_Checksum = client_socket.recv(9).decode('latin-1')
        TCP_Checksum = TCP_Checksum.lstrip("0")
        
        client_socket.sendall("ACK".encode())
        
        print(TCP_PacketNumber)
        print(TCP_Checksum)
        print("\n")
        file.write(imageData)
        
        print()
        
    print("end")
    file.close()

        
    


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
        
            relative_path  = f'pictures/{data[3:]}'
            full_path = os.path.join(absolute_path, relative_path)           

            print(full_path)

            file = open(full_path, 'rb')
            imageSize = os.path.getsize(full_path)
            
            print( "ImageSize :" + str(imageSize))
            print(type(imageSize))
            print("\n")
            client_socket.send((str(imageSize)).encode())
            imageData = file.read()
   
            totalPacketSize = 9 + 10240 + 9
            TCP_PacketNumber = 1
            packetSize = 10240
            localChecksum = 0
            TCP_Checksum = 0

            TCP_BytesReceived = 0
            TCP_TotalBytesReceived = 0
            TCP_TotalPacketNumber = imageSize // packetSize + (1 if imageSize % packetSize > 0 else 0)

            for i in range(0, len(imageData) , packetSize):
                
                str_TCP_PacketNumber = '{:0>9}'.format(str(TCP_PacketNumber))
                client_socket.send(str_TCP_PacketNumber.encode())
                print( str(TCP_PacketNumber))
                TCP_PacketNumber += 1
                
                packet = imageData[i:i+packetSize]
                # for the last packet
                if len(packet) < packetSize:
                    packet += b'\x00' * (packetSize - len(packet))
                client_socket.send(packet)

                

            
                TCP_Checksum = 0
                for a in range(0, packetSize):
                    TCP_Checksum += packet[a]
                str_TCP_Checksum = '{:0>9}'.format(str(TCP_Checksum))
                client_socket.send(str_TCP_Checksum.encode())
            
    
                
                
                print( str(TCP_Checksum))
                
                ACK_NCK = client_socket.recv(4).decode('latin-1')
                print(ACK_NCK + "\n")
                
                

            #print("aaa")   
            #print(TCP_PacketNumber)
            file.close()
            
            
        if data[:3] == 'Rec':
            data = data.replace("\0", "")
            print(f"[Pic] {data[3:]}")

            relative_path  = f'pictures/{data[3:]}'
            full_path = os.path.join(absolute_path, relative_path)      
            recv(full_path)
            
        
#---------------------------------------------------
        
while True:

    client_socket, client_address = server_socket.accept()
    print(f"Connected by {client_address}")
    
    start_new_thread(multi_threaded_client, (client_socket, ))


            

