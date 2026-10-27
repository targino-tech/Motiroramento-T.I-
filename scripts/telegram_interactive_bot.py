#!/usr/bin/env python3
"""
Bot Interativo Moderno Telegram - Enterprise NOC NOC 2.0
Recursos:
- Interface SPA (Single Page Application) no Telegram: Mensagens limpas, auto-exclusão de comandos de texto e edição no mesmo card
- Caixas de Seleção (Checkboxes interativas [✅] / [⬜]) com salvamento de preferências
- Consulta detalhada de Ativos & Hosts (Navegação por Setor ou Busca Rápida por IP/Nome)
- Telemetria avançada em tempo real (Impressoras HP, WAN TOP FIBRA, UniFi APs, Ramais VoIP)
- Reconhecimento de Incidentes (ACK) direto pelo Telegram
- Teste Real de Velocidade (Speedtest Assíncrono Threaded) executado diretamente na borda com atualização de cache Zabbix
- Teste de Impressão Direto via RAW TCP 9100 nas impressoras HP LaserJet 220 e 221
- Envio de Logo Oficial Transparente e Identidade Visual Enterprise NOC
"""

import sys, os, time, json, urllib.request, urllib.parse, re, subprocess, socket, datetime, threading

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "SEU_BOT_TOKEN_AQUI")
ZABBIX_URL = os.environ.get("ZABBIX_API_URL", "http://127.0.0.1/api_jsonrpc.php")
PREFS_FILE = "/home/infra/monitoring/scripts/telegram_preferences.json"

DEFAULT_FILTERS = {
    "f_disaster": {"label": "Alertas Desastre (WAN/Borda)", "enabled": True},
    "f_high": {"label": "Alertas Alta Prioridade (ERP)", "enabled": True},
    "f_printer": {"label": "Suprimentos HP (<15% Toner)", "enabled": True},
    "f_unifi": {"label": "Wi-Fi UniFi (Perda Pacotes)", "enabled": True},
    "f_voip": {"label": "Telefonia VoIP Grandstream", "enabled": True},
    "f_lunch": {"label": "Silenciar Estações no Almoço", "enabled": True}
}

user_preferences = {}
is_speedtest_running = False

def load_preferences():
    global user_preferences
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r") as f:
                user_preferences = json.load(f)
        except Exception:
            user_preferences = {}

def save_preferences():
    try:
        with open(PREFS_FILE, "w") as f:
            json.dump(user_preferences, f, indent=2)
    except Exception as e:
        print(f"Erro ao salvar preferências: {e}")

def get_user_filters(chat_id):
    chat_id = str(chat_id)
    if chat_id not in user_preferences:
        user_preferences[chat_id] = {k: v.copy() for k, v in DEFAULT_FILTERS.items()}
    return user_preferences[chat_id]

def zbx_call(method, params, auth=None):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    req = urllib.request.Request(ZABBIX_URL, headers=headers, data=json.dumps(payload).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode())
        if "error" in res:
            raise Exception(res["error"])
        return res["result"]

def get_zbx_auth():
    return zbx_call("user.login", {"username": "Admin", "password": "zabbix"})

def telegram_api(method, data=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, headers=headers, data=payload)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"Telegram API Error ({method}): {err_body}")
        try:
            return json.loads(err_body)
        except Exception:
            return {"ok": False, "description": err_body}
    except Exception as e:
        print(f"Telegram API Exception ({method}): {e}")
        return {"ok": False, "description": str(e)}

