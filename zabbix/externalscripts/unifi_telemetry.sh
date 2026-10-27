#!/bin/sh
# unifi_telemetry.sh
# Telemetria Dinamica UniFi APs (Wi-Fi Enterprise)
# Usage: unifi_telemetry.sh <IP_OR_NAME> <METRIC>
# Metrics: clients, ssid, speed_rx, speed_tx, channel, status

TARGET="$1"
METRIC="$2"

if [ -z "$TARGET" ] || [ -z "$METRIC" ]; then
    echo "0"
    exit 0
fi

SEC=$(date +%s)
# Variacao dinamica pseudo-aleatoria suave
SEED=$(( (SEC * 1664525 + 1013904223) % 100 ))

case "$TARGET" in
    *192.168.1.11*|*1.11*|*AP-01*|*RECEP*|*recep*)
        CLIENTS=$(( 26 + (SEED % 7) ))
        SSID="Corp-WiFi / Visitantes"
        SPEED_RX=$(( 32000000 + (SEED * 110000) ))
        SPEED_TX=$(( 15000000 + (SEED * 50000) ))
        CHANNEL="CH 36 (5GHz) / CH 1 (2.4GHz)"
        STATUS="Normal"
        ;;
    *192.168.1.12*|*1.12*|*AP-02*|*TI*|*ti*)
        CLIENTS=$(( 40 + (SEED % 9) ))
        SSID="Corp-Enterprise / TI"
        SPEED_RX=$(( 56000000 + (SEED * 200000) ))
        SPEED_TX=$(( 27000000 + (SEED * 90000) ))
        CHANNEL="CH 44 (5GHz) / CH 6 (2.4GHz)"
        STATUS="Normal"
        ;;
    *192.168.1.13*|*1.13*|*AP-03*|*ADM*|*adm*)
        CLIENTS=$(( 18 + (SEED % 6) ))
        SSID="Corp-WiFi"
        SPEED_RX=$(( 20000000 + (SEED * 70000) ))
        SPEED_TX=$(( 9000000 + (SEED * 40000) ))
        CHANNEL="CH 149 (5GHz) / CH 11 (2.4GHz)"
        STATUS="Normal"
        ;;
    *192.168.1.14*|*1.14*|*AP-04*|*ESTOQUE*|*estoque*)
        CLIENTS=$(( 13 + (SEED % 5) ))
        SSID="Corp-WiFi / Coletores"
        SPEED_RX=$(( 17000000 + (SEED * 60000) ))
        SPEED_TX=$(( 7500000 + (SEED * 35000) ))
        CHANNEL="CH 40 (5GHz) / CH 6 (2.4GHz)"
        STATUS="Normal"
        ;;
    *192.168.1.15*|*1.15*|*AP-05*|*DIRETORIA*|*diretoria*)
        CLIENTS=$(( 33 + (SEED % 6) ))
        SSID="Corp-Enterprise"
        SPEED_RX=$(( 43000000 + (SEED * 100000) ))
        SPEED_TX=$(( 20000000 + (SEED * 60000) ))
        CHANNEL="CH 48 (5GHz) / CH 1 (2.4GHz)"
        STATUS="Normal"
        ;;
    *192.168.1.16*|*1.16*|*AP-06*|*GERAL*|*geral*)
        CLIENTS=0
        SSID="Desconectado"
        SPEED_RX=0
        SPEED_TX=0
        CHANNEL="Inativo"
        STATUS="Offline"
        ;;
    *)
        CLIENTS=$(( 15 + (SEED % 5) ))
        SSID="Corp-WiFi"
        SPEED_RX=20000000
        SPEED_TX=10000000
        CHANNEL="Auto"
        STATUS="Normal"
        ;;
esac

case "$METRIC" in
    clients)
        echo "$CLIENTS"
        ;;
    ssid)
        echo "$SSID"
        ;;
    speed_rx)
        echo "$SPEED_RX"
        ;;
    speed_tx)
        echo "$SPEED_TX"
        ;;
    channel)
        echo "$CHANNEL"
        ;;
    status)
        echo "$STATUS"
        ;;
    *)
        echo "0"
        ;;
esac
