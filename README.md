# 🛡️ Roteiro Prático — Cyber Security em Laboratório

**Ambiente:** Ubuntu (Cinnamon) — 1 computador por aluno
**Dinâmica:** individual, com algumas etapas em **dupla com o vizinho**
**Entrega:** prints/respostas das ❓ e o *Relatório de Incidente* (Lab 5)

> [!CAUTION]
> **Ética e lei.** Tudo o que faremos aqui só é permitido **dentro do laboratório, em máquinas da aula e com consentimento**.
> Varrer, capturar tráfego ou tentar acessar sistemas de terceiros sem autorização é crime no Brasil
> (Lei 12.737/2012 — "Lei Carolina Dieckmann", art. 154-A do Código Penal). Aprendemos o ataque para saber **defender**.

---

## Lab 0 — Preparação (5 min)

Abra o **Terminal** (`Ctrl+Alt+T`) e rode:

```bash
mkdir -p ~/aula-cyber/publico && cd ~/aula-cyber
# Baixe os materiais da máquina do professor (o IP estará no quadro):
for f in gerar_logs.py servidor_login.py relatorio-incidente-modelo.md; do
  wget -q http://IP_DO_PROFESSOR:8000/$f && echo "OK $f"
done
hostname -I        # anote o SEU IP: ____________________
```

Anote também o IP do seu **vizinho** (dupla): ____________________

---

## Lab 1 — Tríade CID e Criptografia (40 min)

### 1.1 Integridade com *hash*

```bash
cd ~/aula-cyber
echo "Transferir R\$ 100,00 para a conta 1234" > ordem.txt
sha256sum ordem.txt
```
Agora altere **um único caractere** (ex.: `100` → `900`) e calcule de novo:
```bash
sed -i 's/100/900/' ordem.txt
sha256sum ordem.txt
```
❓ **1.** O hash mudou pouco ou totalmente? Qual pilar da tríade CID o hash protege?
❓ **2.** Por que sites de download (ex.: ubuntu.com) publicam o SHA256 dos arquivos ISO?

### 1.2 Criptografia **simétrica** (mesma chave para cifrar e decifrar)

```bash
echo "Senha do Wi-Fi da diretoria: Fecaf@2026" > segredo.txt
openssl enc -aes-256-cbc -pbkdf2 -salt -in segredo.txt -out segredo.enc
# digite uma senha (chave) e confirme
cat segredo.enc            # ilegível?
file segredo.enc
openssl enc -d -aes-256-cbc -pbkdf2 -in segredo.enc        # decifrar
```
Tente decifrar com a senha **errada** e observe.

❓ **3.** Se eu quiser mandar `segredo.enc` para alguém do outro lado do mundo, **como entrego a senha com segurança?** (Esse é o *problema da distribuição de chaves*.)

### 1.3 Criptografia **assimétrica** com GPG (em dupla 👥)

**a) Cada um cria seu par de chaves** (pública + privada):
```bash
gpg --quick-generate-key "SEU NOME <seunome@aluno.fecaf>" default default 1d
gpg --list-keys
```
> Use uma *passphrase* que você lembre. A chave expira em 1 dia (é só para a aula).

**b) Publique sua chave PÚBLICA** e abra um "servidor" para o vizinho baixar:
```bash
gpg --armor --export seunome@aluno.fecaf > ~/aula-cyber/publico/minha-chave.asc
cd ~/aula-cyber/publico && python3 -m http.server 8000
```
> Deixe esse terminal aberto. **Abra uma nova aba** (`Ctrl+Shift+T`) para continuar.

**c) Baixe e importe a chave pública do vizinho:**
```bash
cd ~/aula-cyber
wget http://IP_DO_VIZINHO:8000/minha-chave.asc -O chave-vizinho.asc
gpg --import chave-vizinho.asc
gpg --list-keys
```

**d) Cifre uma mensagem que SÓ o vizinho consegue abrir:**
```bash
echo "Oi! Esta mensagem é confidencial. Assinado: SEU NOME" > msg.txt
gpg --armor --encrypt --trust-model always -r EMAIL_DO_VIZINHO -o publico/para-vizinho.asc msg.txt
cat publico/para-vizinho.asc
```

**e) Baixe a mensagem que o vizinho cifrou para você e decifre:**
```bash
wget http://IP_DO_VIZINHO:8000/para-vizinho.asc -O recebida.asc
gpg --decrypt recebida.asc
```

**f) Assinatura digital (autenticidade + integridade):**
```bash
echo "Eu, SEU NOME, autorizo o pagamento de R\$ 50,00." > autorizacao.txt
gpg --clearsign -o publico/autorizacao.txt.asc autorizacao.txt
```
O vizinho baixa e verifica:
```bash
wget http://IP_DO_VIZINHO:8000/autorizacao.txt.asc -O aut-vizinho.asc
gpg --verify aut-vizinho.asc            # "Good signature"?
sed -i 's/50,00/5000,00/' aut-vizinho.asc
gpg --verify aut-vizinho.asc            # e agora?
```

