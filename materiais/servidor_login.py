#!/usr/bin/env python3
"""
Servidor de login INSEGURO (HTTP puro) para demonstração no Wireshark.
Uso:  python3 servidor_login.py      -> abra http://localhost:8080
Nada é armazenado; o objetivo é mostrar que a senha trafega em texto claro.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

PAGINA = """<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<title>Banco Inseguro S/A</title>
<style>body{font-family:sans-serif;background:#f4f4f4;display:flex;justify-content:center;margin-top:80px}
form{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px #0003;width:280px}
input{width:100%;padding:8px;margin:6px 0 14px;box-sizing:border-box}
button{width:100%;padding:10px;background:#c0392b;color:#fff;border:0;border-radius:4px}</style>
</head><body><form method="POST" action="/login">
<h2>Banco Inseguro S/A</h2>
<label>Usuário</label><input name="usuario">
<label>Senha</label><input name="senha" type="password">
<button>Entrar</button>
<p style="font-size:12px;color:#888">Conexão: HTTP (sem criptografia)</p>
</form></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _html(self, corpo):
        dados = corpo.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        self._html(PAGINA)

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        campos = parse_qs(self.rfile.read(tamanho).decode("utf-8"))
        usuario = campos.get("usuario", [""])[0]
        self._html(f"<h2 style='font-family:sans-serif'>Bem-vindo, {usuario}!</h2>"
                   "<p style='font-family:sans-serif'>Agora vá ao Wireshark e procure sua senha ;)</p>")


if __name__ == "__main__":
    print("Servidor em http://localhost:8080  (Ctrl+C para sair)")
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
