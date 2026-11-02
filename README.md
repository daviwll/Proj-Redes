> **Aviso:** trabalho acadêmico da disciplina de Redes de Computadores (UFAL), feito para estudo de técnicas de Red Team. Use apenas em laboratório controlado, em máquinas próprias ou com autorização explícita.

# Proj-Redes


Remote Shell Connection System

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
└── README.md            # Este arquivo

🔧 Configuração Inicial

🚀 Como Usar

Antes de Tudo coloque o ip do atacante no host(vamos fazer de forma local mesmo)


Servidor

Inicie o servidor:

    python3 server.py

Cliente

Execute o cliente em outra máquina:

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
