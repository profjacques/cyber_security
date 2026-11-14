#!/usr/bin/env bash
# =============================================================================
#  Preparação do laboratório - Aula Prática de Cyber Security
#  Rodar UMA VEZ em cada máquina (Ubuntu / Linux Mint Cinnamon) com sudo:
#      sudo bash preparar-laboratorio.sh
#  Pode ser executado pelo técnico do laboratório antes da aula.
# =============================================================================
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Execute com sudo:  sudo bash $0"; exit 1
fi

echo "[1/5] Atualizando índice de pacotes..."
apt-get update -y

echo "[2/5] Instalando ferramentas..."
# Responde automaticamente "Sim" para permitir captura por não-root no Wireshark
echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  wireshark tshark tcpdump nmap ufw gnupg openssl curl wget \
  net-tools lynis python3 whois

echo "[3/5] Liberando captura de pacotes para todos os usuários do laboratório..."
# Em laboratório (máquinas de uso didático) liberamos o dumpcap para todos,
# evitando ter que fazer logout/login após adicionar ao grupo 'wireshark'.
chmod 755 /usr/bin/dumpcap
setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
for d in /home/*; do
  u=$(basename "$d")
  id "$u" &>/dev/null && usermod -aG wireshark "$u" || true
done

echo "[4/5] Garantindo SSH desligado e firewall em estado conhecido (inativo)..."
ufw --force reset >/dev/null
ufw disable >/dev/null || true

echo "[5/5] Verificando versões..."
for c in wireshark nmap gpg openssl lynis python3; do
  printf "  %-10s " "$c"; command -v $c >/dev/null && echo OK || echo "FALTANDO"
done

echo
echo "Pronto! IP desta máquina: $(hostname -I | awk '{print $1}')"
echo "Se os alunos NÃO tiverem sudo, o Lab 3 (ufw) e o Lab 4 (lynis completo)"
echo "devem ser demonstrados pelo professor no projetor."
