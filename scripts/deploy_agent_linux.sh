#!/bin/bash
# Script de Instalacao e Configuracao do Zabbix Agent 2 para Estacoes e Servidores Linux (Enterprise)
set -e

ZABBIX_SERVER="${1:-${ZABBIX_SERVER:-10.0.0.10}}"
HOSTNAME=$(hostname)

echo "=========================================================="
echo " Implantador Automatizado Zabbix Agent 2 - Linux "
echo "=========================================================="

if [ -f /etc/debian_version ]; then
    echo "[+] Sistema baseado em Debian/Ubuntu detectado."
    wget -q https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.0+ubuntu24.04_all.deb -O /tmp/zabbix-release.deb || \
    wget -q https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.0+ubuntu22.04_all.deb -O /tmp/zabbix-release.deb
    dpkg -i /tmp/zabbix-release.deb || true
    apt-get update -y
    apt-get install -y zabbix-agent2
elif [ -f /etc/redhat-release ]; then
    echo "[+] Sistema baseado em RHEL/CentOS/Rocky detectado."
    rpm -Uvh https://repo.zabbix.com/zabbix/7.0/rhel/9/x86_64/zabbix-release-latest-7.0.el9.noarch.rpm || true
    dnf install -y zabbix-agent2 || yum install -y zabbix-agent2
fi

CONF="/etc/zabbix/zabbix_agent2.conf"
if [ -f "$CONF" ]; then
    echo "[+] Configurando parâmetros corporativos em $CONF..."
    sed -i "s/^Server=.*/Server=$ZABBIX_SERVER/" "$CONF"
    sed -i "s/^ServerActive=.*/ServerActive=$ZABBIX_SERVER/" "$CONF"
    sed -i "s/^Hostname=.*/Hostname=$HOSTNAME/" "$CONF"
    grep -q "^HostMetadata=" "$CONF" && sed -i "s/^HostMetadata=.*/HostMetadata=Linux_Workstation_Corp/" "$CONF" || echo "HostMetadata=Linux_Workstation_Corp" >> "$CONF"
fi

systemctl daemon-reload
systemctl enable zabbix-agent2
systemctl restart zabbix-agent2

echo "[+] Zabbix Agent 2 ativo e comunicando com $ZABBIX_SERVER!"
