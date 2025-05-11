# server_update_ip.py
import requests
import time

GIST_ID = "a8c3564129a5db5ba5e5adcae70cea4b"  # Exemplo: "a1b2c3d4e5f6g7h8i9j0"
GITHUB_TOKEN = "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"
IP_CHECK_INTERVAL = 300  # Atualiza a cada 5 minutos

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return None

def update_gist(ip):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "files": {
            "ip.txt": {
                "content": ip
            }
        }
    }
    response = requests.patch(
        f"https://api.github.com/gists/{GIST_ID}",
        headers=headers,
        json=data
    )
    return response.status_code == 200

while True:
    current_ip = get_public_ip()
    if current_ip:
        print("IP atual:", current_ip)
        if update_gist(current_ip):
            print("Gist atualizado!")
        else:
            print("Erro ao atualizar Gist.")
    time.sleep(IP_CHECK_INTERVAL)