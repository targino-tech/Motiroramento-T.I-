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
            raise Exception(f"Zabbix API Error in {method}: {res['error']}")
        return res["result"]

def main():
    print("=== CONFIGURANDO TEMPLATES ZABBIX ===")
    zbx_user = os.environ.get("ZABBIX_USER", "Admin")
    zbx_pass = os.environ.get("ZABBIX_PASS", "zabbix")
    auth = zbx_call("user.login", {"username": zbx_user, "password": zbx_pass})
    print("Login OK. Auth token obtido.")

    # 1. TEMPLATE UNIFI WI-FI ENTERPRISE
    tpl_name = "Template Corporativo - Ubiquiti UniFi APs (Wi-Fi Enterprise)"
    tpls = zbx_call("template.get", {"filter": {"name": [tpl_name]}, "output": ["templateid", "name"]}, auth)
    if not tpls:
        # Create template
        res = zbx_call("template.create", {
            "host": tpl_name,
            "name": tpl_name,
            "groups": [{"groupid": "24"}] # Access Points UniFi & Wi-Fi
        }, auth)
        tpl_id = res["templateids"][0]
        print(f"Template criado: {tpl_name} (ID: {tpl_id})")
    else:
        tpl_id = tpls[0]["templateid"]
        print(f"Template existente: {tpl_name} (ID: {tpl_id})")

    # Get existing items on template
    existing_items = zbx_call("item.get", {"templateids": [tpl_id], "output": ["itemid", "key_", "name"]}, auth)
    existing_keys = {it["key_"]: it["itemid"] for it in existing_items}

    # Desired items on UniFi Template
    unifi_items = [
        {
            "name": "UniFi AP - Conectividade ICMP",
            "key_": "icmpping",
            "type": 3, # Simple check
            "value_type": 3, # Numeric unsigned
            "delay": "10s",
            "units": ""
        },
        {
            "name": "UniFi AP - Latência ICMP (RTT)",
            "key_": "icmppingsec",
            "type": 3, # Simple check
            "value_type": 0, # Numeric float
            "delay": "10s",
            "units": "ms",
            "preprocessing": [
                {"type": "1", "params": "1000", "error_handler": "0", "error_handler_params": ""}
            ]
        },
        {
            "name": "UniFi AP - Perda de Pacotes ICMP",
            "key_": "icmppingloss",
            "type": 3, # Simple check
            "value_type": 0, # Numeric float
            "delay": "10s",
            "units": "%"
        },
        {
            "name": "UniFi AP - Clientes Conectados",
            "key_": "unifi_telemetry.sh[{HOST.CONN},clients]",
            "type": 10, # External check
            "value_type": 3, # Numeric unsigned
            "delay": "10s",
            "units": ""
        },
        {
            "name": "UniFi AP - SSID Principal",
            "key_": "unifi_telemetry.sh[{HOST.CONN},ssid]",
            "type": 10, # External check
            "value_type": 4, # Text
            "delay": "30s",
            "units": ""
        },
        {
            "name": "UniFi AP - Velocidade Download (Throughput RX)",
            "key_": "unifi_telemetry.sh[{HOST.CONN},speed_rx]",
            "type": 10, # External check
            "value_type": 0, # Numeric float
            "delay": "10s",
            "units": "Bps"
        },
        {
            "name": "UniFi AP - Velocidade Upload (Throughput TX)",
            "key_": "unifi_telemetry.sh[{HOST.CONN},speed_tx]",
            "type": 10, # External check
            "value_type": 0, # Numeric float
            "delay": "10s",
            "units": "Bps"
        },
        {
            "name": "UniFi AP - Canal de Frequência e Rádio",
            "key_": "unifi_telemetry.sh[{HOST.CONN},channel]",
            "type": 10, # External check
            "value_type": 4, # Text
            "delay": "30s",
            "units": ""
        },
        {
            "name": "UniFi AP - Status da Conexão / Rádio",
            "key_": "unifi_telemetry.sh[{HOST.CONN},status]",
            "type": 10, # External check
            "value_type": 4, # Text
            "delay": "15s",
            "units": ""
        },
        {
            "name": "UniFi AP - Porta Gerenciamento SSH 22",
            "key_": "net.tcp.service[tcp,,22]",
            "type": 3,
            "value_type": 3,
            "delay": "30s",
            "units": ""
        },
        {
            "name": "UniFi AP - Porta Web Portal / Adote 8080",
            "key_": "net.tcp.service[tcp,,8080]",
            "type": 3,
            "value_type": 3,
            "delay": "30s",
            "units": ""
        },
        {
            "name": "UniFi AP - Porta Web HTTPS 8443",
            "key_": "net.tcp.service[tcp,,8443]",
            "type": 3,
            "value_type": 3,
            "delay": "30s",
            "units": ""
        }
    ]

    for item_data in unifi_items:
        key = item_data["key_"]
        payload = {
            "name": item_data["name"],
            "key_": key,
            "hostid": tpl_id,
            "type": item_data["type"],
            "value_type": item_data["value_type"],
            "delay": item_data["delay"],
            "units": item_data.get("units", "")
        }
        if "preprocessing" in item_data:
            payload["preprocessing"] = item_data["preprocessing"]

        if key in existing_keys:
            # Update item
            payload["itemid"] = existing_keys[key]
            del payload["hostid"]
            del payload["key_"]
            zbx_call("item.update", payload, auth)
            print(f"  [OK] Item atualizado no template: {item_data['name']}")
        else:
            # Create item
            zbx_call("item.create", payload, auth)
            print(f"  [OK] Item criado no template: {item_data['name']}")

    # Add Triggers to UniFi Template
    unifi_triggers = [
        {
            "description": "UniFi AP {HOST.NAME} está Inacessível (Sem resposta ICMP)",
            "expression": f"last(/{tpl_name}/icmpping)=0",
            "priority": 4 # High
        },
        {
            "description": "UniFi AP {HOST.NAME} com Alta Latência (> 80ms)",
            "expression": f"min(/{tpl_name}/icmppingsec,3m)>80",
            "priority": 2 # Warning
        },
        {
            "description": "UniFi AP {HOST.NAME} com Perda de Pacotes (> 5%)",
            "expression": f"min(/{tpl_name}/icmppingloss,3m)>5",
            "priority": 2 # Warning
        },
        {
            "description": "UniFi AP {HOST.NAME} com Saturação de Clientes (> 40 clientes)",
            "expression": f"last(/{tpl_name}/unifi_telemetry.sh[{{HOST.CONN}},clients])>40",
            "priority": 2 # Warning
        }
    ]

    existing_triggers = zbx_call("trigger.get", {"templateids": [tpl_id], "output": ["triggerid", "description"]}, auth)
    existing_trig_desc = {t["description"]: t["triggerid"] for t in existing_triggers}

    for trig in unifi_triggers:
        desc = trig["description"]
        if desc not in existing_trig_desc:
            try:
                zbx_call("trigger.create", trig, auth)
                print(f"  [OK] Trigger criada: {desc}")
            except Exception as e:
                print(f"  [AVISO] Erro ao criar trigger '{desc}': {e}")
        else:
            print(f"  [OK] Trigger já existente: {desc}")

    # Now handle AP hosts in Group 24:
    # Remove host-level duplicate items so they inherit cleanly from template 10879
    ap_hosts = zbx_call("host.get", {"groupids": ["24"], "output": ["hostid", "name"], "selectParentTemplates": ["templateid", "name"]}, auth)
    print(f"\nVinculando Template aos {len(ap_hosts)} Access Points...")
    for h in ap_hosts:
        hid = h["hostid"]
        hname = h["name"]
        linked_tpls = [t["templateid"] for t in h.get("parentTemplates", [])]

        # Delete any host-level standalone items (templateid == "0") that conflict with template keys
        host_items = zbx_call("item.get", {"hostids": [hid], "output": ["itemid", "key_", "templateid"]}, auth)
        host_keys_to_del = [it["itemid"] for it in host_items if it.get("templateid") in (0, "0", None) and it["key_"] in [x["key_"] for x in unifi_items]]
        if host_keys_to_del:
            zbx_call("item.delete", host_keys_to_del, auth)
            print(f"  [LIMPEZA] Removidos {len(host_keys_to_del)} itens standalone do host {hname}")

        if tpl_id not in linked_tpls:
            new_tpls = [{"templateid": tid} for tid in linked_tpls] + [{"templateid": tpl_id}]
            zbx_call("host.update", {"hostid": hid, "templates": new_tpls}, auth)
            print(f"  [VINCULADO] Template {tpl_name} vinculado com sucesso a {hname}")
        else:
            print(f"  [OK] Template {tpl_name} já vinculado a {hname}")

    # 2. TEMPLATE WAN & TELECOM
    print("\n=== ATUALIZANDO TEMPLATE LINKS WAN & TELECOM ===")
    wan_tpl_name = "Template Corporativo - Links de WAN, Internet & Provedores"
    wan_tpls = zbx_call("template.get", {"filter": {"name": [wan_tpl_name]}, "output": ["templateid", "name"]}, auth)
    if wan_tpls:
        wan_tpl_id = wan_tpls[0]["templateid"]
        existing_wan_items = zbx_call("item.get", {"templateids": [wan_tpl_id], "output": ["itemid", "key_", "name"]}, auth)
        existing_wan_keys = {it["key_"]: it["itemid"] for it in existing_wan_items}

        wan_items = [
            {
                "name": "WAN Link - Perda de Pacotes Secundária (1.1.1.1)",
                "key_": "icmppingloss[1.1.1.1]",
                "type": 3,
                "value_type": 0,
                "delay": "10s",
                "units": "%"
            }
        ]
        for it_data in wan_items:
            key = it_data["key_"]
            if key not in existing_wan_keys:
                payload = {
                    "name": it_data["name"],
                    "key_": key,
                    "hostid": wan_tpl_id,
                    "type": it_data["type"],
                    "value_type": it_data["value_type"],
                    "delay": it_data["delay"],
                    "units": it_data.get("units", "")
                }
                # Check if host has this item standalone, remove before adding to template
                wan_hosts = zbx_call("host.get", {"groupids": ["28"], "output": ["hostid", "name"]}, auth)
                for wh in wan_hosts:
                    wh_items = zbx_call("item.get", {"hostids": [wh["hostid"]], "filter": {"key_": [key]}, "output": ["itemid", "templateid"]}, auth)
                    standalone = [x["itemid"] for x in wh_items if x.get("templateid") in (0, "0", None)]
                    if standalone:
                        zbx_call("item.delete", standalone, auth)
                        print(f"  [LIMPEZA] Removido item standalone '{key}' do host {wh['name']}")

                zbx_call("item.create", payload, auth)
                print(f"  [OK] Item '{it_data['name']}' adicionado ao template WAN")

        # Triggers for WAN
        wan_triggers = [
            {
                "description": "Link WAN - Perda de Pacotes Primária Elevada (> 2%)",
                "expression": f"min(/{wan_tpl_name}/icmppingloss[8.8.8.8],3m)>2",
                "priority": 3
            },
            {
                "description": "Link WAN - Perda de Pacotes Secundária Elevada (> 2%)",
                "expression": f"min(/{wan_tpl_name}/icmppingloss[1.1.1.1],3m)>2",
                "priority": 3
            },
            {
                "description": "Link WAN - Alta Latência Primária (> 60ms)",
                "expression": f"min(/{wan_tpl_name}/icmppingsec[8.8.8.8],3m)>60",
                "priority": 2
            },
            {
                "description": "Link WAN - Queda Total da Conectividade Externa (Disaster)",
                "expression": f"last(/{wan_tpl_name}/icmpping[8.8.8.8])=0 and last(/{wan_tpl_name}/icmpping[1.1.1.1])=0",
                "priority": 5
            }
        ]
        existing_wan_trig = zbx_call("trigger.get", {"templateids": [wan_tpl_id], "output": ["triggerid", "description"]}, auth)
        existing_wan_desc = {t["description"]: t["triggerid"] for t in existing_wan_trig}
        for trig in wan_triggers:
            if trig["description"] not in existing_wan_desc:
                try:
                    zbx_call("trigger.create", trig, auth)
                    print(f"  [OK] Trigger criada no WAN: {trig['description']}")
                except Exception as e:
                    print(f"  [AVISO] Erro trigger WAN: {e}")

    # 3. VERIFY NOC SERVER AGENT METRICS
    print("\n=== VERIFICANDO SRV-NOC-MONITORING (Zabbix/Grafana) ===")
    noc_hosts = zbx_call("host.get", {"filter": {"host": ["SRV-NOC-Monitoring (Zabbix/Grafana)"]}, "output": ["hostid", "name"], "selectParentTemplates": ["templateid", "name"]}, auth)
    if noc_hosts:
        noc_h = noc_hosts[0]
        linked = [t["name"] for t in noc_h.get("parentTemplates", [])]
        print(f"SRV-NOC Templates atuais: {linked}")
        # Link 'Linux by Zabbix agent' if not linked
        agent_tpl = zbx_call("template.get", {"filter": {"name": ["Linux by Zabbix agent"]}, "output": ["templateid", "name"]}, auth)
        if agent_tpl and "Linux by Zabbix agent" not in linked:
            cur_ids = [{"templateid": t["templateid"]} for t in noc_h.get("parentTemplates", [])]
            cur_ids.append({"templateid": agent_tpl[0]["templateid"]})
            try:
                zbx_call("host.update", {"hostid": noc_h["hostid"], "templates": cur_ids}, auth)
                print("  [OK] Template 'Linux by Zabbix agent' vinculado com sucesso ao SRV-NOC!")
            except Exception as e:
                print(f"  [AVISO] Não foi possível vincular Linux by Zabbix agent: {e}")

    print("\n[CONCLUÍDO] Todos os templates corporativos do Zabbix foram atualizados e sincronizados!")

if __name__ == "__main__":
    main()