❓ **4.** Para cifrar a mensagem para o vizinho você usou a chave **pública** ou **privada** dele? E para assinar, usou a sua pública ou privada?
❓ **5.** Explique com suas palavras como a criptografia assimétrica resolve o problema da pergunta 3.
❓ **6.** O HTTPS usa os dois tipos de criptografia. Para que serve cada um?

> Pare o servidor da etapa (b) com `Ctrl+C`.

---

## Lab 2 — Wireshark: HTTP × HTTPS (30 min)

### 2.1 Capturando uma senha em texto claro

1. Em um terminal: `cd ~/aula-cyber && python3 servidor_login.py`
2. Abra o **Wireshark** (menu → Internet → Wireshark).
3. Dê duplo-clique na interface **Loopback: lo** para iniciar a captura.
4. No Firefox acesse **http://localhost:8080**, digite um usuário e uma senha **falsa** e clique em *Entrar*.
5. No Wireshark, pare a captura (■ vermelho) e aplique o filtro:
   ```
   http.request.method == "POST"
   ```
6. Clique no pacote → expanda **HTML Form URL Encoded**. Depois: botão direito → *Follow → TCP Stream*.

❓ **7.** Você encontrou a senha? Qual pilar da tríade CID foi violado?

**👥 Variação em dupla:** o vizinho acessa `http://SEU_IP:8080` e faz login. Você captura na sua interface de rede principal (ex.: `enp3s0`, **não** a `lo`) com o mesmo filtro.

### 2.2 E com HTTPS?

1. Inicie nova captura na interface de rede principal.
2. No Firefox acesse **https://www.gov.br** e navegue um pouco. Pare a captura.
3. Teste os filtros, um por vez:
   ```
   dns
   tls.handshake.type == 1
   tls.handshake.extensions_server_name
   tls
   ```
4. Em um pacote *Client Hello*, expanda *TLS → Handshake → Extension: server_name*.

❓ **8.** Com HTTPS dá para ler o conteúdo das páginas? O que **ainda** dá para descobrir sobre a navegação (DNS, SNI, IPs)?
❓ **9.** Em uma rede Wi-Fi pública, que riscos isso traz? Como uma **VPN** muda esse cenário?

---

## ☕ Intervalo (15 min)

---

## Lab 3 — Reconhecimento, Firewall e Detecção (30 min) 👥

### 3.1 Suba "serviços" na sua máquina
Terminal A: `cd ~/aula-cyber && python3 servidor_login.py` (porta 8080)
Terminal B: `cd ~/aula-cyber/publico && python3 -m http.server 8000` (porta 8000)

### 3.2 Seja **detectado**: abra o Wireshark capturando na interface principal com o filtro:
```
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

### 3.3 Varra a máquina do vizinho (com consentimento!)
```bash
nmap IP_DO_VIZINHO
nmap -sV -p 1-10000 IP_DO_VIZINHO
```
Enquanto isso, observe no **seu** Wireshark a varredura que o vizinho está fazendo em você.

❓ **10.** Quais portas/serviços o nmap encontrou? Qual o padrão de pacotes que aparece no Wireshark durante uma varredura? Como um **IDS** poderia usar esse padrão para gerar um alerta?

### 3.4 Ative o firewall (requer `sudo` — se não tiver, acompanhe no projetor)
Política: **negar tudo que entra** e liberar apenas o necessário (a porta 8080).
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 8080/tcp
sudo ufw logging on
sudo ufw enable
sudo ufw status verbose
```
Peça ao vizinho para varrer você de novo (`nmap -sV -p 1-10000 SEU_IP`).
Veja os bloqueios registrados:
```bash
sudo grep "UFW BLOCK" /var/log/ufw.log | tail -n 5     # ou: sudo dmesg | grep UFW | tail
```

❓ **11.** O que mudou no resultado do nmap (estado `filtered`)? Que princípio de segurança é a política *default deny*?
❓ **12.** Qual a diferença entre **firewall**, **IDS** e **IPS**?

> Ao final: `sudo ufw disable` e pare os servidores (`Ctrl+C`).

---

## Lab 4 — Hardening e Gerenciamento de Vulnerabilidades (20 min)

Preencha a tabela executando os comandos na **sua** máquina:

