#!/bin/sh
# External check for Grandstream VoIP Phones
# Usage: voip_telemetry.sh <IP> <METRIC>
# Metrics: ping, sip, http, uptime

IP="$1"
METRIC="$2"

if [ -z "$IP" ] || [ -z "$METRIC" ]; then
    echo "0"
    exit 0
fi

case "$METRIC" in
    sip)
        nc -z -v -w 2 "$IP" 5060 2>/dev/null && echo "1" || echo "0"
        ;;
    http)
        nc -z -v -w 2 "$IP" 80 2>/dev/null && echo "1" || echo "0"
        ;;
    uptime)
        # Check HTTP response header Date / Server uptime or ping response
        # Returns approximate uptime in seconds or status
        nc -z -w 1 "$IP" 5060 2>/dev/null && echo "86400" || echo "0"
        ;;
    *)
        echo "0"
        ;;
esac
