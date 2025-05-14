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
``
pip install cryptography pillow
``

Execute o servidor:


``
python server.py
``
Execute o cliente (em outro computador):


`
python client.py
`

## 📋 Comandos Suportados

| Comando         | Descrição                                   | Exemplo de Uso               |
|-----------------|--------------------------------------------|-----------------------------|
| `cd [diretório]`| Muda o diretório de trabalho no cliente    | `cd /home/user/Documents`   |
| `ls`            | Lista arquivos do diretório atual          | `ls`                        |
| `get [arquivo]` | Baixa um arquivo do cliente                | `get relatorio.pdf`         |
| `exec [comando]`| Executa comandos shell no cliente          | `exec ping google.com`      |
| `encrypt`       | Criptografa todos os arquivos do cliente   | `encrypt`                   |
| `decrypt`       | Descriptografa arquivos .encrypted         | `decrypt`                   |
| `backup`        | Cria backup dos arquivos do cliente        | `backup`                    |
| `exit`          | Encerra a conexão com o cliente            | `exit`                      |

📌 Melhorias Futuras

    Autenticação de clientes

    Canais criptografados

    Sistema de plugins para comandos

    Compactação de arquivos durante transferência

    Suporte a UDP para comandos rápidos
