import time
import socket
import os
from _thread import *
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from functools import partial


absolute_path = os.path.dirname(os.path.abspath(__file__))
folderPathCV = os.path.join(absolute_path, "imagesCV")
folderPathMap = os.path.join(absolute_path, "imagesMap")

ThreadCount = 0
HOST = '0.0.0.0'



def recv(full_path, client_socket):
     
    # creates a file in given path
    file = open(full_path, "wb")

    # receive the image size in 15 bytes
    imageSize = client_socket.recv(15).decode('latin-1')
    imageSize = int(imageSize.lstrip("0"))

    # variables
    totalPacketSize = 9 + 10240 + 9
    TCP_PacketNumber = 1
    packetSize = 1024
    localChecksum = 0
    TCP_Checksum = 0

    TCP_BytesReceived = 0
    TCP_TotalBytesReceived = 0
    TCP_TotalPacketNumber = imageSize // packetSize + (1 if imageSize % packetSize > 0 else 0)
    # --

    print("Image Size : " + str(imageSize))
    print("Expected Packet Number : " + str(TCP_TotalPacketNumber))
    print("\n")
    
    while not (TCP_TotalPacketNumber == TCP_PacketNumber) :
        
        TCP_PacketNumber = client_socket.recv(9).decode('latin-1')
        TCP_PacketNumber = int(TCP_PacketNumber.lstrip("#"))
        
        imageData = client_socket.recv(1024)
        
        TCP_Checksum = client_socket.recv(9).decode('latin-1')
        TCP_Checksum = int(TCP_Checksum.lstrip("#"))
        
        localChecksum = 0
        for a in range(0, packetSize):
            localChecksum += imageData[a]

        if localChecksum == TCP_Checksum :
            client_socket.sendall("ACK".encode())
        else :
            client_socket.sendall("NCK".encode())
        
        
        print("Sent Packet Number : " + str(TCP_PacketNumber))
        print("Checksum of Packet: " + str(TCP_Checksum))
        print("\n")
        file.write(imageData)
        
    print("END OF RECEIVE \n")   
    file.close()

def send(client_socket, dir_path, imageName):
    
    full_path = os.path.join(dir_path, imageName)
    folder_name = os.path.basename(dir_path)
    
    file = open(full_path, 'rb')
    imageSize = os.path.getsize(full_path)
    

    
    messageFolderName ='{:#>15}'.format(folder_name)
    client_socket.send(messageFolderName.encode('latin-1'))
    print( "FolderName :" + folder_name)
    
    messageImageName ='{:#>31}'.format(imageName)
    client_socket.send(messageImageName.encode('latin-1'))
    print( "ImageName :" + imageName)

    
    messageImageSize ='{:#>15}'.format(imageSize)
    client_socket.send((str(messageImageSize)).encode('latin-1'))

    
    imageData = file.read()

    totalPacketSize = 9 + 10240 + 9
    TCP_PacketNumber = 1
    packetSize = 10240
    localChecksum = 0
    TCP_Checksum = 0

    TCP_BytesReceived = 0
    TCP_TotalBytesReceived = 0
    TCP_TotalPacketNumber = imageSize // packetSize + (1 if imageSize % packetSize > 0 else 0)
    
    
    print("Image Size : " + str(imageSize))
    print("Expected Packet Number : " + str(TCP_TotalPacketNumber))
    print("\n")

    for i in range(0, len(imageData) , packetSize):
        
        str_TCP_PacketNumber = '{:0>6}'.format(str(TCP_PacketNumber))
        client_socket.send(str_TCP_PacketNumber.encode('utf-8'))
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
        TCP_Checksum = TCP_Checksum % 256
        str_TCP_Checksum = '{:0>5}'.format(str(TCP_Checksum))
        client_socket.send(str_TCP_Checksum.encode('utf-8'))
    
        print( str(TCP_Checksum))
        
        ACK_NCK = client_socket.recv(4).decode('latin-1')
        print(ACK_NCK + "\n")
        
        

    print("END OF SEND")   
    file.close()
    
    
def on_modified(client_socket, event):
    # call your function here
    file_path = event.src_path
    file_name = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    print(event)
    time.sleep(5)
    send(client_socket, folder_path, file_name)



# Creates a thread with connected device
def multi_threaded_client(PORT, server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[{PORT} - Client] connected")        

        start_new_thread(new_client, (client_socket,PORT, ))
        
def new_client(client_socket, PORT):
    
    Command = client_socket.recv(10).decode('latin-1')
    Command = Command.lstrip("0")
    print(f"[{PORT} - Client] {Command}")

    while True:

        if not Command:
            break
        
        if Command[:4] == 'WDog':
            
            client_global = client_socket
            
            event_handler1 = LoggingEventHandler()
            event_handler2 = LoggingEventHandler()
        
            on_modified_with_arg = partial(on_modified, client_socket)
        
            event_handler1.on_created = on_modified_with_arg
            event_handler2.on_created = on_modified_with_arg
        
            observer1 = Observer()
            observer2 = Observer()
        
            observer1.schedule(event_handler1, folderPathCV, recursive=True)
            observer2.schedule(event_handler2, folderPathMap, recursive=True)
        
            observer1.start()
            observer2.start()
        
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer1.stop()
                observer2.stop()

            observer1.join()
            observer2.join()
        
        
        if Command[:4] == 'Subs':
              
            filesCV = os.listdir(folderPathCV)
            for imageCV in filesCV:
                send(client_socket, folderPathCV, imageCV)
                
            
            filesMap = os.listdir(folderPathMap)
            for imageMap in filesMap:
                send(client_socket, folderPathMap, imageMap)
            
            Command = 'WDog'
            
            
        if Command[:4] == 'Recv':

            fileFolderName = client_socket.recv(15).decode('latin-1')
            fileFolderName = fileFolderName.lstrip("0")
            
            fileName = client_socket.recv(50).decode('latin-1')
            fileName = fileName.lstrip("0")
            
            print(f"[Recv ImageName] {fileFolderName} to {fileName} \n")
            
            full_path = os.path.join(fileFolderName, fileName)
            full_path = os.path.join(absolute_path, full_path)

            recv(full_path, client_socket)
            
            
            
        
#---------------------------------------------------

if __name__ == "__main__":
    PORT1 = 8079
    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket1.bind((HOST, PORT1))
    print ("socket binded to %s" %(PORT1))
    server_socket1.listen() # how many ports to listen
    print(f"Server is listening on {HOST}:{PORT1}...")
    start_new_thread(multi_threaded_client, (PORT1, server_socket1, ))

    PORT2 = 8078
    server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket2.bind((HOST, PORT2))
    print ("socket binded to %s" %(PORT2))
    server_socket2.listen() # how many ports to listen
    print(f"Server is listening on {HOST}:{PORT2}...")
    start_new_thread(multi_threaded_client, (PORT2, server_socket2, ))
    
    while True:
        time.sleep(1)
        

