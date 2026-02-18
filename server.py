import socket
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
    """Sends a message to all connected clients."""
    for addr_str, sock in list(client_data.items()):
        if sock != sender_socket:
            try:
                sock.send(message)
            except:
                remove_client(addr_str)

def remove_client(addr_str):
    """Safely closes and removes a client from the registry."""
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
    """Listens for messages from a specific client."""
    while True:
        try:
            message = sock.recv(1024)
            if not message: break
            broadcast(message, sock)
        except:
            break
    remove_client(addr_str)

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
    thread.start()
