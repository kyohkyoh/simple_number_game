import socket
import threading
import time

IP = "127.0.0.1"
PORT = 5050
ADDR = (IP,PORT)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)

print("Connected")
while True:
    time.sleep(1)
    server_msg = client_socket.recv(1024)
    if not server_msg:
        break
    server_msg = server_msg.decode("utf-8")
    print(server_msg)

    if server_msg[-3:] == '+++': 
        msg = input(">>")

        if msg == 'exit':
            break
        client_socket.send(msg.encode("utf-8"))

client_socket.close()

