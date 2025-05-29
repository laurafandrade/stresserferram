function start() {
    let threads = document.getElementById('threads').value;
    fetch('/start', {
        method: 'POST',
        body: new URLSearchParams({'threads': threads})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('status').innerHTML = data.mensagem;
    });
}

function stop() {
    fetch('/stop', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        document.getElementById('status').innerHTML = data.mensagem;
    });
}