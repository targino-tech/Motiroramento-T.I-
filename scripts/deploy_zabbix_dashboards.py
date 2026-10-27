#!/usr/bin/env python3
"""
deploy_zabbix_dashboards.py
Cria os Dashboards e Seções nativas no Zabbix 8.0 para Enterprise NOC:
1. 🌾 NOC Master 360° & Mitigação IT (Dashboard completo multipáginas)
2. 📶 Cobertura Wi-Fi & APs UniFi
3. 🌐 Links WAN & Operadora Telecom
4. 🖥️ Servidores & Estações de Trabalho
5. 🖨️ Parque de Impressoras & Suprimentos
6. 📞 Ramais VoIP & Telefonia Grandstream
"""

import urllib.request
import json
import sys
import os

ZBX_URL = os.environ.get("ZABBIX_API_URL", "http://127.0.0.1/api_jsonrpc.php")

def zbx_call(method, params, auth=None):
    headers = {"Content-Type": "application/json-rpc"}
    if auth: headers["Authorization"] = f"Bearer {auth}"
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    req = urllib.request.Request(ZBX_URL, headers=headers, data=json.dumps(payload).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode())
        if "error" in res:
            raise Exception(f"Zabbix API Error [{method}]: {res['error']}")
        return res["result"]

def get_item_by_host_key(auth, host_name_pattern, key_pattern):
    hosts = zbx_call("host.get", {"search": {"name": host_name_pattern}, "output": ["hostid", "name"]}, auth)
    if not hosts: return None
    host_id = hosts[0]["hostid"]
    items = zbx_call("item.get", {"hostids": [host_id], "search": {"key_": key_pattern}, "output": ["itemid", "name", "key_"]}, auth)
    if items: return items[0]
    return None

def build_svg_graph(name, x, y, width, height, datasets, legend_cols=2):
    fields = []
    for idx, ds in enumerate(datasets):
        fields.extend([
            {"type": 0, "name": f"ds.{idx}.dataset_type", "value": "0"},
            {"type": 4, "name": f"ds.{idx}.itemids.0", "value": str(ds["itemid"])},
            {"type": 1, "name": f"ds.{idx}.color.0", "value": ds.get("color", "00E676")},
            {"type": 0, "name": f"ds.{idx}.width", "value": str(ds.get("width", 2))}
        ])
    fields.append({"type": 0, "name": "legend_columns", "value": str(legend_cols)})
    return {
        "type": "svggraph",
        "name": name,
        "x": x, "y": y, "width": width, "height": height,
        "view_mode": 0,
        "fields": fields
    }

def build_gauge(name, x, y, width, height, itemid, min_val="0", max_val="100", thresholds=None):
    if thresholds is None:
        thresholds = [
            {"color": "3BC97D", "threshold": "0"},
            {"color": "FCCB1D", "threshold": "70"},
            {"color": "E65660", "threshold": "85"}
        ]
    fields = [
        {"type": 4, "name": "itemid.0", "value": str(itemid)},
        {"type": 1, "name": "min", "value": str(min_val)},
        {"type": 1, "name": "max", "value": str(max_val)},
        {"type": 0, "name": "show.0", "value": "2"}, # Value
        {"type": 0, "name": "th_show_arc", "value": "1"},
        {"type": 0, "name": "th_show_labels", "value": "1"},
        {"type": 0, "name": "value_arc_size", "value": "30"}
    ]
    for idx, th in enumerate(thresholds):
        fields.append({"type": 1, "name": f"thresholds.{idx}.color", "value": th["color"]})
        fields.append({"type": 1, "name": f"thresholds.{idx}.threshold", "value": str(th["threshold"])})
    return {
        "type": "gauge",
        "name": name,
        "x": x, "y": y, "width": width, "height": height,
        "view_mode": 0,
        "fields": fields
    }

def build_item_card(name, x, y, width, height, itemid):
    return {
        "type": "item",
        "name": name,
        "x": x, "y": y, "width": width, "height": height,
        "view_mode": 0,
        "fields": [
            {"type": 4, "name": "itemid.0", "value": str(itemid)},
            {"type": 0, "name": "show.0", "value": "2"}
        ]
    }

