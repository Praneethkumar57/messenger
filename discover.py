"""import socket
import threading
import tkinter as tk
from tkinter import messagebox

class RoomBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("LAN Room Browser")
        self.rooms = {} # Format: {"Room Name": "IP Address"}

        self.label = tk.Label(root, text="Available Rooms (Scanning...)", font=('Arial', 12, 'bold'))
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack(padx=10, pady=10)

        self.join_btn = tk.Button(root, text="Join Selected Room", command=self.join_room)
        self.join_btn.pack(pady=5)

        # Start listener thread
        threading.Thread(target=self.listen_for_servers, daemon=True).start()

    def listen_for_servers(self):
        
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.bind(('', 5556)) # Listen on the beacon port
        
        while True:
            data, addr = listen_sock.recvfrom(1024)
            msg = data.decode('utf-8')
            
            if msg.startswith("ROOM_DISCOVERY:"):
                _, title, ip = msg.split(":")
                if title not in self.rooms:
                    self.rooms[title] = ip
                    self.listbox.insert(tk.END, f"{title} (at {ip})")

    def join_room(self):
        selection = self.listbox.curselection()
        if selection:
            room_info = self.listbox.get(selection[0])
            room_title = room_info.split(" (at ")[0]
            ip = self.rooms[room_title]
            
            messagebox.showinfo("Connect", f"To join, run:\npython3 client.py {ip}")
            # Optional: You could automate starting client.py here using subprocess
        else:
            messagebox.showwarning("Warning", "Please select a room first!")

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomBrowser(root)
    root.mainloop()"""
    
import socket
import threading
import tkinter as tk
from tkinter import messagebox
import time

class RoomBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("LAN Room Browser")
        
        # Format: {"IP_ADDRESS": {"title": "Room Name", "last_seen": timestamp}}
        self.rooms = {} 

        self.label = tk.Label(root, text="Available Rooms (Scanning...)", font=('Arial', 12, 'bold'))
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack(padx=10, pady=10)

        self.join_btn = tk.Button(root, text="Join Selected Room", command=self.join_room)
        self.join_btn.pack(pady=5)

        # Thread 1: Listen for new/active servers
        threading.Thread(target=self.listen_for_servers, daemon=True).start()
        
        # Thread 2: Remove dead servers from the UI
        threading.Thread(target=self.cleanup_rooms, daemon=True).start()

    def listen_for_servers(self):
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.bind(('', 5556))
        
        while True:
            try:
                data, addr = listen_sock.recvfrom(1024)
                msg = data.decode('utf-8')
                
                if msg.startswith("ROOM_DISCOVERY:"):
                    _, title, ip = msg.split(":")
                    
                    # Update or Add the room with current timestamp
                    self.rooms[ip] = {
                        "title": title,
                        "last_seen": time.time()
                    }
                    self.refresh_listbox()
            except:
                pass

    def cleanup_rooms(self):
        """Removes rooms that haven't broadcasted in the last 10 seconds."""
        while True:
            current_time = time.time()
            to_delete = []

            for ip, info in self.rooms.items():
                if current_time - info['last_seen'] > 10:
                    to_delete.append(ip)

            if to_delete:
                for ip in to_delete:
                    del self.rooms[ip]
                self.refresh_listbox()
            
            time.sleep(2) # Check for dead rooms every 2 seconds

    def refresh_listbox(self):
        """Syncs the UI listbox with the self.rooms dictionary."""
        self.listbox.delete(0, tk.END)
        for ip, info in self.rooms.items():
            self.listbox.insert(tk.END, f"{info['title']} (at {ip})")

    def join_room(self):
        selection = self.listbox.curselection()
        if selection:
            item_text = self.listbox.get(selection[0])
            # Extract IP from string "Title (at 192.168.x.x)"
            ip = item_text.split(" (at ")[1].replace(")", "")
            messagebox.showinfo("Connect", f"To join, run:\npython3 client.py {ip}")
        else:
            messagebox.showwarning("Warning", "Please select a room first!")

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomBrowser(root)
    root.mainloop()
