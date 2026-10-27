# Diretório de Scripts Externos do Zabbix (Externalscripts)

Scripts executados periodicamente pelo Zabbix Server como itens do tipo `External Check` (Checagem Externa).

## Scripts Ativos:
- `net_speedtest.sh`:
  - Medição contínua da taxa de Download, Upload, Latência RTT, Operadora (ISP) e IP Público da WAN.
  - Utiliza cache inteligente de 30 minutos em `/tmp/speedtest_cache.json` para não consumir largura de banda da rede.
  - Parâmetros aceitos: `download`, `upload`, `ping`, `isp`, `public_ip`.
