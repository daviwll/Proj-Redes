# Proj-Redes


Remote Shell Connection System

------------SE QUISER TESTAR SEM O TOKEN DO GITHUB É SÓ COLOCAR O IP LOCAL DO SEU PC NA VARIÁVEL HOST E ABRIR O CLIENT.PY EM OUTRO PC ---------------------------------------------------------------------

# O QUE FALTA:
- Transformar o client.py em executável
- Implementar a parte de criptografar arquivos
- Fazer a parte visual do menu 

# DA PRA COLOCAR A MAIS
- Persistência
- ...


📌 Visão Geral

Este sistema permite estabelecer uma conexão remota entre um servidor e um cliente, utilizando um Gist do GitHub para compartilhar dinamicamente o endereço IP do servidor. O cliente pode executar comandos, transferir arquivos e navegar no sistema de arquivos remotamente.
🛠️ Pré-requisitos

    Python 3.6+

    Conta no GitHub

    Acesso à internet

    Bibliotecas Python: requests, socket, threading

📂 Estrutura de Arquivos

remote_shell/
├── server.py            # Script principal do servidor
├── client.py            # Script do cliente
├── server_update_ip.py  # Atualiza o IP no Gist
└── README.md            # Este arquivo

🔧 Configuração Inicial
1. Criar um Gist no GitHub

    Acesse https://gist.github.com

    Crie um novo Gist com um arquivo chamado ip.txt

    Anote o ID do Gist (parte final da URL)

2. Gerar Token de Acesso

    Vá em GitHub Settings > Developer Settings > Personal Access Tokens

    Crie um novo token com permissão gist

    Guarde este token com segurança

3. Configurar os Scripts

Edite os arquivos com suas credenciais:

    server_update_ip.py: Insira seu GIST_ID e GITHUB_TOKEN

    client.py: Verifique se a GIST_RAW_URL aponta para seu Gist

🚀 Como Usar
Servidor

    Execute o atualizador de IP:
    bash

python3 server_update_ip.py

Este script atualizará seu IP público no Gist a cada 5 minutos.

Em outro terminal, inicie o servidor:
bash

    python3 server.py

Cliente

Execute o cliente em outra máquina:
bash

python3 client.py

⌨️ Comandos Disponíveis
Comando	Descrição
cd [diretório]	Navega entre pastas
ls	Lista arquivos no diretório atual
get [arquivo]	Baixa um arquivo do cliente
exec [comando]	Executa um comando no shell
exit	Encerra a conexão
⚠️ Avisos Importantes

    Use apenas em ambientes controlados e com permissão

    Nunca exponha seu token GitHub publicamente

    Este sistema não possui criptografia - não use em redes públicas

🔄 Fluxo de Comunicação

    O server_update_ip.py mantém o IP atualizado no Gist

    O cliente obtém o IP do Gist

    Conexão é estabelecida diretamente entre servidor e cliente

    Comandos são executados remotamente
