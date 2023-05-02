import time
import socket
import os

HOST = "31.223.50.236"  # The server's hostname or IP address
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

			message = "Rec" + file_name
			print(message)
			client_socket.send(message.encode('latin-1'))

			file = open(file_path, 'rb')
			file_size = os.path.getsize(file_path)
			
			print(file_size)
			print(type(file_size))
			
			#client_socket.sendall((str(file_size)).encode())
			
			picture_data = file.read(1024)

			#client_socket.sendall(picture_data)
			END_OF_TRANSMISSION = b'END'

			while picture_data:
				client_socket.send(picture_data)
				picture_data = file.read(1024)
    
			client_socket.send(END_OF_TRANSMISSION)
			file.close()
		
		if (file_num == "close") or (file_num == "exit"):
			print("closing")
			client_socket.close()


