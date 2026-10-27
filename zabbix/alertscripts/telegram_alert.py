#!/usr/bin/env python3
"""
Script de envio de alertas Zabbix para Telegram
Uso: telegram_alert.py <CHAT_ID> <ASSUNTO> <MENSAGEM>
"""
import sys, os, json, urllib.request, re
# Token configurável via variável de ambiente para segurança no GitHub
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "SEU_BOT_TOKEN_AQUI")

if len(sys.argv) < 4:
    print("Uso: telegram_alert.py <CHAT_ID> <ASSUNTO> <MENSAGEM>")
    sys.exit(1)

chat_id = sys.argv[1]
subject = sys.argv[2]
message = sys.argv[3]

text = f"🚨 *{subject}*\n\n{message}"

if BOT_TOKEN == "SEU_BOT_TOKEN_AQUI":
    # Log de simulação caso o token ainda não tenha sido inserido
    print(f"[SIMULACAO TELEGRAM] Mensagem pronta para envio para {chat_id}:\n{text}")
    sys.exit(0)

# Check if an event ID is in the message for ACK button
import re
event_match = re.search(r'(?:Event ID|ID do Evento|#)[:\s]*(\d+)', message, re.IGNORECASE)
buttons = []
if event_match:
    event_id = event_match.group(1)
    buttons.append([{"text": "✅ Reconhecer Incidente (ACK)", "callback_data": f"ack_{event_id}"}])

buttons.append([
    {"text": "📊 Status da Rede", "callback_data": "menu_status"},
    {"text": "🖨️ Suprimentos HP", "callback_data": "menu_printer"}
])
buttons.append([
    {"text": "⚙️ Caixas de Seleção (Filtros)", "callback_data": "menu_filters"}
])

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": text,
    "parse_mode": "Markdown",
    "reply_markup": {"inline_keyboard": buttons}
}

req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload).encode("utf-8"))
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Telegram enviado com sucesso:", resp.read().decode())
except Exception as e:
    print("Erro ao enviar Telegram:", e)
    sys.exit(1)
