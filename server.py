"""import socket
import threading
import sys

# Server setup
if len(sys.argv) > 1:
    IP_ADDRESS = sys.argv[1]
else:
    IP_ADDRESS = input("Enter the IP address to host: ")

PORT = 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP_ADDRESS, PORT))
server.listen()

# client_data format -> {"192.168.1.10:54321": <socket_object>}
client_data = {}

def broadcast(message, sender_socket=None):
    
    for addr_str, sock in list(client_data.items()):
        if sock != sender_socket:
            try:
                sock.send(message)
            except:
                remove_client(addr_str)

def remove_client(addr_str):
    
    if addr_str in client_data:
        sock = client_data[addr_str]
        try:
            sock.send("KICKED: You have been removed by the admin.".encode('ascii'))
            sock.close()
        except:
            pass
        del client_data[addr_str]
        print(f"\n[DISCONNECTED] Removed {addr_str}")

def handle_client(sock, addr_str):
    
    while True:
        try:
            message = sock.recv(1024)
            if not message: break
            broadcast(message, sock)
        except:
            break
    remove_client(addr_str)

def admin_console():
    
    print("--- Admin Console Active ---")
    print("Commands: 'list' (show users), 'kick <ip:port>' (remove user)")
    while True:
        cmd = input("Admin> ")
        if cmd == "list":
            print(f"Connected Clients ({len(client_data)}):")
            for addr in client_data.keys():
                print(f" - {addr}")
        
        elif cmd.startswith("kick "):
            target = cmd.split(" ")[1]
            if target in client_data:
                remove_client(target)
                print(f"Kicked {target}")
            else:
                print(f"Error: {target} not found. Use 'list' to see active addresses.")

# Start Admin Console thread
threading.Thread(target=admin_console, daemon=True).start()

print(f"Server listening on {IP_ADDRESS}:{PORT}...")

while True:
    client_sock, address = server.accept()
    addr_str = f"{address[0]}:{address[1]}"
    print(f"\n[NEW CONNECTION] {addr_str}")
    
    client_data[addr_str] = client_sock
    
    thread = threading.Thread(target=handle_client, args=(client_sock, addr_str))
    thread.start() """
    
    
import socket
import threading
import sys
import time  # Required for the beacon sleep
from cryptography.fernet import Fernet

# --- ENCRYPTION SETUP ---
KEY = b'6u0_vT7-0X_Z6v8W-G_pX_X7Pz6J5v8B3u0_vT7-0X_=' 
cipher = Fernet(KEY)

# Server setup
if len(sys.argv) > 1:
    IP_ADDRESS = sys.argv[1] 
else:
    IP_ADDRESS = input("Enter the IP address to host: ") 

ROOM_TITLE = input("Enter the Room Title/Topic: ")

PORT = 5555 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((IP_ADDRESS, PORT)) 
server.listen() 

client_data = {} 

# --- NEW FUNCTIONS ---

def discovery_beacon():
    """Broadcasts the server's presence on the network via UDP."""
    beacon_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    beacon_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    discovery_msg = f"ROOM_DISCOVERY:{ROOM_TITLE}:{IP_ADDRESS}".encode('utf-8')
    
    while True:
        try:
            # Broadcast on port 5556 for discovery.py to find
            beacon_sock.sendto(discovery_msg, ('<broadcast>', 5556))
        except Exception as e:
            print(f"Beacon error: {e}")
        time.sleep(3) 

def admin_console():
    """A separate thread for the server owner to type commands."""
    print("--- Admin Console Active ---")
    print("Commands: 'list' (show users), 'kick <ip:port>' (remove user)")
    while True:
        cmd = input("Admin> ")
        if cmd == "list":
            print(f"Connected Clients ({len(client_data)}):")
            for addr in client_data.keys():
                print(f" - {addr}")
        elif cmd.startswith("kick "):
            try:
                target = cmd.split(" ")[1]
                remove_client(target)
            except IndexError:
                print("Usage: kick <ip:port>")

# --- EXISTING LOGIC ---

def broadcast(message, sender_socket=None):
    """Sends a message to all connected clients."""
    for addr_str, sock in list(client_data.items()): 
        if sock != sender_socket: 
            try:
                sock.send(message) 
            except:
                remove_client(addr_str) 

def remove_client(addr_str):
    """Safely closes and removes a client."""
    if addr_str in client_data: 
        sock = client_data[addr_str] 
        try:
            kick_msg = cipher.encrypt("KICKED: Removed by admin.".encode('ascii'))
            sock.send(kick_msg)
            sock.close() 
        except:
            pass
        del client_data[addr_str] 
        print(f"\n[DISCONNECTED] Removed {addr_str}") 

def handle_client(sock, addr_str):
    """Listens for messages from a specific client."""
    while True:
        try:
            message = sock.recv(1024) 
            if not message: break 
            broadcast(message, sock) 
        except:
            break
    remove_client(addr_str) 

# --- STARTING THE SERVER ---

# 1. Start Beacon (UDP)
threading.Thread(target=discovery_beacon, daemon=True).start()

# 2. Start Admin Console
threading.Thread(target=admin_console, daemon=True).start()

print(f"Server listening on {IP_ADDRESS}:{PORT}...")

# 3. Main Connection Loop
while True:
    client_sock, address = server.accept() 
    addr_str = f"{address[0]}:{address[1]}" 
    print(f"\n[NEW CONNECTION] {addr_str}") 
    
    # Send Title immediately
    title_packet = cipher.encrypt(f"TITLE:{ROOM_TITLE}".encode('ascii'))
    client_sock.send(title_packet)
    
    client_data[addr_str] = client_sock 
    threading.Thread(target=handle_client, args=(client_sock, addr_str)).start()
    
    