def main():
    print("=== INICIANDO IMPLANTAÇÃO DOS DASHBOARDS NATIVOS NO ZABBIX ===")
    zbx_user = os.environ.get("ZABBIX_USER", "Admin")
    zbx_pass = os.environ.get("ZABBIX_PASS", "zabbix")
    auth = zbx_call("user.login", {"username": zbx_user, "password": zbx_pass})
    print("Autenticado no Zabbix com sucesso.")

    # Remove previous dashboards if updating
    existing_dashs = zbx_call("dashboard.get", {"search": {"name": "Enterprise NOC"}, "output": ["dashboardid", "name"]}, auth)
    if existing_dashs:
        ids = [d["dashboardid"] for d in existing_dashs]
        print(f"Limpando {len(ids)} dashboards anteriores...")
        zbx_call("dashboard.delete", ids, auth)

    # Coleta de Itens Essenciais
    print("Mapeando itens e telemetria...")
    
    # UniFi APs (Group 24)
    ap_hosts = zbx_call("host.get", {"groupids": ["24"], "output": ["hostid", "name"], "sortfield": "name"}, auth)
    ap_client_items = []
    ap_latency_items = []
    ap_loss_items = []
    ap_rx_items = []
    ap_tx_items = []

    ap_colors = ["00E676", "2979FF", "FFD600", "FF1744", "AA00FF", "00E5FF"]
    for idx, h in enumerate(ap_hosts):
        c = ap_colors[idx % len(ap_colors)]
        h_items = zbx_call("item.get", {"hostids": [h["hostid"]], "output": ["itemid", "key_", "name"]}, auth)
        h_map = {it["key_"]: it["itemid"] for it in h_items}
        
        # Friendly name
        clean_name = h["name"].replace("AP-UniFi-", "").split(" (")[0]
        
        if "unifi_telemetry.sh[{HOST.CONN},clients]" in h_map:
            ap_client_items.append({"itemid": h_map["unifi_telemetry.sh[{HOST.CONN},clients]"], "name": clean_name, "color": c})
        if "icmppingsec" in h_map:
            ap_latency_items.append({"itemid": h_map["icmppingsec"], "name": clean_name, "color": c})
        if "icmppingloss" in h_map:
            ap_loss_items.append({"itemid": h_map["icmppingloss"], "name": clean_name, "color": c})
        if "unifi_telemetry.sh[{HOST.CONN},speed_rx]" in h_map:
            ap_rx_items.append({"itemid": h_map["unifi_telemetry.sh[{HOST.CONN},speed_rx]"], "name": clean_name, "color": c})
        if "unifi_telemetry.sh[{HOST.CONN},speed_tx]" in h_map:
            ap_tx_items.append({"itemid": h_map["unifi_telemetry.sh[{HOST.CONN},speed_tx]"], "name": clean_name, "color": c})

    # WAN Link (Group 28)
    wan_hosts = zbx_call("host.get", {"groupids": ["28"], "output": ["hostid", "name"]}, auth)
    wan_items_map = {}
    if wan_hosts:
        w_items = zbx_call("item.get", {"hostids": [wan_hosts[0]["hostid"]], "output": ["itemid", "key_", "name"]}, auth)
        wan_items_map = {it["key_"]: it["itemid"] for it in w_items}

    # Impressoras HP (Group 26)
    printer_hosts = zbx_call("host.get", {"groupids": ["26"], "output": ["hostid", "name"], "sortfield": "name"}, auth)
    printer_toner_items = []
    printer_adf_items = []
    printer_page_items = []
    printer_rtt_items = []
    for idx, p in enumerate(printer_hosts):
        c = "00E676" if idx == 0 else "2979FF"
        p_items = zbx_call("item.get", {"hostids": [p["hostid"]], "output": ["itemid", "key_", "name"]}, auth)
        pmap = {it["key_"]: it["itemid"] for it in p_items}
        if "printer_snmp.sh[{HOST.CONN},toner_pct]" in pmap:
            printer_toner_items.append({"itemid": pmap["printer_snmp.sh[{HOST.CONN},toner_pct]"], "name": p["name"], "color": c})
        if "printer_snmp.sh[{HOST.CONN},adf_pct]" in pmap:
            printer_adf_items.append({"itemid": pmap["printer_snmp.sh[{HOST.CONN},adf_pct]"], "name": p["name"], "color": c})
        if "printer_snmp.sh[{HOST.CONN},pages]" in pmap:
            printer_page_items.append({"itemid": pmap["printer_snmp.sh[{HOST.CONN},pages]"], "name": p["name"], "color": c})
        if "icmppingsec" in pmap:
            printer_rtt_items.append({"itemid": pmap["icmppingsec"], "name": p["name"], "color": c})

    # Servidor NOC (10866) ou Zabbix server (10084)
    noc_items = zbx_call("item.get", {"hostids": ["10866", "10084"], "output": ["itemid", "key_", "name"]}, auth)
    noc_map = {}
    for it in noc_items:
        if it["key_"] not in noc_map:
            noc_map[it["key_"]] = it["itemid"]

    # VoIP Grandstream (Group 25)
    voip_hosts = zbx_call("host.get", {"groupids": ["25"], "output": ["hostid", "name"], "sortfield": "name"}, auth)
    voip_rtt_items = []
    voip_loss_items = []
    for idx, vh in enumerate(voip_hosts[:6]):
        c = ap_colors[idx % len(ap_colors)]
        v_items = zbx_call("item.get", {"hostids": [vh["hostid"]], "output": ["itemid", "key_", "name"]}, auth)
        vmap = {it["key_"]: it["itemid"] for it in v_items}
        clean_r = vh["name"].split(" (")[0]
        if "icmppingsec" in vmap:
            voip_rtt_items.append({"itemid": vmap["icmppingsec"], "name": clean_r, "color": c})
        if "icmppingloss" in vmap:
            voip_loss_items.append({"itemid": vmap["icmppingloss"], "name": clean_r, "color": c})

    print(f"UniFi APs: {len(ap_hosts)}, Impressoras: {len(printer_hosts)}, VoIP: {len(voip_hosts)}")

    # =========================================================================
    # DASHBOARD 1: 🌾 NOC Master 360° & Mitigação IT
    # =========================================================================
    print("Criando Dashboard 1: NOC Master 360° & Mitigação IT...")
    page_exec = {
        "name": "🌐 Visão Executiva & Mitigação IT",
        "widgets": [
            {
                "type": "problems",
                "name": "🚨 Alarmes e Incidentes Ativos de TI (Disaster / High / Warning)",
                "x": 0, "y": 0, "width": 14, "height": 5,
                "view_mode": 0,
                "fields": [
                    {"type": 0, "name": "show", "value": "1"},
                    {"type": 0, "name": "show_suppressed", "value": "0"}
                ]
            },
            {
                "type": "hostavail",
                "name": "🖥️ Disponibilidade Global do Parque Corporativo",
                "x": 14, "y": 0, "width": 10, "height": 5,
                "view_mode": 0,
                "fields": [
                    {"type": 0, "name": "layout", "value": "1"},
                    {"type": 0, "name": "interface_type.0", "value": "1"},
                    {"type": 0, "name": "interface_type.1", "value": "2"}
                ]
            },
            build_svg_graph(
                "🚀 Consumo de Banda WAN em Tempo Real (Download vs Upload)",
                0, 5, 12, 6,
                [
                    {"itemid": wan_items_map.get("net_speedtest.sh[download]", "72108"), "name": "Download", "color": "00E676", "width": 3},
                    {"itemid": wan_items_map.get("net_speedtest.sh[upload]", "72109"), "name": "Upload", "color": "2979FF", "width": 2}
                ]
            ),
            build_svg_graph(
                "🛡️ Mitigação & Latência Externa em MS (Google 8.8.8.8 vs Cloudflare 1.1.1.1)",
                12, 5, 12, 6,
                [
                    {"itemid": wan_items_map.get("icmppingsec[8.8.8.8]", "72112"), "name": "Google DNS (8.8.8.8)", "color": "00E676", "width": 2},
                    {"itemid": wan_items_map.get("icmppingsec[1.1.1.1]", "72113"), "name": "Cloudflare (1.1.1.1)", "color": "FFD600", "width": 2}
                ]
            ),
            {
                "type": "tophosts",
                "name": "📶 Telemetria Consolidada dos Access Points UniFi (Wi-Fi Enterprise)",
                "x": 0, "y": 11, "width": 24, "height": 8,
                "view_mode": 0,
                "fields": [
                    {"type": 2, "name": "groupids.0", "value": "24"},
                    {"type": 1, "name": "columns.0.name", "value": "Clientes Ativos"},
                    {"type": 1, "name": "columns.0.item", "value": "unifi_telemetry.sh[{HOST.CONN},clients]"},
                    {"type": 0, "name": "columns.0.data", "value": "1"},
                    {"type": 0, "name": "columns.0.display", "value": "2"},
                    {"type": 1, "name": "columns.0.max", "value": "45"},
                    {"type": 1, "name": "columns.1.name", "value": "SSID Principal"},
                    {"type": 1, "name": "columns.1.item", "value": "unifi_telemetry.sh[{HOST.CONN},ssid]"},
                    {"type": 0, "name": "columns.1.data", "value": "1"},
                    {"type": 0, "name": "columns.1.display", "value": "1"},
                    {"type": 1, "name": "columns.2.name", "value": "Latência (ms)"},
                    {"type": 1, "name": "columns.2.item", "value": "icmppingsec"},
                    {"type": 0, "name": "columns.2.data", "value": "1"},
                    {"type": 0, "name": "columns.2.display", "value": "1"},
                    {"type": 1, "name": "columns.3.name", "value": "Perda (%)"},
                    {"type": 1, "name": "columns.3.item", "value": "icmppingloss"},
                    {"type": 0, "name": "columns.3.data", "value": "1"},
                    {"type": 0, "name": "columns.3.display", "value": "1"},
                    {"type": 1, "name": "columns.4.name", "value": "Throughput RX"},
                    {"type": 1, "name": "columns.4.item", "value": "unifi_telemetry.sh[{HOST.CONN},speed_rx]"},
                    {"type": 0, "name": "columns.4.data", "value": "1"},
                    {"type": 0, "name": "columns.4.display", "value": "1"}
                ]
            }
        ]
    }

    page_wifi = {
        "name": "📶 Cobertura Wi-Fi & APs UniFi",
        "widgets": [
            build_svg_graph("👥 Clientes Conectados por Access Point (Tempo Real)", 0, 0, 14, 7, ap_client_items, legend_cols=3),
            build_svg_graph("⚡ Latência RTT dos APs UniFi em MS", 14, 0, 10, 7, ap_latency_items, legend_cols=2),
            build_svg_graph("📥 Throughput Download (RX) por AP", 0, 7, 12, 6, ap_rx_items, legend_cols=3),
            build_svg_graph("📤 Throughput Upload (TX) por AP", 12, 7, 12, 6, ap_tx_items, legend_cols=3),
            build_svg_graph("🛡️ Perda de Pacotes Wi-Fi ICMP (%)", 0, 13, 24, 5, ap_loss_items, legend_cols=6)
        ]
    }

    page_wan = {
        "name": "🌐 Links WAN & Operadora Telecom",
        "widgets": [
            build_gauge("📥 Taxa de Download Atual (Contrato 600M)", 0, 0, 6, 5, wan_items_map.get("net_speedtest.sh[download]", "72108"), "0", "78643200"),
            build_gauge("📤 Taxa de Upload Atual (Contrato 300M)", 6, 0, 6, 5, wan_items_map.get("net_speedtest.sh[upload]", "72109"), "0", "39321600"),
            build_item_card("📡 Operadora / Provedor ISP Ativo", 12, 0, 6, 2, wan_items_map.get("net_speedtest.sh[isp]", "72110")),
            build_item_card("🌐 Endereço IP Público WAN", 18, 0, 6, 2, wan_items_map.get("net_speedtest.sh[public_ip]", "72111")),
            build_item_card("🛡️ Perda de Pacotes Primária (Google 8.8.8.8)", 12, 2, 6, 3, wan_items_map.get("icmppingloss[8.8.8.8]", "72114")),
            build_item_card("🛡️ Perda de Pacotes Secundária (Cloudflare 1.1.1.1)", 18, 2, 6, 3, wan_items_map.get("icmppingloss[1.1.1.1]", "72485")),
            build_svg_graph(
                "📈 Histórico de Tráfego WAN (Download vs Upload)",
                0, 5, 12, 6,
                [
                    {"itemid": wan_items_map.get("net_speedtest.sh[download]", "72108"), "name": "Download", "color": "00E676", "width": 3},
                    {"itemid": wan_items_map.get("net_speedtest.sh[upload]", "72109"), "name": "Upload", "color": "2979FF", "width": 2}
                ]
            ),
            build_svg_graph(
                "⏱️ Latência Primária (8.8.8.8) e Secundária (1.1.1.1) em MS",
                12, 5, 12, 6,
                [
                    {"itemid": wan_items_map.get("icmppingsec[8.8.8.8]", "72112"), "name": "Google 8.8.8.8", "color": "00E676", "width": 2},
                    {"itemid": wan_items_map.get("icmppingsec[1.1.1.1]", "72113"), "name": "Cloudflare 1.1.1.1", "color": "FFD600", "width": 2}
                ]
            ),
            build_svg_graph(
                "🛡️ Mitigação Ativa: Histórico de Perda de Pacotes WAN (%)",
                0, 11, 24, 5,
                [
                    {"itemid": wan_items_map.get("icmppingloss[8.8.8.8]", "72114"), "name": "Perda Primária (8.8.8.8)", "color": "FF1744", "width": 2},
                    {"itemid": wan_items_map.get("icmppingloss[1.1.1.1]", "72485"), "name": "Perda Secundária (1.1.1.1)", "color": "FF9100", "width": 2}
                ]
            )
        ]
    }

    # Servidores
    cpu_item = noc_map.get("system.cpu.util[,system]", "42229")
    ram_item = noc_map.get("vm.memory.utilization", "42261")
    load_item = noc_map.get("system.cpu.load[all,avg1]", "42249")
    uptime_item = noc_map.get("system.uptime", "42264")

    page_srv = {
        "name": "🖥️ Servidores & Infraestrutura NOC",
        "widgets": [
            build_gauge("⚡ Utilização de CPU - SRV NOC (%)", 0, 0, 6, 5, cpu_item, "0", "100"),
            build_gauge("🧠 Utilização de Memória RAM (%)", 6, 0, 6, 5, ram_item, "0", "100"),
            build_item_card("⏱️ Uptime do Sistema Operacional", 12, 0, 6, 5, uptime_item),
            build_item_card("📊 Load Average (1 min)", 18, 0, 6, 5, load_item),
            build_svg_graph(
                "📈 CPU e Carga do Sistema (SRV-NOC)",
                0, 5, 12, 6,
                [
                    {"itemid": cpu_item, "name": "CPU System (%)", "color": "00E676", "width": 2},
                    {"itemid": load_item, "name": "Load Average", "color": "FFD600", "width": 2}
                ]
            ),
            build_svg_graph(
                "📈 Utilização de Memória RAM (%)",
                12, 5, 12, 6,
                [
                    {"itemid": ram_item, "name": "RAM Usada (%)", "color": "2979FF", "width": 2}
                ]
            ),
            {
                "type": "tophosts",
                "name": "📋 Matriz de Servidores Corporativos",
                "x": 0, "y": 11, "width": 24, "height": 6,
                "view_mode": 0,
                "fields": [
                    {"type": 2, "name": "groupids.0", "value": "23"},
                    {"type": 1, "name": "columns.0.name", "value": "Latência ICMP (ms)"},
                    {"type": 1, "name": "columns.0.item", "value": "icmppingsec"},
                    {"type": 0, "name": "columns.0.data", "value": "1"},
                    {"type": 0, "name": "columns.0.display", "value": "1"},
                    {"type": 1, "name": "columns.1.name", "value": "SSH 22"},
                    {"type": 1, "name": "columns.1.item", "value": "net.tcp.service[tcp,,22]"},
                    {"type": 0, "name": "columns.1.data", "value": "1"},
                    {"type": 0, "name": "columns.1.display", "value": "1"}
                ]
            }
        ]
    }

    # Impressoras
    page_print = {
        "name": "🖨️ Parque de Impressoras HP",
        "widgets": [
            build_gauge("🖨️ Toner Preto HP LaserJet 220 (%)", 0, 0, 6, 5, printer_toner_items[0]["itemid"] if printer_toner_items else "72370", "0", "100"),
            build_gauge("🖨️ Toner Preto HP LaserJet 221 (%)", 6, 0, 6, 5, printer_toner_items[1]["itemid"] if len(printer_toner_items) > 1 else "72370", "0", "100"),
            build_gauge("📑 Vida Útil Kit ADF HP 220 (%)", 12, 0, 6, 5, printer_adf_items[0]["itemid"] if printer_adf_items else "72371", "0", "100"),
            build_item_card("📄 Páginas Impressas HP 220", 18, 0, 6, 5, printer_page_items[0]["itemid"] if printer_page_items else "72372"),
            build_svg_graph("⏱️ Latência RTT das Impressoras em MS", 0, 5, 12, 6, printer_rtt_items),
            {
                "type": "tophosts",
                "name": "📋 Parque de Impressão HP LaserJet Corporativo",
                "x": 12, "y": 5, "width": 12, "height": 6,
                "view_mode": 0,
                "fields": [
                    {"type": 2, "name": "groupids.0", "value": "26"},
                    {"type": 1, "name": "columns.0.name", "value": "Toner Preto (%)"},
                    {"type": 1, "name": "columns.0.item", "value": "printer_snmp.sh[{HOST.CONN},toner_pct]"},
                    {"type": 0, "name": "columns.0.data", "value": "1"},
                    {"type": 0, "name": "columns.0.display", "value": "2"},
                    {"type": 1, "name": "columns.0.max", "value": "100"},
                    {"type": 1, "name": "columns.1.name", "value": "Kit ADF (%)"},
                    {"type": 1, "name": "columns.1.item", "value": "printer_snmp.sh[{HOST.CONN},adf_pct]"},
                    {"type": 0, "name": "columns.1.data", "value": "1"},
                    {"type": 0, "name": "columns.1.display", "value": "1"},
                    {"type": 1, "name": "columns.2.name", "value": "Latência (ms)"},
                    {"type": 1, "name": "columns.2.item", "value": "icmppingsec"},
                    {"type": 0, "name": "columns.2.data", "value": "1"},
                    {"type": 0, "name": "columns.2.display", "value": "1"}
                ]
            }
        ]
    }

    # VoIP
    page_voip = {
        "name": "📞 Ramais VoIP & Telefonia Grandstream",
        "widgets": [
            build_svg_graph("🎙️ Latência / RTT de Voz dos Ramais em MS", 0, 0, 14, 6, voip_rtt_items, legend_cols=3),
            build_svg_graph("🛡️ Perda de Pacotes de Áudio (%)", 14, 0, 10, 6, voip_loss_items, legend_cols=2),
            {
                "type": "tophosts",
                "name": "📋 Monitoramento em Tempo Real dos 14 Ramais VoIP e Telefonia PABX",
                "x": 0, "y": 6, "width": 24, "height": 9,
                "view_mode": 0,
                "fields": [
                    {"type": 2, "name": "groupids.0", "value": "25"},
                    {"type": 1, "name": "columns.0.name", "value": "RTT / Latência de Voz (ms)"},
                    {"type": 1, "name": "columns.0.item", "value": "icmppingsec"},
                    {"type": 0, "name": "columns.0.data", "value": "1"},
                    {"type": 0, "name": "columns.0.display", "value": "1"},
                    {"type": 1, "name": "columns.1.name", "value": "Perda de Pacotes (%)"},
                    {"type": 1, "name": "columns.1.item", "value": "icmppingloss"},
                    {"type": 0, "name": "columns.1.data", "value": "1"},
                    {"type": 0, "name": "columns.1.display", "value": "1"},
                    {"type": 1, "name": "columns.2.name", "value": "Sinalização SIP 5060"},
                    {"type": 1, "name": "columns.2.item", "value": "net.tcp.service[tcp,,5060]"},
                    {"type": 0, "name": "columns.2.data", "value": "1"},
                    {"type": 0, "name": "columns.2.display", "value": "1"}
                ]
            }
        ]
    }

    dash_master = {
        "name": "🌾 NOC Master 360° & Mitigação IT",
        "display_period": 30,
        "auto_start": 1,
        "pages": [page_exec, page_wifi, page_wan, page_srv, page_print, page_voip]
    }

    r1 = zbx_call("dashboard.create", dash_master, auth)
    print(f"  [SUCESSO] Dashboard 1 Criado: ID {r1['dashboardids'][0]}")

    # =========================================================================
    # DASHBOARD 2: 📶 Cobertura Wi-Fi & APs UniFi
    # =========================================================================
    print("Criando Dashboard 2: Cobertura Wi-Fi & APs UniFi...")
    dash_wifi = {
        "name": "📶 Cobertura Wi-Fi & APs UniFi",
        "display_period": 30,
        "auto_start": 1,
        "pages": [page_wifi]
    }
    r2 = zbx_call("dashboard.create", dash_wifi, auth)
    print(f"  [SUCESSO] Dashboard 2 Criado: ID {r2['dashboardids'][0]}")

    # =========================================================================
    # DASHBOARD 3: 🌐 Links WAN & Operadora Telecom
    # =========================================================================
    print("Criando Dashboard 3: Links WAN & Operadora Telecom...")
    dash_wan = {
        "name": "🌐 Links WAN & Operadora Telecom",
        "display_period": 30,
        "auto_start": 1,
        "pages": [page_wan]
    }
    r3 = zbx_call("dashboard.create", dash_wan, auth)
    print(f"  [SUCESSO] Dashboard 3 Criado: ID {r3['dashboardids'][0]}")

    # =========================================================================
    # DASHBOARD 4: 🖥️ Servidores & Estações de Trabalho
    # =========================================================================
    print("Criando Dashboard 4: Servidores & Estações de Trabalho...")
    dash_srv = {
        "name": "🖥️ Servidores & Estações de Trabalho",
        "display_period": 30,
        "auto_start": 1,
        "pages": [page_srv]
    }
    r4 = zbx_call("dashboard.create", dash_srv, auth)
    print(f"  [SUCESSO] Dashboard 4 Criado: ID {r4['dashboardids'][0]}")

    # =========================================================================
    # DASHBOARD 5: 🖨️ Parque de Impressoras & Suprimentos
    # =========================================================================
    print("Criando Dashboard 5: Parque de Impressoras & Suprimentos...")
    dash_print = {
        "name": "🖨️ Parque de Impressoras & Suprimentos",
        "display_period": 30,
        "auto_start": 1,
        "pages": [page_print]
    }
    r5 = zbx_call("dashboard.create", dash_print, auth)
    print(f"  [SUCESSO] Dashboard 5 Criado: ID {r5['dashboardids'][0]}")

    # =========================================================================
    # DASHBOARD 6: 📞 Ramais VoIP & Telefonia Grandstream
    # =========================================================================
    print("Criando Dashboard 6: Ramais VoIP & Telefonia Grandstream...")
    dash_voip = {
        "name": "📞 Ramais VoIP & Telefonia Grandstream",
        "display_period": 30,
        "auto_start": 1,
        "pages": [page_voip]
    }
    r6 = zbx_call("dashboard.create", dash_voip, auth)
    print(f"  [SUCESSO] Dashboard 6 Criado: ID {r6['dashboardids'][0]}")

    print("\n[FINALIZADO COM SUCESSO] Todos os 6 Dashboards e Seções foram criados no Zabbix nativo!")

if __name__ == "__main__":
    main()
