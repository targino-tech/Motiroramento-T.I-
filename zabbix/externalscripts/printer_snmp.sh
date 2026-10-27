#!/bin/sh
# External script wrapper for HP Printer SNMP Metrics
# Usage: printer_snmp.sh <IP> <METRIC>
# Metrics: pages, toner_pct, adf_pct, cleaning_pct, status

IP="$1"
METRIC="$2"
COMMUNITY="public"

if [ -z "$IP" ] || [ -z "$METRIC" ]; then
    echo "0"
    exit 0
fi

case "$METRIC" in
    pages)
        # OID: 1.3.6.1.2.1.43.10.2.1.4.1.1
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.43.10.2.1.4.1.1 2>/dev/null | awk '{print $NF}')
        echo "${val:-0}"
        ;;
    toner_pct)
        # OID: 1.3.6.1.2.1.43.11.1.1.9.1.1
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.43.11.1.1.9.1.1 2>/dev/null | awk '{print $NF}')
        echo "${val:-0}"
        ;;
    adf_pct)
        # OID: 1.3.6.1.2.1.43.11.1.1.9.1.2
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.43.11.1.1.9.1.2 2>/dev/null | awk '{print $NF}')
        echo "${val:-0}"
        ;;
    cleaning_pct)
        # OID: 1.3.6.1.2.1.43.11.1.1.9.1.3
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.43.11.1.1.9.1.3 2>/dev/null | awk '{print $NF}')
        echo "${val:-0}"
        ;;
    status)
        # OID: 1.3.6.1.2.1.43.16.5.1.2.1.1
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.43.16.5.1.2.1.1 2>/dev/null | sed -e 's/.*STRING: //g' -e 's/"//g')
        echo "${val:-Pronta}"
        ;;
    uptime)
        # OID: 1.3.6.1.2.1.1.3.0
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.1.3.0 2>/dev/null | awk -F '[()]' '{print $2}')
        if [ -n "$val" ]; then
            # Convert timeticks (hundredths of a second) to seconds
            echo $((val / 100))
        else
            echo "0"
        fi
        ;;
    serial)
        # OID: 1.3.6.1.2.1.43.5.1.1.17.1
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.43.5.1.1.17.1 2>/dev/null | sed -e 's/.*STRING: //g' -e 's/"//g')
        echo "${val:-BRBSQ2Q11P}"
        ;;
    model)
        # OID: 1.3.6.1.2.1.25.3.2.1.3.1
        val=$(snmpget -v2c -c "$COMMUNITY" -t 2 -r 1 "$IP" 1.3.6.1.2.1.25.3.2.1.3.1 2>/dev/null | sed -e 's/.*STRING: //g' -e 's/"//g')
        echo "${val:-HP LaserJet Flow MFP E52645}"
        ;;
    *)
        echo "0"
        ;;
esac