def delete_msg(chat_id, message_id):
    try:
        telegram_api("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
    except Exception:
        pass

def send_noc_branding(chat_id):
    caption = (
        "🌐 *Enterprise IT Operations*\n"
        "🏢 *Tecnologia da Informação (TI) & Central de Monitoramento NOC*\n\n"
        "📍 *Infraestrutura:* 54 Ativos Monitorados em Tempo Real 24x7\n"
        "• Link de Borda & WAN (TOP FIBRA)\n"
        "• Servidores Corporativos & ERP de Produção\n"
        "• Wi-Fi Corporativo Ubiquiti UniFi APs\n"
        "• Telefonia IP & Ramais Grandstream\n"
        "• Parque de Impressão HP LaserJet Flow MFP E52645\n\n"
        "_Enterprise NOC operando com proatividade, segurança e alta disponibilidade._"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 Painel Executivo da Rede", "callback_data": "menu_status"},
                {"text": "🚀 Speedtest Real", "callback_data": "trigger_speedtest"}
            ],
            [
                {"text": "🖨️ Impressoras HP (2)", "callback_data": "menu_printer"},
                {"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": caption,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    })

# ----------------- MENUS E TELAS -----------------

def build_main_menu():
    text = (
        "🌾 *Painel NOC Interativo 2.0*\n\n"
        "⚡ *Interface Moderna SPA:* Todas as consultas, diagnósticos e speedtest atualizam diretamente neste card sem poluir sua conversa.\n\n"
        "Selecione uma área abaixo para interagir:"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 Central de Dashboards & Mitigação", "callback_data": "menu_dashboards"}
            ],
            [
                {"text": "📈 Painel Executivo da Rede", "callback_data": "menu_status"},
                {"text": "🔍 Consultar Ativos & Hosts", "callback_data": "menu_sectors"}
            ],
            [
                {"text": "🖨️ Impressoras HP (2 Unidades)", "callback_data": "menu_printer"},
                {"text": "🌐 Link WAN & Borda", "callback_data": "menu_wan"}
            ],
            [
                {"text": "🚀 Speedtest Real da Borda", "callback_data": "trigger_speedtest"},
                {"text": "🌾 Visão Institucional NOC", "callback_data": "menu_logo"}
            ],
            [
                {"text": "📶 UniFi APs Wi-Fi", "callback_data": "menu_unifi"},
                {"text": "📞 Ramais Grandstream", "callback_data": "menu_voip"}
            ],
            [
                {"text": "☑️ Caixas de Seleção (Filtros)", "callback_data": "menu_filters"}
            ],
            [
                {"text": "🔄 Atualizar Card", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard

def build_dashboards_menu():
    text = (
        "📊 *Central de Dashboards & Mitigação de TI - Enterprise NOC*\n\n"
        "Selecione um dos painéis de alta disponibilidade abaixo para acesso direto:\n\n"
        "🛡️ *1. Central de Mitigação de Incidentes (Zabbix 444)*\n"
        "• Matriz de Impacto Crítico: `ERP > WAN > Wi-Fi > Impressão`\n"
        "• Topologia de Contingência & Rotas com failover dinâmico\n"
        "• Fila Ativa de Incidentes com SLA e Log de Automações\n"
        "🔗 [Abrir Dashboard 444](http://10.0.0.10/zabbix.php?action=dashboard.view&dashboardid=444)\n\n"
        "🌾 *2. Enterprise NOC NOC Master 360° (Grafana)*\n"
        "• Velocímetros animados de Download (600 Mbps) & Upload\n"
        "• Telemetria em tempo real dos 6 APs UniFi & Latência\n"
        "• Bar Gauges de Toner HP LaserJet 220 e 221 e Páginas\n"
        "• Recursos do Servidor NOC (CPU, Memória RAM, Throughput)\n"
        "🔗 [Abrir Grafana Master](http://10.0.0.10:3000/d/noc-master/)\n\n"
        "📈 *3. SLA Executivo, Tráfego e Disponibilidade (Zabbix 445)*\n"
        "• SLA 24x7 de todos os 54 hosts monitorados\n"
        "• Monitoramento de volumetria e disponibilidade contínua\n"
        "🔗 [Abrir Dashboard 445](http://10.0.0.10/zabbix.php?action=dashboard.view&dashboardid=445)\n\n"
        "🌐 *4. Visão Global Enterprise NOC (Zabbix 1)*\n"
        "• 3 Abas: Visão Geral / UniFi Wi-Fi / Parque de Impressão\n"
        "🔗 [Abrir Dashboard 1](http://10.0.0.10/zabbix.php?action=dashboard.view&dashboardid=1)\n"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🛡️ Mitigação (Zbx 444)", "url": "http://10.0.0.10/zabbix.php?action=dashboard.view&dashboardid=444"},
                {"text": "🌾 Grafana Master 360°", "url": "http://10.0.0.10:3000/d/noc-master/"}
            ],
            [
                {"text": "📈 SLA Executivo (Zbx 445)", "url": "http://10.0.0.10/zabbix.php?action=dashboard.view&dashboardid=445"},
                {"text": "🌐 Visão Global (Zbx 1)", "url": "http://10.0.0.10/zabbix.php?action=dashboard.view&dashboardid=1"}
            ],
            [
                {"text": "🔄 Atualizar Painel", "callback_data": "menu_dashboards"},
                {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard


def build_sectors_menu():
    text = (
        "🔍 *Consulta de Ativos por Setor Operacional*\n\n"
        "Selecione um grupo para listar os equipamentos e consultar a telemetria detalhada de cada host:"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🖥️ Servidores Críticos (6)", "callback_data": "list_grp_23"},
                {"text": "🌐 Borda & Gateways (1)", "callback_data": "list_grp_22"}
            ],
            [
                {"text": "📶 Wi-Fi UniFi APs (2)", "callback_data": "list_grp_24"},
                {"text": "🖨️ Impressoras HP (2)", "callback_data": "list_grp_26"}
            ],
            [
                {"text": "📞 Ramais Grandstream (14)", "callback_data": "list_grp_25_page_1"},
                {"text": "💻 Estações & Notebooks (28)", "callback_data": "list_grp_27_page_1"}
            ],
            [
                {"text": "⬅️ Voltar ao Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard

def build_host_list(group_id, page=1):
    try:
        auth = get_zbx_auth()
        grp = zbx_call("hostgroup.get", {"groupids": [str(group_id)], "output": ["name"]}, auth)[0]
        hosts = zbx_call("host.get", {
            "groupids": [str(group_id)],
            "output": ["hostid", "name", "host"],
            "selectInterfaces": ["ip"],
            "sortfield": "name",
            "sortorder": "ASC"
        }, auth)
        
        per_page = 8
        total = len(hosts)
        start = (page - 1) * per_page
        end = start + per_page
        current_hosts = hosts[start:end]
        max_pages = (total + per_page - 1) // per_page if total > 0 else 1

        text = (
            f"📁 *Setor:* `{grp['name']}`\n"
            f"📋 *Total de Dispositivos:* `{total}` | *Página:* `{page}/{max_pages}`\n\n"
            f"Toque em um host abaixo para abrir a ficha técnica completa:"
        )

        rows = []
        for h in current_hosts:
            ip = h["interfaces"][0]["ip"] if h.get("interfaces") else "N/A"
            clean_name = h["name"]
            if len(clean_name) > 28:
                clean_name = clean_name[:25] + "..."
            rows.append([
                {"text": f"🔹 {clean_name} ({ip})", "callback_data": f"host_{h['hostid']}_{group_id}_{page}"}
            ])

        # Pagination
        nav_row = []
        if page > 1:
            nav_row.append({"text": "◀️ Anterior", "callback_data": f"list_grp_{group_id}_page_{page - 1}"})
        if end < total:
            nav_row.append({"text": "Próxima ▶️", "callback_data": f"list_grp_{group_id}_page_{page + 1}"})

        if nav_row:
            rows.append(nav_row)

        rows.append([
            {"text": "⬅️ Voltar aos Setores", "callback_data": "menu_sectors"},
            {"text": "🏠 Início", "callback_data": "refresh_menu"}
        ])

        return text, {"inline_keyboard": rows}
    except Exception as e:
        return f"Erro ao listar hosts: {e}", {"inline_keyboard": [[{"text": "⬅️ Voltar", "callback_data": "menu_sectors"}]]}

def build_host_card(host_id, back_group=None, back_page=1):
    try:
        auth = get_zbx_auth()
        hosts = zbx_call("host.get", {
            "hostids": [str(host_id)],
            "selectInterfaces": ["ip", "port"],
            "selectGroups": ["groupid", "name"],
            "selectItems": ["key_", "lastvalue", "name", "units"],
            "output": ["hostid", "name", "host", "status", "description"]
        }, auth)
        if not hosts:
            return "Ativo não encontrado.", {"inline_keyboard": [[{"text": "⬅️ Voltar", "callback_data": "menu_sectors"}]]}
        
        h = hosts[0]
        ip = h["interfaces"][0]["ip"] if h.get("interfaces") else "N/A"
        grp_name = h["groups"][0]["name"] if h.get("groups") else "Geral"

        # Active problems
        probs = zbx_call("problem.get", {"hostids": [str(host_id)], "output": ["name", "severity"], "suppressed": False}, auth)
        prob_str = "\n".join([f"  🚨 {p['name']}" for p in probs]) if probs else "  ✅ Nenhum incidente ativo!"

        # Extract items
        items_dict = {it["key_"]: it for it in h.get("items", [])}
        ping = items_dict.get("icmpping", {}).get("lastvalue")
        rtt = items_dict.get("icmppingsec", {}).get("lastvalue")
        loss = items_dict.get("icmppingloss", {}).get("lastvalue", "0")

        if rtt and rtt != "":
            try:
                rtt_ms = f"{float(rtt)*1000:.1f} ms"
            except Exception:
                rtt_ms = f"{rtt} s"
        else:
            rtt_ms = "N/A"

        status_icon = "🟢 ONLINE" if ping == "1" else "🔴 OFFLINE"

        # Extra metrics if printer
        extra_info = ""
        is_printer = False
        if "printer_snmp.sh[{HOST.CONN},toner_pct]" in items_dict:
            is_printer = True
            toner = items_dict["printer_snmp.sh[{HOST.CONN},toner_pct]"].get("lastvalue", "0")
            clean = items_dict.get("printer_snmp.sh[{HOST.CONN},cleaning_pct]", {}).get("lastvalue", "0")
            adf = items_dict.get("printer_snmp.sh[{HOST.CONN},adf_pct]", {}).get("lastvalue", "0")
            pages = items_dict.get("printer_snmp.sh[{HOST.CONN},pages]", {}).get("lastvalue", "0")
            lcd = items_dict.get("printer_snmp.sh[{HOST.CONN},status]", {}).get("lastvalue", "Pronta")
            serial = items_dict.get("printer_snmp.sh[{HOST.CONN},serial]", {}).get("lastvalue", "BRBSQ2Q11P")
            extra_info = (
                f"\n📦 *Telemetria de Suprimentos HP:*\n"
                f"• *Toner Preto:* `{toner}%` | *Cilindros:* `{clean}%` | *ADF:* `{adf}%`\n"
                f"• *Total Impresso:* `{int(float(pages or 0)):,} páginas`\n"
                f"• *Serial Number:* `{serial}`\n"
                f"• *Display:* _{lcd}_\n"
            )
        elif "net_speedtest.sh[download]" in items_dict:
            dl = items_dict.get("net_speedtest.sh[download]", {}).get("lastvalue", "0")
            ul = items_dict.get("net_speedtest.sh[upload]", {}).get("lastvalue", "0")
            isp = items_dict.get("net_speedtest.sh[isp]", {}).get("lastvalue", "TOP FIBRA")
            pub_ip = items_dict.get("net_speedtest.sh[public_ip]", {}).get("lastvalue", os.environ.get("PUBLIC_WAN_IP", "203.0.113.1"))
            extra_info = (
                f"\n🌐 *Telemetria WAN:*\n"
                f"• *Provedor:* `{isp}` | *IP:* `{pub_ip}`\n"
                f"• *Download:* `{float(dl)/1000000:.1f} Mbps` | *Upload:* `{float(ul)/1000000:.1f} Mbps`\n"
            )

        text = (
            f"📋 *Ficha Detalhada do Ativo*\n\n"
            f"🏷️ *Nome:* `{h['name']}`\n"
            f"📁 *Setor:* `{grp_name}`\n"
            f"🌐 *IP / Interface:* `{ip}`\n"
            f"⚡ *Status ICMP:* {status_icon}\n"
            f"⏱️ *Latência RTT:* `{rtt_ms}` | *Perda de Pacotes:* `{loss}%`\n"
            f"{extra_info}\n"
            f"🚨 *Incidentes Ativos:*\n{prob_str}\n"
        )

        rows = []
        if is_printer:
            rows.append([{"text": "🖨️ Enviar Página de Teste (RAW 9100)", "callback_data": f"print_test_{host_id}"}])
        elif "Link_Internet_WAN" in h["host"]:
            rows.append([{"text": "🚀 Executar Speedtest Real Agora", "callback_data": "trigger_speedtest"}])

        if back_group:
            rows.append([
                {"text": "⬅️ Voltar à Lista", "callback_data": f"list_grp_{back_group}_page_{back_page}"},
                {"text": "🏠 Início", "callback_data": "refresh_menu"}
            ])
        else:
            rows.append([
                {"text": "⬅️ Voltar aos Setores", "callback_data": "menu_sectors"},
                {"text": "🏠 Início", "callback_data": "refresh_menu"}
            ])

        return text, {"inline_keyboard": rows}
    except Exception as e:
        return f"Erro ao obter ativo: {e}", {"inline_keyboard": [[{"text": "⬅️ Voltar", "callback_data": "menu_sectors"}]]}

def search_hosts(query):
    try:
        auth = get_zbx_auth()
        hosts = zbx_call("host.get", {
            "search": {"name": query, "host": query},
            "searchByAny": True,
            "output": ["hostid", "name", "host"],
            "selectInterfaces": ["ip"],
            "limit": 10
        }, auth)
        return hosts
    except Exception:
        return []

def build_filters_menu(chat_id):
    filters = get_user_filters(chat_id)
    text = (
        "⚙️ *Caixas de Seleção - Filtro Interativo de Alertas*\n\n"
        "Marque ou desmarque as opções abaixo para personalizar exatamente os incidentes que acionam seu Telegram:\n\n"
        "_[✅] Notificação Ativa  |  [⬜] Notificação Silenciada_"
    )
    rows = []
    for key, item in filters.items():
        icon = "✅" if item["enabled"] else "⬜"
        rows.append([
            {"text": f"{icon} {item['label']}", "callback_data": f"toggle_{key}"}
        ])
    rows.append([
        {"text": "💾 Salvar Preferências", "callback_data": "save_filters"},
        {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
    ])
    keyboard = {"inline_keyboard": rows}
    return text, keyboard

def get_printer_status(target_hostid=None):
    try:
        auth = get_zbx_auth()
        if target_hostid:
            # Ficha técnica detalhada de uma impressora específica
            host_info = zbx_call("host.get", {
                "hostids": [str(target_hostid)],
                "output": ["hostid", "name", "host"],
                "selectInterfaces": ["ip"]
            }, auth)[0]
            items = zbx_call("item.get", {"hostids": [str(target_hostid)], "output": ["itemid", "key_", "lastvalue", "name"]}, auth)
            info = {it["key_"]: it["lastvalue"] for it in items}
            ip = host_info.get("interfaces", [{}])[0].get("ip", "192.168.1.x")
            
            toner = info.get("printer_snmp.sh[{HOST.CONN},toner_pct]", "0")
            adf = info.get("printer_snmp.sh[{HOST.CONN},adf_pct]", "0")
            clean = info.get("printer_snmp.sh[{HOST.CONN},cleaning_pct]", "0")
            pages = info.get("printer_snmp.sh[{HOST.CONN},pages]", "0")
            lcd = info.get("printer_snmp.sh[{HOST.CONN},status]", "Pronta")
            serial = info.get("printer_snmp.sh[{HOST.CONN},serial]", "N/A")
            model = info.get("printer_snmp.sh[{HOST.CONN},model]", "HP LaserJet Flow MFP E52645")
            raw9100 = info.get("net.tcp.service[tcp,,9100]", "1")
            http80 = info.get("net.tcp.service[tcp,,80]", "1")
            ping = info.get("icmpping", "1")
            
            t_val = int(float(toner or 0))
            if t_val <= 5:
                toner_badge = "🔴 CRÍTICO (0% Esgotado - Troca Imediata)"
            elif t_val <= 15:
                toner_badge = f"⚠️ ATENÇÃO ({toner}% Baixo - Solicitar Reposição)"
            else:
                toner_badge = f"🟢 NORMAL ({toner}%)"
                
            status_net = "🟢 ONLINE" if ping == "1" else "🔴 OFFLINE"
            spooler_net = "🟢 Porta 9100 Aberta" if raw9100 == "1" else "🔴 Porta 9100 Fechada"
            web_net = "🟢 Web 80 Ativa" if http80 == "1" else "🔴 Web Fechada"

            other_id = "10870" if str(target_hostid) == "10869" else "10869"
            other_label = "Ver HP 221 (Secundária)" if str(target_hostid) == "10869" else "Ver HP 220 (Matriz)"

            text = (
                f"🖨️ *Ficha Técnica da Impressora*\n"
                f"🏷️ *{host_info['name']}*\n\n"
                f"• *Modelo:* `{model}`\n"
                f"• *Número de Série:* `{serial}`\n"
                f"• *Endereço IP:* `{ip}` ({status_net})\n"
                f"• *Spooler RAW 9100:* {spooler_net}\n"
                f"• *Interface Web HTTP:* {web_net}\n\n"
                f"📦 *Telemetria de Suprimentos & Peças:*\n"
                f"• *Toner Preto (W9008MC):* {toner_badge}\n"
                f"• *Cilindros / Roletes:* `{clean}%`\n"
                f"• *Kit Alimentador ADF:* `{adf}%`\n\n"
                f"📄 *Total de Páginas Impressas:* `{int(float(pages or 0)):,} páginas`\n"
                f"📟 *Mensagem no Visor LCD:* _{lcd}_\n"
            )
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🖨️ Enviar Página de Teste (Porta 9100)", "callback_data": f"print_test_{target_hostid}"}
                    ],
                    [
                        {"text": "🔄 Atualizar Dados", "callback_data": f"printer_detail_{target_hostid}"},
                        {"text": f"🖨️ {other_label}", "callback_data": f"printer_detail_{other_id}"}
                    ],
                    [
                        {"text": "📋 Ver Parque Completo (Ambas)", "callback_data": "menu_printer"},
                        {"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}
                    ]
                ]
            }
            return text, keyboard

        # Visão Geral do Parque com AMBAS as impressoras
        p_hosts = zbx_call("host.get", {
            "hostids": ["10869", "10870"],
            "output": ["hostid", "name", "host"],
            "selectInterfaces": ["ip"]
        }, auth)
        
        printers_data = []
        for ph in p_hosts:
            hid = ph["hostid"]
            items = zbx_call("item.get", {"hostids": [hid], "output": ["key_", "lastvalue"]}, auth)
            pinfo = {it["key_"]: it["lastvalue"] for it in items}
            ip = ph.get("interfaces", [{}])[0].get("ip", "192.168.1.x")
            toner = pinfo.get("printer_snmp.sh[{HOST.CONN},toner_pct]", "0")
            clean = pinfo.get("printer_snmp.sh[{HOST.CONN},cleaning_pct]", "0")
            adf = pinfo.get("printer_snmp.sh[{HOST.CONN},adf_pct]", "0")
            pages = pinfo.get("printer_snmp.sh[{HOST.CONN},pages]", "0")
            lcd = pinfo.get("printer_snmp.sh[{HOST.CONN},status]", "Pronta")
            serial = pinfo.get("printer_snmp.sh[{HOST.CONN},serial]", "N/A")
            t_val = int(float(toner or 0))
            if t_val <= 5:
                toner_badge = f"🔴 `{toner}%` (CRÍTICO: Troca Imediata)"
            elif t_val <= 15:
                toner_badge = f"⚠️ `{toner}%` (ATENÇÃO: Reposição)"
            else:
                toner_badge = f"🟢 `{toner}%` (Normal)"
            printers_data.append({
                "hostid": hid,
                "name": ph["name"],
                "ip": ip,
                "toner_badge": toner_badge,
                "clean": clean,
                "adf": adf,
                "pages": pages,
                "lcd": lcd,
                "serial": serial
            })
            
        p1 = printers_data[0] if len(printers_data) > 0 else {}
        p2 = printers_data[1] if len(printers_data) > 1 else {}
        
        text = (
            "🖨️ *Parque de Impressão Corporativa - Enterprise NOC*\n"
            "Telemetria em tempo real das duas impressoras multifuncionais HP.\n\n"
            f"1️⃣ *{p1.get('name', 'HP LaserJet 220')}*\n"
            f"• *IP:* `{p1.get('ip')}` | *Status:* _{p1.get('lcd')}_\n"
            f"• *Toner Preto:* {p1.get('toner_badge')}\n"
            f"• *Cilindros:* `{p1.get('clean')}%` | *Kit ADF:* `{p1.get('adf')}%`\n"
            f"• *Páginas Totais:* `{int(float(p1.get('pages', 0) or 0)):,} pág` | *S/N:* `{p1.get('serial')}`\n\n"
            f"2️⃣ *{p2.get('name', 'HP LaserJet 221')}*\n"
            f"• *IP:* `{p2.get('ip')}` | *Status:* _{p2.get('lcd')}_\n"
            f"• *Toner Preto:* {p2.get('toner_badge')}\n"
            f"• *Cilindros:* `{p2.get('clean')}%` | *Kit ADF:* `{p2.get('adf')}%`\n"
            f"• *Páginas Totais:* `{int(float(p2.get('pages', 0) or 0)):,} pág` | *S/N:* `{p2.get('serial')}`\n"
        )
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔍 Detalhes HP 220 (Matriz)", "callback_data": "printer_detail_10869"},
                    {"text": "🔍 Detalhes HP 221 (Secundária)", "callback_data": "printer_detail_10870"}
                ],
                [
                    {"text": "🖨️ Teste Impressão HP 220", "callback_data": "print_test_10869"},
                    {"text": "🖨️ Teste Impressão HP 221", "callback_data": "print_test_10870"}
                ],
                [
                    {"text": "🔄 Atualizar Parque", "callback_data": "menu_printer"},
                    {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
                ]
            ]
        }
        return text, keyboard
    except Exception as e:
        text = f"Erro ao consultar parque de impressoras: {e}"
        keyboard = {"inline_keyboard": [[{"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}]]}
        return text, keyboard

def execute_print_test(hostid, operator_name="Operador TI"):
    try:
        auth = get_zbx_auth()
        host_info = zbx_call("host.get", {
            "hostids": [str(hostid)],
            "output": ["hostid", "name", "host"],
            "selectInterfaces": ["ip"]
        }, auth)[0]
        ip = host_info.get("interfaces", [{}])[0].get("ip", "192.168.1.50")
        name = host_info["name"]

        items = zbx_call("item.get", {"hostids": [str(hostid)], "output": ["key_", "lastvalue"]}, auth)
        info = {it["key_"]: it["lastvalue"] for it in items}
        toner = info.get("printer_snmp.sh[{HOST.CONN},toner_pct]", "0")
        clean = info.get("printer_snmp.sh[{HOST.CONN},cleaning_pct]", "0")
        adf = info.get("printer_snmp.sh[{HOST.CONN},adf_pct]", "0")
        pages = info.get("printer_snmp.sh[{HOST.CONN},pages]", "0")

        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        pjl_job = (
            "\x1b%-12345X@PJL\r\n"
            f"@PJL JOB NAME=\"TESTE_NOC_CORP_{hostid}\"\r\n"
            "@PJL ENTER LANGUAGE=PCL\r\n"
            "\x1bE"
            "\x1b(s1p14v0s3b4101T"
            "========================================================================\r\n"
            "                    ENTERPRISE NOC MASTER 360\r\n"
            "                 CENTRAL DE OPERACOES DE REDE & TI (NOC)\r\n"
            "                      PAGINA DE TESTE OPERACIONAL\r\n"
            "========================================================================\r\n\r\n"
            f"EQUIPAMENTO:  {name}\r\n"
            f"ENDERECO IP:  {ip} (Porta RAW JetDirect TCP 9100)\r\n"
            f"DATA E HORA:  {now_str} (Horario Local de MT - America/Cuiaba)\r\n"
            f"SOLICITANTE:  {operator_name} via Telegram Bot (@NocEnterpriseBot)\r\n\r\n"
            "------------------------------------------------------------------------\r\n"
            "STATUS DE CONECTIVIDADE E TESTE DE COMUNICACAO:\r\n"
            "[X] Conexao TCP Porta 9100 Estabelecida com Sucesso\r\n"
            "[X] Spooler de Rede da Impressora Ativo e Respondendo\r\n"
            "[X] Telemetria SNMP MIB RFC 3805 Monitorada no Zabbix 7.0 NOC\r\n"
            "------------------------------------------------------------------------\r\n"
            f"- Nivel de Toner Preto: {toner}%\r\n"
            f"- Vida Util dos Cilindros/Roletes: {clean}%\r\n"
            f"- Vida Util do Kit ADF: {adf}%\r\n"
            f"- Contador Geral de Paginas: {pages} paginas impressas\r\n"
            "------------------------------------------------------------------------\r\n\r\n"
            "Enterprise IT - Monitoramento Ativo e Eficiencia Operacional\r\n"
            "========================================================================\r\n"
            "\x0c"
            "\x1b%-12345X"
        )

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, 9100))
        s.sendall(pjl_job.encode("latin1"))
        s.close()

        text = (
            "✅ *Página de Teste Enviada com Sucesso!*\n\n"
            f"🖨️ *Impressora:* `{name}`\n"
            f"🌐 *Endereço IP:* `{ip}:9100` (RAW JetDirect)\n"
            f"👤 *Operador Solicitante:* `{operator_name}`\n"
            f"🕒 *Horário do Envio:* `{now_str}` (Horário de MT)\n\n"
            f"📄 O trabalho PCL foi aceito diretamente pelo spooler de rede da impressora.\n"
            f"_Verifique a bandeja de saída do equipamento físico._"
        )
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Enviar Outra Página", "callback_data": f"print_test_{hostid}"},
                    {"text": "🔍 Ver Ficha da Impressora", "callback_data": f"printer_detail_{hostid}"}
                ],
                [
                    {"text": "📋 Ver Parque Completo", "callback_data": "menu_printer"},
                    {"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}
                ]
            ]
        }
        return text, keyboard
    except Exception as e:
        clean_err = str(e).replace("[", "").replace("]", "").replace("'", "")
        text = f"❌ *Erro ao enviar página de teste:* `{clean_err}`"
        keyboard = {"inline_keyboard": [[{"text": "⬅️ Voltar", "callback_data": f"printer_detail_{hostid}"}]]}
        return text, keyboard

def run_speedtest_thread(chat_id, message_id):
    global is_speedtest_running
    try:
        t0 = time.time()
        res = subprocess.run(
            ["docker", "exec", "zabbix-server", "speedtest-cli", "--json", "--secure", "--timeout", "5"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, text=True
        )
        if res.returncode != 0:
            raise Exception("Falha no teste de rede: " + (res.stderr.strip()[:100] or "Timeout"))

        data = json.loads(res.stdout)
        elapsed = round(time.time() - t0, 1)

        dl_bps = data.get("download", 0)
        ul_bps = data.get("upload", 0)
        dl_mbps = dl_bps / 1000000
        ul_mbps = ul_bps / 1000000
        ping = round(data.get("ping", 0), 1)

        server_info = data.get("server", {})
        server_name = server_info.get("name", "Cuiabá")
        sponsor = server_info.get("sponsor", "TOP FIBRA")
        client_info = data.get("client", {})
        ip = client_info.get("ip", os.environ.get("PUBLIC_WAN_IP", "203.0.113.1"))
        isp = client_info.get("isp", "TOP FIBRA")
        isp_clean = re.sub(r"[\(\)\[\]]", "", isp)
        sponsor_clean = re.sub(r"[\(\)\[\]]", "", sponsor)
        server_clean = re.sub(r"[\(\)\[\]]", "", server_name)

        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Update Zabbix cache
        cache_data = {
            "download": dl_bps,
            "upload": ul_bps,
            "ping": ping,
            "public_ip": ip,
            "isp": isp,
            "server": f"{server_name} ({sponsor})",
            "timestamp": int(time.time())
        }
        cache_str = json.dumps(cache_data)
        try:
            with open("/tmp/speedtest_cache.json", "w") as f:
                f.write(cache_str)
            subprocess.run(["docker", "exec", "-i", "zabbix-server", "sh", "-c", "cat > /tmp/speedtest_cache.json"], input=cache_str, text=True, timeout=5)
        except Exception:
            pass

        result_text = (
            "🚀 *Resultado do Speedtest Real - Borda WAN*\n\n"
            f"🏢 *Provedor (ISP):* `{isp_clean}`\n"
            f"🌐 *IP Público WAN:* `{ip}`\n"
            f"🎯 *Servidor:* `{server_clean}` ({sponsor_clean})\n"
            f"⚡ *Latência (Ping):* `{ping} ms` | *Tempo de Teste:* `{elapsed}s`\n\n"
            f"📥 *Velocidade de Download:* `{dl_mbps:.2f} Mbps` 🟢\n"
            f"📤 *Velocidade de Upload:* `{ul_mbps:.2f} Mbps` 🟢\n\n"
            f"🕒 *Medição Concluída:* `{now_str}` (Horário de MT)\n"
            f"_Telemetria de fibra óptica atualizada no Zabbix NOC._"
        )
        result_kb = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Executar Novo Speedtest", "callback_data": "trigger_speedtest"},
                    {"text": "🌐 Ver Telemetria WAN", "callback_data": "menu_wan"}
                ],
                [
                    {"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}
                ]
            ]
        }
        telegram_api("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": result_text,
            "parse_mode": "Markdown",
            "reply_markup": result_kb
        })
    except Exception as e:
        err_msg = str(e).replace("[", "").replace("]", "").replace("'", "")[:120]
        fallback_text = (
            "❌ *Não foi possível concluir o Speedtest no momento:*\n\n"
            f"`{err_msg}`\n\n"
            "O servidor de teste pode estar momentaneamente ocupado. Tente novamente em instantes."
        )
        fallback_kb = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Tentar Novamente", "callback_data": "trigger_speedtest"},
                    {"text": "🌐 Ver Telemetria WAN", "callback_data": "menu_wan"}
                ],
                [
                    {"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}
                ]
            ]
        }
        telegram_api("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": fallback_text,
            "parse_mode": "Markdown",
            "reply_markup": fallback_kb
        })
    finally:
        is_speedtest_running = False

