import time
import socket
import os

#HOST = "127.0.0.1"  # The server's hostname or IP address
HOST = "20.203.172.10"  # The server's hostname or IP address
PORT = 8079  # The port used by the server

absolute_path = os.path.dirname(os.path.abspath(__file__))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

	client_socket.connect((HOST, PORT))
	folder_path = os.path.join(absolute_path, "picture_tcp")
	file_list = [f for f in os.listdir(folder_path)]

	for i, file_name in enumerate(file_list):
		print(f"{i+1}. {file_name}")


	while True:

		file_num = int(input("Enter a string: "))
  
		print(file_list[file_num-1])
	

		if 1 <= file_num <= len(file_list):
			file_path = os.path.join(folder_path, file_list[file_num-1])
			print(f"You have selected '{file_path}' \n")

			file_name = file_list[file_num-1]
			file_path = os.path.join(folder_path, file_name)
   
			file = open(file_path, 'rb')
			imageSize = os.path.getsize(file_path)

			message = "Rec" + file_name
			print(message)
			client_socket.send(message.encode('latin-1'))
   
			str_imageSize = '{:0>15}'.format(str(imageSize))
			client_socket.send(str_imageSize.encode())
			print(imageSize)
   
			totalPacketSize = 9 + 10240 + 9
			TCP_PacketNumber = 1
			packetSize = 1024
			localChecksum = 0
			TCP_Checksum = 0

			TCP_BytesReceived = 0
			TCP_TotalBytesReceived = 0
			TCP_TotalPacketNumber = imageSize // packetSize + (1 if imageSize % packetSize > 0 else 0)

			imageData = file.read()

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
				
			file.close()
		
		if (file_num == "close") or (file_num == "exit"):
			print("closing")
			client_socket.close()