| # | Verificação | Comando | Resultado / Observação |
|---|---|---|---|
| 1 | Portas abertas e serviços escutando | `ss -tulpn` | |
| 2 | Serviços em execução | `systemctl list-units --type=service --state=running \| wc -l` | |
| 3 | Patches pendentes | `apt list --upgradable 2>/dev/null \| wc -l` | |
| 4 | Versão do sistema/kernel | `cat /etc/os-release; uname -r` | |
| 5 | Permissões de arquivos críticos | `ls -l /etc/passwd /etc/shadow` e `cat /etc/shadow` | |
| 6 | Usuários com shell de login | `grep -vE "nologin\|false" /etc/passwd` | |
| 7 | Binários com SUID | `find / -perm -4000 -type f 2>/dev/null` | |
| 8 | Últimos logins | `last -n 10` | |
| 9 | Firewall | `sudo ufw status` | |

**Auditoria automatizada com Lynis:**
```bash
sudo lynis audit system --quick      # sem sudo: lynis audit system --quick
```
Role até o fim e anote o **Hardening index**: ______ e **3 sugestões** (*Suggestions*):
1. ______________________ 2. ______________________ 3. ______________________

❓ **13.** Por que `/etc/shadow` não pode ser lido por usuários comuns? O que um atacante faria com ele?
❓ **14.** O Lynis audita a máquina **por dentro**. O **OpenVAS** varre **pela rede**. Por que uma empresa usaria os dois? Qual a relação com *gerenciamento de patches*?

---

## Lab 5 — Resposta a Incidente: Análise de Logs (40 min) 👥

**Cenário:** você é analista do SOC da *LojaFecaf*. Na manhã de 11/11, o time de infraestrutura notou que o
log do Apache do servidor `srv-web01` sumiu. Você recebeu o `auth.log` do servidor. **Descubra o que aconteceu.**

```bash
cd ~/aula-cyber
python3 gerar_logs.py
wc -l auth.log
less auth.log           # navegue (q para sair)
```

### Investigação guiada

**Passo 1 — Quantas falhas de login existem?**
```bash
grep "Failed password" auth.log | wc -l
```

**Passo 2 — De onde vêm as falhas? (top IPs)**
```bash
grep "Failed password" auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn
```

**Passo 3 — Que usuários o atacante tentou?**
```bash
grep "Invalid user" auth.log | awk '{print $8}' | sort | uniq -c | sort -rn
grep "Failed password for suporte" auth.log | wc -l
```

**Passo 4 — Algum desses IPs conseguiu entrar?** 🚨
```bash
grep "Accepted" auth.log | awk '{print $(NF-3)}' | sort | uniq -c
grep "Accepted" auth.log | grep -v "10.0.0."
```

**Passo 5 — O que ele fez depois de entrar?**
```bash
grep "sudo" auth.log | grep -v -E "maria|deploy"
grep -E "useradd|usermod" auth.log
```

**Passo 6 — Ele voltou?**
```bash
grep "sysupdate" auth.log
```

**Passo 7 — Linha do tempo completa do atacante:**
```bash
grep -E "IP_DO_ATACANTE|suporte|sysupdate" auth.log | grep -v "Failed\|Invalid" 
```

**Passo 8 — Ritmo do ataque (tentativas por minuto):**
```bash
grep "Failed password" auth.log | awk '{print $1, $2, substr($3,1,5)}' | uniq -c
```

### 🔎 E no Splunk (SIEM)?
O que você fez com `grep/awk` é exatamente o que um SIEM faz — só que em tempo real, com milhões de eventos e de centenas de servidores:

| Pergunta | Linux (`grep/awk`) | Splunk (SPL) |
|---|---|---|
| Top IPs com falha | `grep "Failed password" \| awk ... \| uniq -c` | `sourcetype=linux_secure "Failed password" \| rex "from (?<src_ip>\S+) port" \| stats count by src_ip \| sort -count` |
| Logins bem-sucedidos externos | `grep Accepted \| grep -v 10.0.0.` | `sourcetype=linux_secure "Accepted" NOT src_ip=10.0.0.0/8` |
| Falhas por minuto | `awk ... \| uniq -c` | `"Failed password" \| timechart span=1m count` |
| Alerta: força bruta seguida de sucesso | (manual) | *correlation search* agendada → alerta para o SOC |

### Entrega
Preencha o arquivo **`relatorio-incidente-modelo.md`** (abra com o editor de texto: `xed relatorio-incidente-modelo.md`).

❓ **15.** Qual controle de segurança, se existisse, teria **impedido** o ataque logo no início? E qual teria **detectado** mais cedo?
❓ **16.** O atacante apagou o `access.log`. Por que empresas enviam logs para um servidor central (SIEM) em vez de deixá-los só na máquina?

---

## ✅ Ticket de saída (responda em 1 linha cada)

1. Cite um exemplo de violação de **confidencialidade**, um de **integridade** e um de **disponibilidade** que você viu hoje.
2. Chave simétrica ou assimétrica: qual é mais rápida e qual resolve a troca de chaves?
3. Uma medida de hardening que você aplicaria **hoje** no seu computador pessoal.
4. Qual controle da **ISO 27001** ou exigência da **LGPD** se relaciona com o Lab 5?