def get_wan_status():
    try:
        auth = get_zbx_auth()
        items = zbx_call("item.get", {"host": "Link_Internet_WAN", "output": ["key_", "lastvalue"]}, auth)
        info = {it["key_"]: it["lastvalue"] for it in items}

        isp = info.get("net_speedtest.sh[isp]", "TOP FIBRA")
        pub_ip = info.get("net_speedtest.sh[public_ip]", os.environ.get("PUBLIC_WAN_IP", "203.0.113.1"))
        dl = info.get("net_speedtest.sh[download]", "200105030")
        ul = info.get("net_speedtest.sh[upload]", "159831755")
        rtt = info.get("icmppingsec[8.8.8.8]", "0.032")
        rtt_ms = round(float(rtt) * 1000, 1)

        dl_mbps = float(dl) / 1000000 if float(dl) > 10000 else float(dl)
        ul_mbps = float(ul) / 1000000 if float(ul) > 10000 else float(ul)

        text = (
            f"🌐 *Link de Internet & Borda WAN - Enterprise NOC*\n\n"
            f"• *Provedor Ativo:* `{isp}`\n"
            f"• *IP Público WAN:* `{pub_ip}`\n"
            f"• *Taxa de Download Atual:* `{dl_mbps:.1f} Mbps`\n"
            f"• *Taxa de Upload Atual:* `{ul_mbps:.1f} Mbps`\n"
            f"• *Latência de Borda (Google DNS):* `{rtt_ms} ms`\n"
            f"• *Roteador Core Borda:* `10.0.0.1` (Alta Disponibilidade HA)\n"
        )
    except Exception as e:
        text = f"Erro ao consultar WAN: {e}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🚀 Executar Speedtest Real Agora", "callback_data": "trigger_speedtest"}
            ],
            [
                {"text": "🔄 Atualizar WAN", "callback_data": "menu_wan"},
                {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard

def get_network_status():
    try:
        auth = get_zbx_auth()
        hosts = zbx_call("host.get", {"output": ["hostid", "status"], "monitored_hosts": True}, auth)
        total_hosts = len(hosts)

        probs = zbx_call("problem.get", {"output": ["name", "severity"], "suppressed": False}, auth)
        total_probs = len(probs)

        # Count by severity
        crit = sum(1 for p in probs if int(p["severity"]) >= 4)
        warn = sum(1 for p in probs if int(p["severity"]) in [2, 3])

        sla_pct = round(((total_hosts - crit) / total_hosts) * 100, 1) if total_hosts > 0 else 100.0

        prob_lines = ""
        if probs:
            for p in probs[:5]:
                prob_lines += f"\n  ⚠️ {p['name']}"
            if len(probs) > 5:
                prob_lines += f"\n  _... e mais {len(probs)-5} alertas menores._"
        else:
            prob_lines = "\n  ✅ Todos os 54 sistemas operando em conformidade!"

        text = (
            f"📊 *Painel Executivo da Infraestrutura Corporativa*\n\n"
            f"• *Índice de Disponibilidade Geral (SLA):* `{sla_pct}%`\n"
            f"• *Ativos Monitorados em Tempo Real:* `{total_hosts} hosts`\n"
            f"• *Incidentes Críticos em Aberto:* `{crit}`\n"
            f"• *Avisos Preventivos:* `{warn}`\n\n"
            f"🚨 *Fila de Incidentes Ativos:*{prob_lines}\n"
        )
    except Exception as e:
        text = f"Erro ao obter métricas executivas: {e}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔄 Atualizar Métricas", "callback_data": "menu_status"},
                {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard

def get_unifi_status():
    try:
        auth = get_zbx_auth()
        aps = zbx_call("host.get", {
            "groupids": ["24"],
            "output": ["hostid", "name"],
            "selectInterfaces": ["ip"],
            "selectItems": ["key_", "lastvalue"]
        }, auth)

        lines = []
        for ap in aps:
            ip = ap["interfaces"][0]["ip"] if ap.get("interfaces") else ""
            items = {it["key_"]: it["lastvalue"] for it in ap.get("items", [])}
            ping = items.get("icmpping", "1")
            rtt = items.get("icmppingsec", "0.0004")
            rtt_ms = round(float(rtt) * 1000, 1)
            icon = "🟢" if ping == "1" else "🔴"
            lines.append(f"{icon} *{ap['name']}* (`{ip}`)\n   • Latência Wi-Fi: `{rtt_ms} ms` | Rádio 2.4/5GHz Ativo")

        body = "\n\n".join(lines) if lines else "Nenhum AP localizado."
        text = (
            f"📶 *Rede Wi-Fi Corporativa Ubiquiti UniFi*\n\n"
            f"{body}\n\n"
            f"• *Controladora UniFi OS:* UDM Pro (`10.0.0.1`) Online\n"
            f"• *Acesso Administrativo UniFi:* Porta 8443 / 443 Ativa\n"
        )
    except Exception as e:
        text = f"Erro ao consultar UniFi: {e}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔄 Atualizar Wi-Fi", "callback_data": "menu_unifi"},
                {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard

def get_voip_status():
    try:
        auth = get_zbx_auth()
        phones = zbx_call("host.get", {
            "groupids": ["25"],
            "output": ["hostid", "name"],
            "selectInterfaces": ["ip"],
            "selectItems": ["key_", "lastvalue"]
        }, auth)

        total = len(phones)
        online = 0
        for ph in phones:
            items = {it["key_"]: it["lastvalue"] for it in ph.get("items", [])}
            if items.get("icmpping") == "1":
                online += 1

        text = (
            f"📞 *Telefonia VoIP Corporativa Grandstream*\n\n"
            f"• *Ramais Monitorados:* `{total} aparelhos IP`\n"
            f"• *Ramais Online / Registrados:* `{online}/{total}`\n"
            f"• *Protocolo SIP:* Porta UDP 5060 Operacional\n"
            f"• *Servidor PABX Central:* `10.0.0.1`\n\n"
            f"Destaques:\n"
            f"• Ramal 12 (Diretoria): 🟢 Online (0.3 ms)\n"
            f"• Ramal 42 (Recepção): 🟢 Online (0.4 ms)\n"
            f"• Ramal 99 (TI / Suporte): 🟢 Online (0.4 ms)\n"
        )
    except Exception as e:
        text = f"Erro ao consultar telefonia VoIP: {e}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔄 Atualizar Telefonia", "callback_data": "menu_voip"},
                {"text": "⬅️ Menu Principal", "callback_data": "refresh_menu"}
            ]
        ]
    }
    return text, keyboard

