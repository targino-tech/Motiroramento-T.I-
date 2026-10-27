#!/usr/bin/env python3
"""
Configurador Automatizado de Alertas Telegram - Enterprise NOC Master
Conecta seu Bot do Telegram ao Zabbix, valida a entrega de mensagens
e cadastra a mídia para recebimento em tempo real de incidentes de rede.
"""

import sys, os, json, urllib.request, argparse

ZABBIX_API_URL = "http://127.0.0.1/api_jsonrpc.php"
ALERTSCRIPT_PATH = "/home/infra/monitoring/zabbix/alertscripts/telegram_alert.py"

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
    req = urllib.request.Request(ZABBIX_API_URL, headers=headers, data=json.dumps(payload).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode())
        if "error" in res:
            raise Exception(res["error"])
        return res["result"]

def send_telegram_test(token, chat_id):
    print(f"\n[+] Enviando mensagem de teste para o Chat ID: {chat_id} via Telegram...")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🌐 *Enterprise NOC Master*\n\n✅ *Conexão Estabelecida com Sucesso!*\n\nEste canal está oficialmente integrado ao Zabbix 7.0.\nA partir de agora, você receberá aqui notificações críticas da rede, status de links WAN, APs UniFi, ramais VoIP e suprimentos de impressoras.",
        "parse_mode": "Markdown"
    }
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload).encode("utf-8"))
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok"):
                print(">>> Mensagem de teste entregue com SUCESSO no Telegram! <<<")
                return True
            else:
                print("Falha na API do Telegram:", data)
                return False
    except Exception as e:
        print(f"Erro ao contatar API do Telegram: {e}")
        return False

def configure_zabbix(token, chat_id):
    print("\n[+] Integrando Telegram nas configurações internas do Zabbix...")
    auth = zbx_call("user.login", {"username": "Admin", "password": "zabbix"})
    
    # 1. Atualizar MediaType nativo 97 (Telegram)
    mt = zbx_call("mediatype.get", {"mediatypeids": ["97"], "output": "extend"})[0]
    params = mt.get("parameters", [])
    updated_params = []
    for p in params:
        if p["name"] == "api_token":
            updated_params.append({"name": "api_token", "value": token})
        elif p["name"] == "api_parse_mode":
            updated_params.append({"name": "api_parse_mode", "value": "markdown"})
        else:
            updated_params.append(p)
            
    zbx_call("mediatype.update", {
        "mediatypeid": "97",
        "status": "0", # Enabled
        "parameters": updated_params
    }, auth)
    print("  -> Tipo de Mídia Telegram (ID: 97) atualizado com seu Token.")

    # 2. Associar mídia ao usuário Admin
    user = zbx_call("user.get", {"filter": {"username": "Admin"}, "selectMedias": "extend"}, auth)[0]
    medias = user.get("medias", [])
    # Remove existing telegram media if any
    medias = [m for m in medias if m.get("mediatypeid") != "97"]
    medias.append({
        "mediatypeid": "97",
        "sendto": [chat_id],
        "active": "0",
        "severity": "63", # All severities (Disaster, High, Average, Warning, Info)
        "period": "1-7,00:00-24:00"
    })
    zbx_call("user.update", {"userid": user["userid"], "medias": medias}, auth)
    print(f"  -> Mídia Telegram associada ao usuário Admin (Chat ID: {chat_id}).")

    # 3. Criar ou Atualizar Ação Global no Zabbix
    action_name = "Notificações Telegram - Enterprise NOC Master"
    existing_actions = zbx_call("action.get", {"filter": {"name": action_name}}, auth)
    if not existing_actions:
        zbx_call("action.create", {
            "name": action_name,
            "eventsource": 0, # Triggers
            "status": 0, # Enabled
            "operations": [
                {
                    "operationtype": 0, # Send message
                    "opmessage": {
                        "default_msg": 1,
                        "mediatypeid": "97"
                    },
                    "opmessage_usr": [{"userid": user["userid"]}]
                }
            ],
            "recovery_operations": [
                {
                    "operationtype": 11, # Notify all involved
                    "opmessage": {"default_msg": 1}
                }
            ]
        }, auth)
        print("  -> Ação Global de Notificação para Telegram criada com sucesso.")
    else:
        print("  -> Ação Global de Notificação para Telegram já estava ativa.")

def update_alertscript(token):
    if os.path.exists(ALERTSCRIPT_PATH):
        with open(ALERTSCRIPT_PATH, "r") as f:
            content = f.read()
        new_content = content.replace('BOT_TOKEN = "SEU_BOT_TOKEN_AQUI"', f'BOT_TOKEN = "{token}"')
        with open(ALERTSCRIPT_PATH, "w") as f:
            f.write(new_content)
        print(f"[+] Script auxiliar {ALERTSCRIPT_PATH} atualizado.")

def main():
    parser = argparse.ArgumentParser(description="Configurador de Telegram do Zabbix NOC")
    parser.add_argument("--token", help="Bot Token obtido no @BotFather")
    parser.add_argument("--chat-id", help="Chat ID obtido no @userinfobot")
    args = parser.parse_args()

    token = args.token
    chat_id = args.chat_id

    if not token or not chat_id:
        print("="*60)
        print("  Assistente de Configuração do Telegram - Enterprise NOC")
        print("="*60)
        print("1. Escaneie o QR Code do @BotFather para criar seu bot e obter o Token.")
        print("2. Escaneie o QR Code do @userinfobot para obter seu Chat ID.")
        print("="*60)
        token = input("Cole o Bot Token: ").strip()
        chat_id = input("Cole o Chat ID: ").strip()

    if not token or not chat_id:
        print("Token e Chat ID são obrigatórios!")
        sys.exit(1)

    success = send_telegram_test(token, chat_id)
    if success:
        configure_zabbix(token, chat_id)
        update_alertscript(token)
        print("\n🎉 Tudo pronto! Alertas do Telegram 100% configurados no Zabbix!")
    else:
        print("\n❌ Não foi possível verificar o token ou chat_id. Verifique se enviou /start para o bot antes de executar.")

if __name__ == "__main__":
    main()
