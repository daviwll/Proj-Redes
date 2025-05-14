# N.O.M.E. – Núcleo Operacional de Monitoramento e Exfiltração

Significado:
Núcleo Operacional → indica que é um centro de controle (como uma shell reversa que comanda a máquina).

Monitoramento → cobre a execução de comandos, acesso a dados.

Exfiltração → representa o download de arquivos e o comportamento de ransomware (roubo e criptografia de dados).

Um sistema cliente-servidor para gerenciamento remoto de computadores com interface gráfica, transferência de arquivos e funções de criptografia de dados.

## 🚀 Funcionalidades

### Cliente
- Conexão persistente com servidor
- Execução remota de comandos
- Transferência segura de arquivos
- Criptografia AES de arquivos locais
- Sistema de backup automático
- Interface visual discreta

### Servidor
- Interface gráfica de controle
- Gerenciamento de múltiplos clientes
- Envio de comandos personalizados
- Recebimento de arquivos
- Log de atividades

## ⚙️ Tecnologias Utilizadas

- Python 3.x
- Sockets TCP/IP
- Threading para concorrência
- Tkinter para interface gráfica
- Cryptography (AES via Fernet)
- PIL/Pillow para exibição de GIFs

## 🔧 Requisitos e Instalação

1. Instale as dependências:
```bash
pip install cryptography pillow

    Execute o servidor:

bash

python server.py

    Execute o cliente (em outro computador):

bash

python client.py

📋 Comandos Suportados
Comando	Descrição
cd [dir]	Muda diretório no cliente
ls	Lista arquivos no diretório atual
get [arquivo]	Baixa arquivo do cliente
exec [cmd]	Executa comando shell no cliente
encrypt	Criptografa todos os arquivos do cliente
decrypt	Descriptografa arquivos do cliente
backup	Cria backup dos arquivos do cliente
exit	Encerra conexão com o cliente
