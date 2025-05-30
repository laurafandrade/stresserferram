function start() {
    const alvo = document.getElementById("alvo").value;
    const threads = document.getElementById("threads").value;
    const tempo = document.getElementById("tempo").value;

    const formData = new FormData();
    formData.append("alvo", alvo);
    formData.append("threads", threads);
    formData.append("tempo", tempo);

    fetch("/start", { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            document.getElementById("status").innerHTML = data.mensagem;
            carregarLogs();
        });
}

function stop() {
    fetch("/stop", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            document.getElementById("status").innerHTML = data.mensagem;
            carregarLogs();
        });
}

function carregarLogs() {
    fetch("/logs")
        .then(res => res.json())
        .then(logs => {
            const logList = document.getElementById("log-list");
            logList.innerHTML = "";
            logs.forEach(log => {
                const item = document.createElement("li");
                item.textContent = `🧠 Alvo: ${log.alvo} | Threads: ${log.threads} | Tempo: ${log.tempo}s | Status: ${log.status}`;
                logList.appendChild(item);
            });
        });
}

setInterval(carregarLogs, 5000);
carregarLogs();
