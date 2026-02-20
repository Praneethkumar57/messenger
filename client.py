"""import socket
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext
from cryptography.fernet import Fernet

# --- ENCRYPTION SETUP ---
# Key must be identical for all participants.
KEY = b'6u0_vT7-0X_Z6v8W-G_pX_X7Pz6J5v8B3u0_vT7-0X_=' 
cipher = Fernet(KEY)

if len(sys.argv) > 1:
    SERVER_IP = sys.argv[1] #
else:
    SERVER_IP = input("Enter Server IP: ") #

PORT = 5555 #
nickname = input("Choose a nickname: ") #

# --- NETWORK CONNECTION ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #
try:
    client.connect((SERVER_IP, PORT)) #
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit()

# --- GUI INTERFACE ---
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Messenger - {nickname}")

        # Chat Window
        self.display = scrolledtext.ScrolledText(root, state='disabled')
        self.display.pack(padx=10, pady=10)

        # Message Entry
        self.entry = tk.Entry(root)
        self.entry.pack(padx=10, pady=10, fill="x")
        self.entry.bind("<Return>", self.send)

        # Start the receive thread
        threading.Thread(target=self.receive, daemon=True).start()

    def update_chat(self, message):
        
        self.display.config(state='normal')
        self.display.insert(tk.END, message + "\n")
        self.display.yview(tk.END)
        self.display.config(state='disabled')

    def receive(self):
        
        while True:
            try:
                # Receive encrypted bytes
                encrypted_msg = client.recv(1024)
                if not encrypted_msg: break
                
                # Decrypt and display
                message = cipher.decrypt(encrypted_msg).decode('ascii')
                self.update_chat(message)
            except:
                print("An error occurred!") #
                client.close() #
                break

    def send(self, event=None):
        
        msg = self.entry.get()
        if msg:
            full_message = f'{nickname}: {msg}' #
            
            # 1. Update our own GUI locally so we see the message immediately
            self.update_chat(full_message)
            
            # 2. Encrypt and send to others
            encrypted_message = cipher.encrypt(full_message.encode('ascii'))
            client.send(encrypted_message)
            
            self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop() """
    
import socket
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext
from cryptography.fernet import Fernet

KEY = b'6u0_vT7-0X_Z6v8W-G_pX_X7Pz6J5v8B3u0_vT7-0X_=' 
cipher = Fernet(KEY)

if len(sys.argv) > 1:
    SERVER_IP = sys.argv[1] #
else:
    SERVER_IP = input("Enter Server IP: ") #

PORT = 5555 #
nickname = input("Choose a nickname: ") #

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #
try:
    client.connect((SERVER_IP, PORT)) #
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit()

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Connecting to {SERVER_IP}...") # Default title

        self.display = scrolledtext.ScrolledText(root, state='disabled')
        self.display.pack(padx=10, pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(padx=10, pady=10, fill="x")
        self.entry.bind("<Return>", self.send)

        threading.Thread(target=self.receive, daemon=True).start() #

    def update_chat(self, message):
        self.display.config(state='normal')
        self.display.insert(tk.END, message + "\n")
        self.display.yview(tk.END)
        self.display.config(state='disabled')

    def receive(self):
        while True:
            try:
                encrypted_msg = client.recv(1024) #
                if not encrypted_msg: break
                
                message = cipher.decrypt(encrypted_msg).decode('ascii')
                
                # Check if this is the special Room Title message
                if message.startswith("TITLE:"):
                    room_name = message.replace("TITLE:", "")
                    self.root.title(f"Room: {room_name} | User: {nickname}")
                else:
                    self.update_chat(message)
            except:
                print("An error occurred!") #
                client.close() #
                break

    def send(self, event=None):
        msg = self.entry.get()
        if msg:
            full_message = f'{nickname}: {msg}' #
            self.update_chat(full_message)
            encrypted_message = cipher.encrypt(full_message.encode('ascii'))
            client.send(encrypted_message)
            self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