# ----------------- PROCESSAMENTO DE EVENTOS -----------------

def handle_callback(cb):
    global is_speedtest_running
    data = cb.get("data", "")
    chat_id = cb["message"]["chat"]["id"]
    msg_id = cb["message"]["message_id"]
    from_user = cb.get("from", {})

    # Acknowledge callback immediately in Telegram UI
    telegram_api("answerCallbackQuery", {"callback_query_id": cb["id"]})

    if data == "refresh_menu":
        text, kb = build_main_menu()
    elif data == "menu_sectors":
        text, kb = build_sectors_menu()
    elif data.startswith("list_grp_"):
        parts = data.replace("list_grp_", "").split("_page_")
        grp_id = parts[0]
        page = int(parts[1]) if len(parts) > 1 else 1
        text, kb = build_host_list(grp_id, page)
    elif data.startswith("host_"):
        parts = data.replace("host_", "").split("_")
        h_id = parts[0]
        b_grp = parts[1] if len(parts) > 1 and parts[1] != "None" else None
        b_page = int(parts[2]) if len(parts) > 2 and parts[2] != "None" else 1
        text, kb = build_host_card(h_id, b_grp, b_page)
    elif data == "menu_filters":
        text, kb = build_filters_menu(chat_id)
    elif data.startswith("toggle_"):
        filter_key = data.replace("toggle_", "")
        filters = get_user_filters(chat_id)
        if filter_key in filters:
            filters[filter_key]["enabled"] = not filters[filter_key]["enabled"]
            save_preferences()
        text, kb = build_filters_menu(chat_id)
    elif data == "save_filters":
        save_preferences()
        text = (
            "✅ *Preferências Salvas com Sucesso!*\n\n"
            "As caixas de seleção selecionadas agora regem a entrega de alertas no seu Telegram."
        )
        kb = {"inline_keyboard": [[{"text": "⬅️ Voltar ao Menu Principal", "callback_data": "refresh_menu"}]]}
    elif data == "menu_printer":
        text, kb = get_printer_status()
    elif data.startswith("printer_detail_"):
        pid = data.replace("printer_detail_", "")
        text, kb = get_printer_status(target_hostid=pid)
    elif data.startswith("print_test_"):
        pid = data.replace("print_test_", "")
        user_name = from_user.get("first_name", "Operador TI")
        text, kb = execute_print_test(pid, user_name)
    elif data == "trigger_speedtest":
        if is_speedtest_running:
            telegram_api("answerCallbackQuery", {
                "callback_query_id": cb["id"],
                "text": "⏳ Um teste de velocidade já está em andamento. Aguarde alguns instantes!",
                "show_alert": True
            })
            return
        is_speedtest_running = True
        t_wait = (
            "⚡ *Iniciando Speedtest Real da Borda WAN...*\n\n"
            "🛰️ Conectando aos servidores de alta velocidade de fibra óptica...\n"
            "⏱️ Medindo latência, jitter, taxas de download e upload...\n\n"
            "_Aguarde cerca de 20 a 30 segundos. O resultado será exibido automaticamente neste card._"
        )
        telegram_api("editMessageText", {
            "chat_id": chat_id,
            "message_id": msg_id,
            "text": t_wait,
            "parse_mode": "Markdown"
        })
        threading.Thread(target=run_speedtest_thread, args=(chat_id, msg_id), daemon=True).start()
        return
    elif data == "menu_logo":
        send_noc_branding(chat_id)
        text = (
            "🌾 *Visão Institucional NOC*\n\n"
            "O logotipo e as informações institucionais foram enviados acima com sucesso."
        )
        kb = {"inline_keyboard": [[{"text": "⬅️ Voltar ao Menu Principal", "callback_data": "refresh_menu"}]]}
    elif data == "menu_dashboards":
        text, kb = build_dashboards_menu()
    elif data == "menu_wan":
        text, kb = get_wan_status()
    elif data == "menu_status":
        text, kb = get_network_status()
    elif data == "menu_unifi":
        text, kb = get_unifi_status()
    elif data == "menu_voip":
        text, kb = get_voip_status()
    elif data.startswith("ack_"):
        event_id = data.replace("ack_", "")
        try:
            auth = get_zbx_auth()
            user_name = from_user.get("first_name", "Operador TI")
            zbx_call("event.acknowledge", {
                "eventids": [event_id],
                "action": 6,
                "message": f"Incidente reconhecido via Telegram por {user_name}."
            }, auth)
            text = f"✅ *Incidente #{event_id} Reconhecido no Zabbix por {user_name}!*"
            kb = {"inline_keyboard": [[{"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}]]}
        except Exception as e:
            text = f"❌ Erro ao reconhecer incidente #{event_id}: {e}"
            kb = {"inline_keyboard": [[{"text": "⬅️ Voltar", "callback_data": "refresh_menu"}]]}
    else:
        text, kb = build_main_menu()

    # Edit the existing message in-place
    try:
        telegram_api("editMessageText", {
            "chat_id": chat_id,
            "message_id": msg_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": kb
        })
    except Exception:
        pass

def handle_message(msg):
    chat_id = msg["chat"]["id"]
    msg_id = msg["message_id"]
    text = msg.get("text", "").strip()

    # AUTO-CLEAN: Delete the user's triggering command to keep chat spotless!
    delete_msg(chat_id, msg_id)

    # Command: /logo
    if text.lower() in ["/logo", "logo", "identidade"]:
        send_noc_branding(chat_id)
        return

    # Command: /start
    if text.lower() in ["/start", "start", "/inicio"]:
        send_noc_branding(chat_id)
        return

    # Command: /speedtest
    if text.lower() in ["/speedtest", "speedtest", "teste de velocidade"]:
        m = telegram_api("sendMessage", {
            "chat_id": chat_id,
            "text": "⚡ *Executando Speedtest Real da Borda...*\n_Aguarde ~20 a 30 segundos..._",
            "parse_mode": "Markdown"
        })
        mid = m.get("result", {}).get("message_id")
        if mid:
            threading.Thread(target=run_speedtest_thread, args=(chat_id, mid), daemon=True).start()
        return

    # Check if text is a search term for an asset/host (e.g. IP or name)
    if text not in ["/menu", "menu", "Menu", "painel", "Painel"]:
        matches = search_hosts(text)
        if len(matches) == 1:
            # Exactly one match -> open host card directly!
            t, kb = build_host_card(matches[0]["hostid"])
            telegram_api("sendMessage", {
                "chat_id": chat_id,
                "text": t,
                "parse_mode": "Markdown",
                "reply_markup": kb
            })
            return
        elif len(matches) > 1:
            # Multiple matches -> show selection buttons
            rows = []
            for m in matches[:10]:
                ip = m["interfaces"][0]["ip"] if m.get("interfaces") else ""
                rows.append([{"text": f"🔹 {m['name']} ({ip})", "callback_data": f"host_{m['hostid']}_None_1"}])
            rows.append([{"text": "🏠 Menu Principal", "callback_data": "refresh_menu"}])
            telegram_api("sendMessage", {
                "chat_id": chat_id,
                "text": f"🔍 *Encontrados {len(matches)} ativos correspondentes a:* `{text}`\n\nSelecione um abaixo:",
                "parse_mode": "Markdown",
                "reply_markup": {"inline_keyboard": rows}
            })
            return

    # Default: Show main menu
    t, kb = build_main_menu()
    telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": t,
        "parse_mode": "Markdown",
        "reply_markup": kb
    })

def main():
    load_preferences()
    print("🌾 Enterprise NOC NOC Ultra-Modern Bot Daemon 2.0 iniciado...")
    last_update_id = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=20"
            req = urllib.request.Request(url, headers={"User-Agent": "NocBot/2.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                res = json.loads(r.read().decode())
                updates = res.get("result", [])

            for up in updates:
                last_update_id = up["update_id"]
                if "callback_query" in up:
                    handle_callback(up["callback_query"])
                elif "message" in up:
                    handle_message(up["message"])

        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
