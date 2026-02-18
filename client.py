import socket
import threading
import sys

# Get IP from command line or user input
if len(sys.argv) > 1:
    SERVER_IP = sys.argv[1]
else:
    SERVER_IP = input("Enter Server IP: ")

PORT = 5555
nickname = input("Choose a nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii'))

# Start threads for simultaneous sending and receiving
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
